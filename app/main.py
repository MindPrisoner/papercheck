from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import APP_DIR, APP_NAME, APP_VERSION
from app.db.database import Base, engine
from app.db import models  # 关键：必须先导入 models，create_all 才知道有哪些表
from app.routes.pages import router as pages_router
from app.routes.submit import router as submit_router
from app.routes.status import router as status_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
)

app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")

app.include_router(pages_router)
app.include_router(submit_router)
app.include_router(status_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}