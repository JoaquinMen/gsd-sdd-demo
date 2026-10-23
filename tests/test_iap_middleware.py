import time
import pytest
import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.testclient import TestClient

from src.agent.config import AppConfig
from src.agent.middleware.iap import IAPAuthMiddleware

@pytest.fixture
def ec_key_pair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem_private, pem_public

@pytest.fixture
def base_config():
    return AppConfig(
        project_id="test-cimbal-project",
        location="us-central1",
        use_vertexai=True,
        gemini_model="gemini-3.5-flash",
        bq_dataset_id="test_dataset",
        bq_table_id="test_table",
        gcs_docs_bucket="test-bucket",
        vertex_search_location="global",
        vertex_search_datastore_id="test-ds",
        iap_enabled=True,
        iap_bypass_dev=False,
        iap_audience="/projects/123/locations/us-central1/services/cimbal-service",
        port=8080
    )

def create_test_app(config: AppConfig, public_key_pem: bytes | None = None):
    app = FastAPI()
    
    # Custom key getter for test client using known public key
    key_getter = (lambda token: public_key_pem) if public_key_pem else None
    app.add_middleware(IAPAuthMiddleware, config=config, key_getter=key_getter)

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    @app.get("/api/user")
    async def get_user(request: Request):
        return {"user": request.state.user}

    return app

def test_iap_middleware_valid_jwt(base_config, ec_key_pair):
    pem_private, pem_public = ec_key_pair
    now = int(time.time())
    payload = {
        "iss": "https://cloud.google.com/iap",
        "aud": base_config.iap_audience,
        "sub": "accounts.google.com:10987654321",
        "email": "field.tech@cimbal.com",
        "exp": now + 3600,
        "iat": now,
    }
    token = jwt.encode(payload, pem_private, algorithm="ES256", headers={"kid": "key-1"})
    
    app = create_test_app(base_config, public_key_pem=pem_public)
    client = TestClient(app)

    response = client.get("/api/user", headers={"X-Goog-IAP-JWT-Assertion": token})
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "field.tech@cimbal.com"
    assert data["user"]["sub"] == "accounts.google.com:10987654321"

def test_iap_middleware_expired_jwt(base_config, ec_key_pair):
    pem_private, pem_public = ec_key_pair
    now = int(time.time())
    payload = {
        "iss": "https://cloud.google.com/iap",
        "aud": base_config.iap_audience,
        "sub": "accounts.google.com:10987654321",
        "email": "field.tech@cimbal.com",
        "exp": now - 3600,  # Expired
        "iat": now - 7200,
    }
    token = jwt.encode(payload, pem_private, algorithm="ES256", headers={"kid": "key-1"})
    
    app = create_test_app(base_config, public_key_pem=pem_public)
    client = TestClient(app)

    response = client.get("/api/user", headers={"X-Goog-IAP-JWT-Assertion": token})
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()

def test_iap_middleware_invalid_audience(base_config, ec_key_pair):
    pem_private, pem_public = ec_key_pair
    now = int(time.time())
    payload = {
        "iss": "https://cloud.google.com/iap",
        "aud": "/projects/wrong-project/locations/us-central1/services/wrong-service",
        "sub": "accounts.google.com:10987654321",
        "email": "field.tech@cimbal.com",
        "exp": now + 3600,
        "iat": now,
    }
    token = jwt.encode(payload, pem_private, algorithm="ES256", headers={"kid": "key-1"})
    
    app = create_test_app(base_config, public_key_pem=pem_public)
    client = TestClient(app)

    response = client.get("/api/user", headers={"X-Goog-IAP-JWT-Assertion": token})
    assert response.status_code == 401
    assert "audience" in response.json()["detail"].lower()

def test_iap_middleware_missing_header_production(base_config):
    app = create_test_app(base_config)
    client = TestClient(app)

    response = client.get("/api/user")
    assert response.status_code == 401
    assert "missing" in response.json()["detail"].lower()

def test_iap_middleware_bypass_dev():
    dev_config = AppConfig(
        project_id="test-cimbal-project",
        location="us-central1",
        use_vertexai=True,
        gemini_model="gemini-3.5-flash",
        bq_dataset_id="test_dataset",
        bq_table_id="test_table",
        gcs_docs_bucket="test-bucket",
        vertex_search_location="global",
        vertex_search_datastore_id="test-ds",
        iap_enabled=True,
        iap_bypass_dev=True,  # Dev bypass enabled
        iap_audience=None,
        port=8080
    )
    app = create_test_app(dev_config)
    client = TestClient(app)

    response = client.get("/api/user")
    assert response.status_code == 200
    user = response.json()["user"]
    assert user["email"] == "dev-engineer@cimbal.com"

def test_iap_middleware_healthz_exempt(base_config):
    app = create_test_app(base_config)
    client = TestClient(app)

    # /healthz should bypass IAP even with no headers
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
