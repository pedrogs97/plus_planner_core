"""Global configs and constants"""

import os
from datetime import datetime

from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()
# PostgresSQL config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_HOST = os.getenv("POSTGRESQL_HOST", "localhost")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_database_url(test=False, sqlite=False):
    """Return database url"""
    if sqlite:
        return "sqlite://db.sqlite3"
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

ID_NOT_FOUND = "ID não encontrado"

ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1",
    "http://localhost",
    "https://localhost:5173",
    "https://127.0.0.1",
    "https://localhost",
]

PERMISSIONS = {
    "manager": {
        "models": [
            {"name": "permissions", "label": "Permissões"},
            {"name": "profiles", "label": "Perfil de usuário"},
            {"name": "users", "label": "Usuários"},
            {"name": "clinics", "label": "Clínicas"},
        ],
        "label": "Perfis e Permissões",
    },
    "clinic_office": {
        "models": [
            {"name": "specialties", "label": "Especialidades"},
            {"name": "patients", "label": "Pacientes"},
        ],
        "label": "Perfis e Permissões",
    },
}

SCHEDULER_API_KEY = os.getenv("SCHEDULER_API_KEY")
AUTH_API_URL = os.getenv("AUTH_API_URL")
AUTH_API_KEY = os.getenv("AUTH_API_KEY")
INVERTEXTO_TOKEN = os.getenv("INVERTEXTO_TOKEN")
