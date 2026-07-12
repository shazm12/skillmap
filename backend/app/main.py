import asyncio
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import dev_settings as settings
from app.pipelines.roadmap.graph import build_roadmap_graph
from app.routes.roadmap_router import router as roadmap_router
from app.routes.voice_router import router as voice_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.roadmap_graph = build_roadmap_graph()

    agent_proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "app.pipelines.voice_agent.agent",
        "dev",
    )
    app.state.agent_process = agent_proc

    yield

    agent_proc.terminate()
    await agent_proc.wait()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(roadmap_router, prefix="/api")
app.include_router(voice_router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}
