import logging
from functools import wraps
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import config
from services.bot_stat import BotStat
from services.redis_service import redis_service
from services.ai_service import update_cached_prompt
from services.ai_service import get_default_prompt

ADMIN_USER_ID = int(config.admin_user_id)
bot_stat = BotStat()

logger = logging.getLogger("food_bot.admin")


class PromptStates(StatesGroup):
    waiting_for_prompt = State()


def is_admin(msg: types.Message) -> bool:
    return msg.from_user.id == ADMIN_USER_ID


# Декоратор для проверки прав администратора
def admin_only(handler):
    @wraps(handler)
    async def wrapper(msg, *args, **kwargs):
        if not is_admin(msg):
            await msg.answer("Нет доступа.")
            return
        return await handler(msg, *args, **kwargs)

    return wrapper


@admin_only
async def on_admin_stats(msg: types.Message, bot):
    try:
        await bot_stat.send_stats(bot, msg.chat.id)
    except Exception as e:
        logger.exception("Ошибка в on_admin_stats: %s", e)
        await msg.answer("Произошла ошибка при получении статистики.")


@admin_only
async def on_get_prompt(msg: types.Message, bot):
    try:
        default_prompt = await get_default_prompt()
        prompt = await redis_service.get_prompt(default_prompt)
        await msg.answer(f"Текущий промпт:\n\n{prompt}")
    except Exception as e:
        logger.exception("Ошибка в on_get_prompt: %s", e)
        await msg.answer("Произошла ошибка при получении промпта.")


@admin_only
async def on_set_prompt(msg: types.Message, bot, state: FSMContext):
    try:
        await msg.answer(
            "Отправьте новый промпт одним сообщением. Он будет применён сразу после получения."
        )
        await state.set_state(PromptStates.waiting_for_prompt)
    except Exception as e:
        logger.exception("Ошибка в on_set_prompt: %s", e)
        await msg.answer("Произошла ошибка при подготовке смены промпта.")


@admin_only
async def on_new_prompt(msg: types.Message, bot, state: FSMContext):
    try:
        await redis_service.set_prompt(msg.text)
        await update_cached_prompt(msg.text)
        await msg.answer("Промпт успешно обновлён и применён ко всем новым запросам!")
        await state.clear()
    except Exception as e:
        logger.exception("Ошибка в on_new_prompt: %s", e)
        await msg.answer("Произошла ошибка при обновлении промпта.")


async def waiting_for_prompt_filter(msg, state):
    return await state.get_state() == PromptStates.waiting_for_prompt.state


def register_admin_handlers(dp):
    dp.message.register(on_admin_stats, Command("stats"))
    dp.message.register(on_get_prompt, Command("get_prompt"))
    dp.message.register(on_set_prompt, Command("set_prompt"))
    dp.message.register(on_new_prompt, waiting_for_prompt_filter)
