import json
import re
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document as DocxDocument

from app.config import DATA_DIR

PARSED_DIR = DATA_DIR / "parsed"
PARSED_DIR.mkdir(parents=True, exist_ok=True)


def extract_text_from_docx(file_path: str) -> str:
    doc = DocxDocument(file_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text_from_pdf(file_path: str) -> str:
    texts = []
    pdf = fitz.open(file_path)
    for page in pdf:
        text = page.get_text("text")
        if text:
            texts.append(text.strip())
    return "\n".join(texts)


def load_raw_text(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    if suffix == ".docx":
        return extract_text_from_docx(file_path)
    elif suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {suffix}")


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_title(text: str) -> str | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None

    # 简单策略：取第一行非空内容作为标题
    first_line = lines[0]
    if len(first_line) > 60 and len(lines) > 1:
        return lines[1]
    return first_line


def extract_abstract(text: str) -> str | None:
    patterns = [
        r"摘要[:：]?\s*(.*?)\s*(关键词[:：]|关键字[:：]|Abstract|1\s|一、|第一章)",
        r"Abstract[:：]?\s*(.*?)\s*(Keywords[:：]|1\s|Introduction|一、|第一章)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.S | re.I)
        if match:
            abstract = match.group(1).strip()
            if abstract:
                return abstract[:3000]

    return None


def extract_keywords(text: str) -> list[str]:
    patterns = [
        r"关键词[:：]\s*(.*)",
        r"关键字[:：]\s*(.*)",
        r"Keywords[:：]\s*(.*)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            raw = match.group(1).strip()
            if raw:
                parts = re.split(r"[，,；;、\s]+", raw)
                return [p.strip() for p in parts if p.strip()][:8]

    return []


def split_sections(text: str) -> list[dict]:
    lines = text.splitlines()

    heading_patterns = [
        r"^(第[一二三四五六七八九十\d]+章\s*.*)$",
        r"^([一二三四五六七八九十]+、\s*.*)$",
        r"^(\d+\.\d+\s+.*)$",
        r"^(\d+\s+.*)$",
    ]

    sections = []
    current_heading = "正文开始"
    current_content = []

    def flush_section():
        nonlocal current_heading, current_content, sections
        content = "\n".join(current_content).strip()
        if content:
            sections.append(
                {
                    "heading": current_heading,
                    "level": 1,
                    "content": content[:8000],
                }
            )

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        is_heading = False
        for pattern in heading_patterns:
            if re.match(pattern, line):
                flush_section()
                current_heading = line
                current_content = []
                is_heading = True
                break

        if not is_heading:
            current_content.append(line)

    flush_section()
    return sections[:30]


def extract_references(text: str) -> list[str]:
    match = re.search(r"(参考文献|References)\s*(.*)", text, re.S | re.I)
    if not match:
        return []

    ref_block = match.group(2).strip()
    if not ref_block:
        return []

    lines = [line.strip() for line in ref_block.splitlines() if line.strip()]
    refs = []

    for line in lines:
        if len(line) < 4:
            continue
        refs.append(line)

    return refs[:100]


def save_raw_text(public_id: str, text: str) -> str:
    raw_text_path = PARSED_DIR / f"{public_id}.txt"
    raw_text_path.write_text(text, encoding="utf-8")
    return str(raw_text_path)


def parse_document(file_path: str, public_id: str) -> dict:
    raw_text = load_raw_text(file_path)
    raw_text = normalize_text(raw_text)

    title = extract_title(raw_text)
    abstract_text = extract_abstract(raw_text)
    keywords = extract_keywords(raw_text)
    sections = split_sections(raw_text)
    references = extract_references(raw_text)
    raw_text_path = save_raw_text(public_id, raw_text)

    word_count = len(re.sub(r"\s+", "", raw_text))
    section_count = len(sections)
    reference_count = len(references)

    return {
        "title": title,
        "abstract_text": abstract_text,
        "keywords": keywords,
        "sections": sections,
        "references": references,
        "raw_text_path": raw_text_path,
        "word_count": word_count,
        "section_count": section_count,
        "reference_count": reference_count,
        "raw_text_preview": raw_text[:1500],
    }