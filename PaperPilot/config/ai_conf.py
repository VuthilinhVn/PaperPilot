import os
from pathlib import Path
from dotenv import load_dotenv

# 明确指定 .env 文件路径（项目根目录）
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

AI_CHAT_CONFIG = {
    "api_endpoint": os.getenv("DEEPSEEK_API_ENDPOINT", "https://api.deepseek.com/v1/chat/completions"),
    "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
    "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    "stream": os.getenv("DEEPSEEK_STREAM", "True").lower() in ("true", "1"),
    "timeout": int(os.getenv("DEEPSEEK_TIMEOUT", "120")),
}