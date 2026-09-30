from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.knowledge import router as knowledge_router
from app.api.tickets import router as tickets_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(health_router)
app.include_router(tickets_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")
