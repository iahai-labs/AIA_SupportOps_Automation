from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.health import router as health_router
from app.api.knowledge import router as knowledge_router
from app.api.tickets import router as tickets_router
from app.core.config import settings
from app.db.bootstrap import initialize_database
from app.ui.demo import router as demo_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(health_router)
app.include_router(tickets_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")
app.include_router(demo_router)
