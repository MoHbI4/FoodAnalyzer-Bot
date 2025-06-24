import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv


BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    bot_token: str = os.getenv("BOT_TOKEN")
    channel_id: str = os.getenv("CHANNEL_ID")
    admin_user_id: str = os.getenv("ADMIN_USER_ID")
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    channel_name: str = os.getenv("CHANNEL_NAME")
    redis_url: str = os.getenv("REDIS_URL")


config = Settings()
