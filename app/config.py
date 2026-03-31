import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
REPORT_DIR = DATA_DIR / "reports"
PARSED_DIR = DATA_DIR / "parsed"

APP_NAME = "PaperCheck Lite"
APP_VERSION = "0.1.0"

DATABASE_URL = f"sqlite:///{BASE_DIR / 'papercheck.db'}"

MAX_FILE_SIZE_MB = 20
ALLOWED_EXTENSIONS = {".docx", ".pdf"}

load_dotenv(BASE_DIR / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
PARSED_DIR.mkdir(parents=True, exist_ok=True)