from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import APP_DIR, APP_NAME, APP_VERSION
from app.db.database import Base, engine
from app.routes.pages import router as pages_router

# 初始化数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
)

app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")

app.include_router(pages_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}