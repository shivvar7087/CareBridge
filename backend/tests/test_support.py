import os
import sys
import tempfile
import uuid
from pathlib import Path

backend_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_root))
test_root = Path(tempfile.gettempdir()) / f"carebridge-test-{os.getpid()}"
test_root.mkdir(parents=True, exist_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{(test_root / 'test.db').as_posix()}"
os.environ["UPLOAD_DIR"] = str(test_root / "uploads")
os.environ["SECRET_KEY"] = "pytest-only-secret-key-with-at-least-32-bytes"
os.environ["DEMO_MODE"] = "false"
os.environ["AI_API_KEY"] = ""

from fastapi.testclient import TestClient  # noqa: E402
from app.database.connection import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


def create_account(client: TestClient, *, role="patient", email=None, invite_code=None):
    email = email or f"{uuid.uuid4().hex}@example.com"
    response = client.post("/api/auth/register", json={"full_name": "Sample User", "email": email,
                                                        "password": "valid-password-123", "role": role,
                                                        "invite_code": invite_code})
    if response.status_code != 201:
        raise AssertionError(response.text)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, response.json()["user"]
