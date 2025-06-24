import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import config
from handlers.admin_handlers import register_admin_handlers
from handlers.user_handlers import register_user_handlers

from logging.handlers import RotatingFileHandler

log_handlers = [
    RotatingFileHandler(
        "bot.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,  # 3 last logs
        encoding="utf-8",
    ),
    logging.StreamHandler(),
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=log_handlers,
)

logger = logging.getLogger("food_bot")


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(
        token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    register_admin_handlers(dp)
    register_user_handlers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started polling.")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(f"Critical error in polling: {e}")
    finally:
        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Fatal error in main: {e}")
