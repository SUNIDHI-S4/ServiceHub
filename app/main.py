"""FastAPI application entry point for ServiceHub."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter

from app.config import settings
from app.database import engine, get_db
from app.graphql.context import get_context
from app.graphql.schema import schema

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    level=logging.DEBUG if settings.debug else logging.INFO,
)
logger = logging.getLogger("servicehub")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app-scoped resources (DB engine) across startup/shutdown."""
    logger.info("ServiceHub starting up")
    yield
    logger.info("ServiceHub shutting down; disposing DB engine")
    await engine.dispose()


app = FastAPI(title="ServiceHub API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=True,
)

graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    """Liveness probe — also verifies DB connectivity."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as exc:  # pragma: no cover — only in DB outage
        logger.exception("Health check failed")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": str(exc)},
        )
