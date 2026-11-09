import os
from pathlib import Path


def _read_local_env():
    for candidate in (Path(".env"), Path("backend/.env"), Path(__file__).resolve().parents[2] / ".env"):
        if candidate.is_file():
            for line in candidate.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
            break


_read_local_env()


class Settings:
    def __init__(self):
        self.app_name = os.getenv("APP_NAME", "CareBridge")
        self.secret_key = os.getenv("SECRET_KEY", "local-development-key-change-before-deployment")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./carebridge.db")
        self.upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
        self.max_upload_mb = int(os.getenv("MAX_UPLOAD_MB", "10"))
        self.access_token_minutes = int(os.getenv("ACCESS_TOKEN_MINUTES", "720"))
        self.demo_mode = os.getenv("DEMO_MODE", "true").strip().lower() in {"true", "1", "yes"}
        self.ai_api_key = os.getenv("AI_API_KEY", "")
        self.ai_model = os.getenv("AI_MODEL", "gpt-4o-mini")
        self.ai_base_url = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
        self.cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")

    @property
    def allowed_origins(self) -> list[str]:
        origins = {origin.strip().rstrip("/") for origin in self.cors_origins.split(",") if origin.strip()}
        origins.update({
            "https://shivvar7087.github.io",
            "https://carebridge147.netlify.app",
        })
        if self.demo_mode:
            origins.update({
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:5174",
                "http://127.0.0.1:5174",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            })
        return sorted(origins)


settings = Settings()
