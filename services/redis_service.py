import redis.asyncio as redis
from config import config

REDIS_URL = config.redis_url
PROMPT_KEY = "foodbot:prompt"
STAT_KEY = "foodbot:stats"

USER_SET_KEY = "foodbot:users:subscribed"


class RedisService:
    def __init__(self):
        self.client = redis.from_url(REDIS_URL, decode_responses=True)

    async def get_prompt(self, default_prompt: str) -> str:
        prompt = await self.client.get(PROMPT_KEY)
        if prompt is None:
            await self.client.set(PROMPT_KEY, default_prompt)
            return default_prompt
        return prompt

    async def set_prompt(self, new_prompt: str):
        await self.client.set(PROMPT_KEY, new_prompt)

    async def incr_stat(self, field: str, amount: int = 1):
        await self.client.hincrby(STAT_KEY, field, amount)

    async def set_stat(self, field: str, value: int):
        await self.client.hset(STAT_KEY, field, value)

    async def get_stats(self) -> dict:
        stats = await self.client.hgetall(STAT_KEY)
        return stats or {}

    async def add_subscribed_user(self, user_id: int):
        await self.client.sadd(USER_SET_KEY, user_id)

    async def get_subscribed_count(self) -> int:
        return await self.client.scard(USER_SET_KEY)

    async def close(self):
        await self.client.aclose()


redis_service = RedisService()
