"""Main Service"""

import logging
import os
from contextlib import asynccontextmanager
from logging.handlers import TimedRotatingFileHandler

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from plus_db_agent.manager import close, init
from tortoise import connections
from tortoise.exceptions import DBConnectionError

from src.backends import ClinicByHost
from src.config import (
    BASE_API,
    BASE_DIR,
    DATE_FORMAT,
    FORMAT,
    LOG_FILENAME,
    ORIGINS,
    STATIC_DIR,
)
from src.exceptions import default_response_exception
from src.manager.router import router as auth_router

if not os.path.exists(f"{BASE_DIR}/logs/"):
    os.makedirs(f"{BASE_DIR}/logs/")

file_handler = TimedRotatingFileHandler(LOG_FILENAME, when="midnight")
file_handler.suffix = "bkp"
logging.basicConfig(
    encoding="utf-8",
    level=logging.DEBUG,
    format=FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[file_handler],
)
logger = logging.getLogger(__name__)

exception_handlers = {
    500: default_response_exception,
    404: default_response_exception,
    401: default_response_exception,
    400: default_response_exception,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Context manager for the lifespan of the application."""
    logger.info("Service Version %s", app.version)
    await init()
    yield
    await close()


appAPI = FastAPI(
    exception_handlers=exception_handlers,
    version="1.0.0",
    lifespan=lifespan,
)

add_pagination(appAPI)
appAPI.include_router(
    auth_router, prefix=BASE_API, dependencies=[Depends(ClinicByHost())]
)

appAPI.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

appAPI.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@appAPI.get("/", tags=["Service"])
def root():
    """Redirect to docs"""
    return RedirectResponse(url="/docs")


@appAPI.get("/health", tags=["Service"])
async def health():
    """Health check"""
    try:
        await connections.get("default").execute_query("SELECT 1")
        return {"status": "ok"}
    except DBConnectionError:
        return {"status": "Database connection error"}
