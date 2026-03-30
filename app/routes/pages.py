import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import APP_DIR
from app.db.database import get_db
from app.db.models import Submission

router = APIRouter()

templates = Jinja2Templates(directory=str(APP_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
def upload_page(request: Request):
    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "page_title": "论文体检官",
        },
    )


@router.get("/processing/{public_id}", response_class=HTMLResponse)
def processing_page(request: Request, public_id: str):
    return templates.TemplateResponse(
        "processing.html",
        {
            "request": request,
            "page_title": "处理中",
            "submission_id": public_id,
        },
    )


@router.get("/preview/{public_id}", response_class=HTMLResponse)
def preview_page(request: Request, public_id: str, db: Session = Depends(get_db)):
    submission = (
        db.query(Submission)
        .filter(Submission.public_id == public_id)
        .first()
    )

    if not submission:
        return templates.TemplateResponse(
            "preview.html",
            {
                "request": request,
                "page_title": "解析预览",
                "not_found": True,
            },
            status_code=404,
        )

    document = submission.document

    sections = json.loads(document.sections_json) if document and document.sections_json else []
    keywords = json.loads(document.keywords_json) if document and document.keywords_json else []
    references = json.loads(document.references_json) if document and document.references_json else []

    return templates.TemplateResponse(
        "preview.html",
        {
            "request": request,
            "page_title": "解析预览",
            "not_found": False,
            "submission": submission,
            "document": document,
            "sections": sections,
            "keywords": keywords,
            "references": references,
        },
    )