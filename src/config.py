"""Global configs and constants"""

import os
from datetime import datetime
from tortoise import Tortoise

from dotenv import load_dotenv

load_dotenv()
# PostgresSQL config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_HOST = os.getenv("POSTGRESQL_HOST", "localhost")


def get_database_url(test=False):
    """Return database url"""
    server = DB_HOST if not test else os.getenv("POSTGRESQL_HOST_TEST", "localhost")
    db = os.getenv("POSTGRESQL_DATABASE", "app") if not test else "db_test"
    user = (
        os.getenv("POSTGRESQL_USER", "root")
        if not test
        else os.getenv("POSTGRESQL_USER_TEST", "root")
    )
    password = (
        os.getenv("POSTGRESQL_PASSWORD", "")
        if not test
        else os.getenv("POSTGRESQL_PASSWORD_TEST", "")
    )
    port = os.getenv("POSTGRESQL_PORT", "5432")
    teste = f"postgres://{user}:{password}@{server}:{port}/{db}"
    return f"postgres://{user}:{password}@{server}:{port}/{db}"


PASSWORD_SUPER_USER = os.getenv("PASSWORD_SUPER_USER")

TIMEZONE = os.getenv("TIMEZONE", "America/Bahia")

DEBUG = os.getenv("DEBUG")

# Logging config.

FORMAT = (
    "[%(asctime)s][%(levelname)s] %(name)s "
    "%(filename)s:%(funcName)s:%(lineno)d | %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
date_str = datetime.now().strftime("%Y-%m-%d")
LOG_FILENAME = f"{BASE_DIR}/logs/{date_str}.log"

DEFAULT_DATE_FORMAT = "%d/%m/%Y"
DEFAULT_DATE_TIME_FORMAT = "%d/%m/%Y %H:%M:%S"

SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_HOURS = 8
REFRESH_TOKEN_EXPIRE_DAYS = 2
STORAGE_DIR = "storage" if DEBUG else "/storage"
MEDIA_UPLOAD_TEST_DIR = os.path.join(BASE_DIR, "media")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

BASE_API = "/api/v1"

NOT_ALLOWED = "Não permitido"

PAGE_NUMBER_DESCRIPTION = "Page number"

PAGE_SIZE_DESCRIPTION = "Page size"

PAGINATION_NUMBER = 15

MAX_PAGINATION_NUMBER = 100

ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1",
    "http://localhost",
    "https://localhost:3000",
    "https://127.0.0.1",
    "https://localhost",
]
