import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Submission

router = APIRouter()


@router.get("/status/{public_id}")
def get_submission_status(public_id: str, db: Session = Depends(get_db)):
    submission = (
        db.query(Submission)
        .filter(Submission.public_id == public_id)
        .first()
    )

    if not submission:
        raise HTTPException(status_code=404, detail="未找到该提交记录")

    document = submission.document

    return {
        "public_id": submission.public_id,
        "filename": submission.filename,
        "paper_title": submission.paper_title,
        "school_name": submission.school_name,
        "major_name": submission.major_name,
        "paper_type": submission.paper_type,
        "need_defense_pack": submission.need_defense_pack,
        "status": submission.status,
        "error_message": submission.error_message,
        "created_at": submission.created_at.isoformat() if submission.created_at else None,
        "finished_at": submission.finished_at.isoformat() if submission.finished_at else None,
        "document": {
            "title": document.title if document else None,
            "abstract_text": document.abstract_text[:300] if document and document.abstract_text else None,
            "keywords": json.loads(document.keywords_json) if document and document.keywords_json else [],
            "word_count": document.word_count if document else 0,
            "section_count": document.section_count if document else 0,
            "reference_count": document.reference_count if document else 0,
        },
    }