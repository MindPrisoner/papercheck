import json
from datetime import datetime

from app.db.database import SessionLocal
from app.db.models import Document, Submission
from app.services.parser_service import blocks_to_raw_text, load_blocks, normalize_text
from app.services.semantic_parser import build_semantic_parse_payload


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

        # 第一步：本地提取原始文本
        blocks = load_blocks(submission.stored_path)
        raw_text = blocks_to_raw_text(blocks)
        raw_text = normalize_text(raw_text)

        if not raw_text.strip():
            raise ValueError("未从文件中提取到有效文本内容")

        # 第二步：调用 LLM 做语义结构化解析
        parsed = build_semantic_parse_payload(
            file_path=submission.stored_path,
            public_id=submission.public_id,
            raw_text=raw_text,
        )

        submission.paper_title = parsed["title"] or submission.paper_title
        submission.status = "parsed"
        submission.finished_at = datetime.utcnow()

        # 避免重复插入 document
        old_document = submission.document
        if old_document:
            db.delete(old_document)
            db.commit()

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