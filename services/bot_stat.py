from services.redis_service import redis_service


class BotStat:
    def __init__(self):
        pass

    async def incr_photo(self):
        await redis_service.incr_stat("photo_requests")

    async def add_response_chars(self, n: int):
        await redis_service.incr_stat("total_response_chars", n)

    async def get_user_count(self) -> int:
        return await redis_service.get_subscribed_count()

    async def get_stats(self) -> dict:
        stats = await redis_service.get_stats()
        user_count = await self.get_user_count()
        return {
            "photo_requests": int(stats.get("photo_requests", 0)),
            "total_response_chars": int(stats.get("total_response_chars", 0)),
            "user_count": user_count,
        }

    async def send_stats(self, bot, chat_id):
        stats = await self.get_stats()
        text = (
            f"Фото-запросов: {stats['photo_requests']}\n"
            f"Символов в ответах: {stats['total_response_chars']}\n"
            f"Пользователей с подпиской: {stats['user_count']}"
        )
        await bot.send_message(chat_id, text)
