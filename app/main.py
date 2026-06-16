from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_fastapi_instrumentator import Instrumentator


from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.api.v1 import api_router
from app.middlewares.request_id import RequestIDMiddleware


settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    setup_logging()
    logger.info("starting", app=settings.APP_NAME, env=settings.APP_ENV)
    yield
    logger.info("shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan
    )

    # ── Middleware
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Prometheus metrics exposed at /metrics
    Instrumentator().instrument(app).expose(app)

    # Global exception handler 
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("unhandled_error", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

    # Health check
    @app.get("/health", tags=["System"])
    async def health():
        return {"status": "ok", "env": settings.APP_ENV}

    # Routes
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
