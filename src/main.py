"""Main Service"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

from src.config import (
    BASE_DIR,
    DATE_FORMAT,
    FORMAT,
    LOG_FILENAME,
    ORIGINS,
    STATIC_DIR,
    get_database_url,
)
from src.exceptions import default_response_exception

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


appAPI = FastAPI(
    exception_handlers=exception_handlers,
    version="1.0.0",
)

register_tortoise(
    appAPI,
    db_url=get_database_url(),
    modules={"models": ["src.clinic_office.models"]},
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
