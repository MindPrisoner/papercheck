import json
from datetime import datetime

from app.db.database import SessionLocal
from app.db.models import Document, Submission
from app.services.parser_service import parse_document


def run_parse_task(public_id: str):
    db = SessionLocal()

    try:
        submission = (
            db.query(Submission)
            .filter(Submission.public_id == public_id)
            .first()
        )

        if not submission:
            return

        submission.status = "parsing"
        submission.error_message = None
        db.commit()

        parsed = parse_document(submission.stored_path, submission.public_id)

        submission.paper_title = parsed["title"] or submission.paper_title
        submission.status = "parsed"
        submission.finished_at = datetime.utcnow()

        document = Document(
            submission_id=submission.id,
            title=parsed["title"],
            abstract_text=parsed["abstract_text"],
            keywords_json=json.dumps(parsed["keywords"], ensure_ascii=False),
            sections_json=json.dumps(parsed["sections"], ensure_ascii=False),
            references_json=json.dumps(parsed["references"], ensure_ascii=False),
            raw_text_path=parsed["raw_text_path"],
            word_count=parsed["word_count"],
            section_count=parsed["section_count"],
            reference_count=parsed["reference_count"],
        )

        db.add(document)
        db.commit()

    except Exception as e:
        submission = (
            db.query(Submission)
            .filter(Submission.public_id == public_id)
            .first()
        )
        if submission:
            submission.status = "failed"
            submission.error_message = str(e)
            db.commit()
    finally:
        db.close()