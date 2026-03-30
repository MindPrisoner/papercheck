from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
REPORT_DIR = DATA_DIR / "reports"

APP_NAME = "PaperCheck Lite"
APP_VERSION = "0.1.0"

DATABASE_URL = f"sqlite:///{BASE_DIR / 'papercheck.db'}"

MAX_FILE_SIZE_MB = 20
ALLOWED_EXTENSIONS = {".docx", ".pdf"}

# 确保目录存在
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)