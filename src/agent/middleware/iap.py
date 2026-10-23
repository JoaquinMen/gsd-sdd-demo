import logging
from typing import Callable, Any
import jwt
from jwt import PyJWKClient
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.agent.config import AppConfig

logger = logging.getLogger("cimbal.agent.middleware.iap")

IAP_JWKS_URL = "https://www.gstatic.com/iap/verify/public_key-jwk"
IAP_ISSUER = "https://cloud.google.com/iap"

class IAPAuthMiddleware(BaseHTTPMiddleware):
    """Identity-Aware Proxy (IAP) cryptographic JWT verification middleware.
    
    Validates X-Goog-IAP-JWT-Assertion header containing ES256 signed JWT
    from Google Cloud IAP, extracts employee identity, and injects into request.state.user.
    """

    def __init__(
        self,
        app,
        config: AppConfig,
        jwks_client: PyJWKClient | None = None,
        key_getter: Callable[[str], Any] | None = None,
        exempt_paths: set[str] | None = None,
    ):
        super().__init__(app)
        self.config = config
        self._key_getter = key_getter
        self._jwks_client = jwks_client or PyJWKClient(IAP_JWKS_URL, cache_keys=True)
        self.exempt_paths = exempt_paths or {"/healthz", "/health"}

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
        # Check path exemption (liveness and readiness probes)
        if request.url.path in self.exempt_paths or request.url.path.startswith("/static"):
            return await call_next(request)

        token = request.headers.get("x-goog-iap-jwt-assertion") or request.headers.get(
            "X-Goog-IAP-JWT-Assertion"
        )

        # Development bypass
        if self.config.iap_bypass_dev and not token:
            request.state.user = {
                "email": "dev-engineer@cimbal.com",
                "sub": "dev-user-001",
                "role": "Field Operations Specialist",
                "claims": {},
            }
            return await call_next(request)

        # Production / strict check: token must be present
        if not token:
            logger.warning("Request rejected: missing X-Goog-IAP-JWT-Assertion header")
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing IAP assertion header (X-Goog-IAP-JWT-Assertion)"},
            )

        # Cryptographic verification of ES256 JWT
        try:
            if self._key_getter:
                key = self._key_getter(token)
            else:
                signing_key = self._jwks_client.get_signing_key_from_jwt(token)
                key = signing_key.key

            options = {
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": bool(self.config.iap_audience),
            }

            payload = jwt.decode(
                token,
                key,
                algorithms=["ES256"],
                audience=self.config.iap_audience if self.config.iap_audience else None,
                issuer=IAP_ISSUER,
                options=options,
            )

            request.state.user = {
                "email": payload.get("email", "unknown@cimbal.com"),
                "sub": payload.get("sub", ""),
                "role": "Certified Operations Specialist",
                "claims": payload,
            }
            return await call_next(request)

        except jwt.ExpiredSignatureError:
            logger.warning("IAP token verification failed: token has expired")
            return JSONResponse(status_code=401, content={"detail": "IAP token has expired"})
        except jwt.InvalidAudienceError:
            logger.warning("IAP token verification failed: invalid audience")
            return JSONResponse(status_code=401, content={"detail": "Invalid IAP audience"})
        except jwt.InvalidIssuerError:
            logger.warning("IAP token verification failed: invalid issuer")
            return JSONResponse(status_code=401, content={"detail": "Invalid IAP issuer"})
        except Exception as exc:
            logger.warning("IAP token verification failed: %s", exc)
            return JSONResponse(
                status_code=401, content={"detail": f"Invalid IAP token: {str(exc)}"}
            )
