from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.connection import Base, SessionLocal, engine
from app.database import models  # noqa: F401 - register all models before create_all
from app.database.compat_migrations import migrate_legacy_sqlite_schema
from app.routers import auth, barriers, caregivers, dashboard, documents, journey, notifications, patients, reports, tasks
from app.services.demo_seed import seed_demo


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.demo_mode and len(settings.secret_key) < 32:
        raise RuntimeError("Set a random SECRET_KEY of at least 32 characters when DEMO_MODE is disabled.")
    Base.metadata.create_all(bind=engine)
    migrate_legacy_sqlite_schema(engine)
    if settings.demo_mode:
        db = SessionLocal()
        try:
            seed_demo(db)
        finally:
            db.close()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", description="Post-discharge journey coordination API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True,
                   allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"], allow_headers=["Authorization", "Content-Type"])

for router in (auth.router, patients.router, dashboard.router, documents.router, journey.router, tasks.router,
               caregivers.router, reports.router, notifications.router, barriers.router):
    app.include_router(router)


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "message": "CareBridge AI API is running.",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "CareBridge AI API", "demo_mode": settings.demo_mode}
