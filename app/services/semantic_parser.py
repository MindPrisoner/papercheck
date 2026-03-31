import json
import re
from pathlib import Path

from app.config import OPENROUTER_MODEL, PARSED_DIR
from app.services.llm_client import client


def truncate_text(text: str, max_chars: int = 18000) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def save_raw_text(public_id: str, text: str) -> str:
    raw_text_path = PARSED_DIR / f"{public_id}.txt"
    raw_text_path.write_text(text, encoding="utf-8")
    return str(raw_text_path)


def build_semantic_parse_prompt(raw_text: str) -> str:
    return f"""
你是一名严谨的中文毕业论文结构解析助手。
你的任务不是改写论文，也不是评价论文质量，而是把论文原文解析成结构化 JSON。

请严格完成以下任务：
1. 识别论文标题
2. 识别摘要
3. 识别关键词（列表）
4. 识别正文章节（sections）
5. 识别参考文献（references）

要求：
- 只根据提供的文本抽取，不要编造不存在的内容
- 如果某项无法识别，返回 null 或空数组
- sections 中每个元素必须包含 heading、level、content
- level 是整数，一级标题填 1，二级标题填 2，三级标题填 3
- references 是字符串数组，每个元素是一条参考文献
- 只返回 JSON，不要输出任何解释文字

返回 JSON 格式如下：
{{
  "title": "论文标题或null",
  "abstract_text": "摘要内容或null",
  "keywords": ["关键词1", "关键词2"],
  "sections": [
    {{
      "heading": "章节标题",
      "level": 1,
      "content": "该章节正文内容"
    }}
  ],
  "references": ["参考文献1", "参考文献2"]
}}

下面是论文原文：
\"\"\"
{raw_text}
\"\"\"
""".strip()


def parse_document_with_llm(raw_text: str) -> dict:
    prompt = build_semantic_parse_prompt(raw_text)

    response = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=[
            {
                "role": "system",
                "content": "你是一个只输出合法 JSON 的论文结构解析器。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("LLM 未返回内容")

    data = json.loads(content)

    return normalize_llm_parse_result(data)


def normalize_llm_parse_result(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError("LLM 返回结果不是 JSON 对象")

    title = data.get("title")
    abstract_text = data.get("abstract_text")
    keywords = data.get("keywords") or []
    sections = data.get("sections") or []
    references = data.get("references") or []

    if title is not None and not isinstance(title, str):
        title = str(title)

    if abstract_text is not None and not isinstance(abstract_text, str):
        abstract_text = str(abstract_text)

    if not isinstance(keywords, list):
        keywords = []

    if not isinstance(sections, list):
        sections = []

    if not isinstance(references, list):
        references = []

    norm_keywords = []
    for kw in keywords:
        if kw is None:
            continue
        kw = str(kw).strip()
        if kw:
            norm_keywords.append(kw)

    norm_sections = []
    for sec in sections:
        if not isinstance(sec, dict):
            continue

        heading = str(sec.get("heading", "")).strip()
        content = str(sec.get("content", "")).strip()

        level = sec.get("level", 1)
        try:
            level = int(level)
        except Exception:
            level = 1

        if not heading and not content:
            continue

        norm_sections.append(
            {
                "heading": heading or "未命名章节",
                "level": max(1, min(level, 3)),
                "content": content[:8000],
            }
        )

    norm_references = []
    for ref in references:
        if ref is None:
            continue
        ref = str(ref).strip()
        if ref:
            norm_references.append(ref)

    return {
        "title": title.strip() if isinstance(title, str) and title.strip() else None,
        "abstract_text": abstract_text.strip() if isinstance(abstract_text, str) and abstract_text.strip() else None,
        "keywords": norm_keywords[:10],
        "sections": norm_sections[:40],
        "references": norm_references[:100],
    }


def build_semantic_parse_payload(file_path: str, public_id: str, raw_text: str) -> dict:
    raw_text = re.sub(r"\n{3,}", "\n\n", raw_text).strip()
    raw_text = truncate_text(raw_text)
    raw_text_path = save_raw_text(public_id, raw_text)

    parsed = parse_document_with_llm(raw_text)

    word_count = len(re.sub(r"\s+", "", raw_text))
    section_count = len(parsed["sections"])
    reference_count = len(parsed["references"])

    return {
        "title": parsed["title"],
        "abstract_text": parsed["abstract_text"],
        "keywords": parsed["keywords"],
        "sections": parsed["sections"],
        "references": parsed["references"],
        "raw_text_path": raw_text_path,
        "word_count": word_count,
        "section_count": section_count,
        "reference_count": reference_count,
        "raw_text_preview": raw_text[:1500],
    }