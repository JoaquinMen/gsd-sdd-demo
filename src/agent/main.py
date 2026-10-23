"""Main FastAPI application entrypoint for Cimbal SA Operations Agent."""
import os
import json
import logging
from pathlib import Path
from typing import Any, Callable

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from google.genai import types
from google.adk.runners import InMemoryRunner

from src.agent.config import AppConfig
from src.agent.middleware.iap import IAPAuthMiddleware
from src.agent.agent import build_root_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cimbal.agent.app")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

class ChatPromptRequest(BaseModel):
    prompt: str
    session_id: str | None = None

def create_app(
    config: AppConfig | None = None,
    runner: Any | None = None,
    key_getter: Callable[[str], Any] | None = None,
) -> FastAPI:
    """Creates and configures the FastAPI application."""
    if config is None:
        config = AppConfig.from_env()

    app = FastAPI(
        title="Cimbal SA Secure Operations Assistant",
        description="Unified agricultural equipment operations agent with direct IAP security.",
        version="1.0.0",
    )

    # Mount static assets
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Setup Jinja2 templates
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

    # Add IAP Authentication Middleware
    app.add_middleware(
        IAPAuthMiddleware,
        config=config,
        key_getter=key_getter,
        exempt_paths={"/healthz", "/health"},
    )

    # Initialize agent runner if not injected
    if runner is None:
        agent = build_root_agent(config)
        runner = InMemoryRunner(agent=agent)

    @app.get("/healthz", tags=["Operations"])
    async def healthz():
        """Liveness & readiness health check endpoint."""
        return {
            "status": "ok",
            "project": config.project_id,
            "model": config.gemini_model,
            "service": "cimbal-secure-agent",
        }

    @app.get("/", response_class=HTMLResponse, tags=["Frontend"])
    async def index(request: Request):
        """Serves the custom Cimbal SA operations dashboard."""
        user = getattr(
            request.state,
            "user",
            {
                "email": "authenticated-specialist@cimbal.com",
                "role": "Certified Operations Specialist",
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "user": user,
                "project_id": config.project_id,
                "bq_table": config.bq_table_fqn,
                "search_ds": config.vertex_search_datastore_id,
            },
        )

    @app.post("/api/v1/chat/stream", tags=["Agent"])
    async def chat_stream(request: Request, body: ChatPromptRequest):
        """Streams agent responses via Server-Sent Events (SSE)."""
        user = getattr(request.state, "user", {})
        user_id = user.get("email") or user.get("sub") or "default-user"
        session_id = body.session_id or f"session-{user_id}"

        async def sse_event_stream():
            try:
                # Ensure session exists in the session service
                if hasattr(runner, "session_service"):
                    session = await runner.session_service.get_session(
                        app_name=getattr(runner, "app_name", None),
                        user_id=user_id,
                        session_id=session_id,
                    )
                    if not session:
                        await runner.session_service.create_session(
                            app_name=getattr(runner, "app_name", None),
                            user_id=user_id,
                            session_id=session_id,
                        )

                # Prepare new user message
                new_msg = types.Content(
                    role="user", parts=[types.Part.from_text(text=body.prompt)]
                )

                # Dispatch async execution to ADK runner
                async for event in runner.run_async(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=new_msg,
                ):
                    if hasattr(event, "message") and event.message and event.message.parts:
                        for part in event.message.parts:
                            if hasattr(part, "text") and part.text:
                                payload = json.dumps({"content": part.text})
                                yield f"data: {payload}\n\n"

                yield "data: [DONE]\n\n"

            except Exception as exc:
                logger.error("Error during streaming generation: %s", exc, exc_info=True)
                err_payload = json.dumps({"content": f"Operational error: {str(exc)}"})
                yield f"data: {err_payload}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(sse_event_stream(), media_type="text/event-stream")

    return app

# Default app instance for ASGI servers (e.g. uvicorn)
try:
    app = create_app()
except Exception as e:
    logger.debug("Deferred application initialization: %s", e)
    app = None

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    cfg = AppConfig.from_env()
    server_app = create_app(cfg)
    uvicorn.run(server_app, host="0.0.0.0", port=port)
