from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    public_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    filename: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(20))
    file_size: Mapped[int] = mapped_column(Integer)

    paper_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    school_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    major_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    paper_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    need_defense_pack: Mapped[bool] = mapped_column(Boolean, default=True)

    status: Mapped[str] = mapped_column(String(50), default="pending")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    document: Mapped["Document | None"] = relationship(
        "Document",
        back_populates="submission",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"), unique=True)

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    abstract_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    sections_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    references_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    raw_text_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    word_count: Mapped[int] = mapped_column(Integer, default=0)
    section_count: Mapped[int] = mapped_column(Integer, default=0)
    reference_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    submission: Mapped["Submission"] = relationship(
        "Submission",
        back_populates="document",
    )