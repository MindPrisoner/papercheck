import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, UPLOAD_DIR
from app.db.database import get_db
from app.db.models import Submission
from app.services.task_service import run_parse_task

router = APIRouter()


def generate_public_id() -> str:
    return f"pc_{uuid.uuid4().hex[:12]}"


@router.post("/submit")
async def submit_paper(
    background_tasks: BackgroundTasks,
    paper_file: UploadFile = File(...),
    school_name: str = Form(""),
    major_name: str = Form(""),
    paper_type: str = Form("本科毕业论文"),
    need_defense_pack: str | None = Form(None),
    db: Session = Depends(get_db),
):
    if not paper_file.filename:
        raise HTTPException(status_code=400, detail="未检测到文件名")

    suffix = Path(paper_file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"暂不支持该文件类型：{suffix}，请上传 docx 或 pdf",
        )

    content = await paper_file.read()
    file_size = len(content)

    if file_size == 0:
        raise HTTPException(status_code=400, detail="上传文件为空")

    max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，请上传不超过 {MAX_FILE_SIZE_MB}MB 的文件",
        )

    public_id = generate_public_id()
    stored_filename = f"{public_id}{suffix}"
    stored_path = UPLOAD_DIR / stored_filename

    with open(stored_path, "wb") as f:
        f.write(content)

    submission = Submission(
        public_id=public_id,
        filename=paper_file.filename,
        stored_path=str(stored_path),
        file_type=suffix.lstrip("."),
        file_size=file_size,
        paper_title=None,
        school_name=school_name.strip() or None,
        major_name=major_name.strip() or None,
        paper_type=paper_type.strip() or "本科毕业论文",
        need_defense_pack=bool(need_defense_pack),
        status="pending",
        error_message=None,
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    background_tasks.add_task(run_parse_task, public_id)

    return RedirectResponse(
        url=f"/processing/{public_id}",
        status_code=303,
    )