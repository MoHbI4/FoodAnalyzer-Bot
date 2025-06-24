import asyncio
from openai import OpenAI
from config import config
from services.redis_service import redis_service

# client = OpenAI(api_key=config.openai_api_key)
client = OpenAI(api_key=config.openai_api_key, base_url="https://api.kluster.ai/v1")

PROMPT_TXT_PATH = "prompt.txt"


async def get_default_prompt() -> str:
    try:
        with open(PROMPT_TXT_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return (
            "Посмотри на фото блюда и опиши его характеристики: вес блюда на фото, БЖУ."
        )


_prompt_cache = None


async def load_prompt():
    global _prompt_cache
    if _prompt_cache is not None:
        return _prompt_cache
    default_prompt = await get_default_prompt()
    prompt = await redis_service.get_prompt(default_prompt)
    _prompt_cache = prompt
    # Если в Redis не было промпта, мы его туда записали (логика в redis_service)
    return _prompt_cache


async def update_cached_prompt(new_prompt: str):
    global _prompt_cache
    _prompt_cache = new_prompt


async def analyze_food_image(img_url: str) -> str:
    """
    Использует кэшированный промпт для отправки запроса к OpenAI Vision через публичный URL.
    """
    prompt = await load_prompt()
    loop = asyncio.get_event_loop()

    def sync_call():
        completion = client.chat.completions.create(
            model="google/gemma-3-27b-it",
            max_tokens=4000,
            temperature=0.6,
            top_p=1,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": img_url}},
                    ],
                }
            ],
        )
        return completion.choices[0].message.content

    return await loop.run_in_executor(None, sync_call)
