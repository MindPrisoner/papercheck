from openai import OpenAI

from app.config import OPENROUTER_API_KEY

if not OPENROUTER_API_KEY:
    raise RuntimeError("未检测到 OPENROUTER_API_KEY，请检查 .env 文件")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)