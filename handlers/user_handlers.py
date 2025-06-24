import logging
from functools import wraps
import tempfile
from aiogram import types, F
from aiogram.filters import Command
from config import config
from utils.keyboards import start_keyboard
from services.bot_stat import BotStat
from services.ai_service import analyze_food_image
from services.redis_service import redis_service
from services.imgur_upload import upload_image_to_imgur

bot_stat = BotStat()
CHANNEL_ID = config.channel_id
CHANNEL_NAME = config.channel_name

logger = logging.getLogger("food_bot.user")


def is_subscribed(member_status: str) -> bool:
    return member_status in ("member", "creator", "administrator")


async def check_subscription(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return is_subscribed(member.status)
    except Exception:
        return False


def require_subscription(handler):
    @wraps(handler)
    async def wrapper(msg: types.Message, bot, *args, **kwargs):
        user_id = msg.from_user.id
        if not await check_subscription(bot, user_id):
            # Получаем название канала
            try:
                chat = await bot.get_chat(CHANNEL_ID)
                channel_title = chat.title
            except Exception:
                channel_title = CHANNEL_NAME
            await msg.answer(
                f"Для использования бота подпишитесь на канал: <a href='https://t.me/{CHANNEL_NAME}'>{channel_title}</a>\nПосле подписки нажмите <b>Старт</b> ещё раз.",
                parse_mode="HTML",
                reply_markup=start_keyboard(),
            )
            return
        return await handler(msg, bot, *args, **kwargs)

    return wrapper


@require_subscription
async def on_start(msg: types.Message, bot):
    try:
        user_id = msg.from_user.id
        await redis_service.add_subscribed_user(user_id)
        user_name = msg.from_user.first_name
        greeting = f"Привет, <b>{user_name}</b>! Присылай фото блюда и я напишу тебе его вес и БЖУ!"
        await msg.answer(greeting, parse_mode="HTML", reply_markup=None)
    except Exception as e:
        logger.exception("Ошибка в on_start: %s", e)
        await msg.answer("Произошла ошибка. Попробуйте позже.", parse_mode="HTML")


@require_subscription
async def on_photo(msg: types.Message, bot):
    try:
        await bot_stat.incr_photo()
        user_id = msg.from_user.id
        if not msg.photo or len(msg.photo) == 0:
            await msg.answer("Пожалуйста, пришлите фото блюда.")
            return
        await process_photo(msg.photo[-1], bot, user_id)
    except Exception as e:
        logger.exception("Ошибка в on_photo: %s", e)
        await msg.answer("Произошла ошибка при обработке фото. Попробуйте позже.")


async def process_photo(photo: types.PhotoSize, bot, user_id: int):
    try:
        # Оповещение пользователя, что обработка началась
        progress_msg = await bot.send_message(
            user_id, "✅ Фото получено! <i>Генерируем ответ...</i>", parse_mode="HTML"
        )
        # Анимация "бот печатает"
        await bot.send_chat_action(user_id, "typing")
        file = await bot.get_file(photo.file_id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as temp:
            await bot.download(file, destination=temp)
            temp.seek(0)
            file_bytes = temp.read()
            img_url = await upload_image_to_imgur(file_bytes)
            answer = await analyze_food_image(img_url)
        await bot_stat.add_response_chars(len(answer))
        # Заменяем сообщение ожидания на итоговый ответ
        await bot.edit_message_text(
            answer,
            chat_id=user_id,
            message_id=progress_msg.message_id,
            parse_mode="HTML",
        )
    except Exception as e:
        logger.exception("Ошибка в process_photo: %s", e)
        await bot.send_message(
            user_id,
            "Ошибка при анализе изображения. Попробуйте позже.",
            parse_mode="HTML",
        )


@require_subscription
async def on_other_message(msg: types.Message, bot):
    await msg.answer("Пожалуйста, пришлите фото блюда.")


def register_user_handlers(dp):
    dp.message.register(on_start, Command("start"))
    dp.message.register(on_start, lambda m: m.text == "Старт")
    dp.message.register(on_photo, F.photo)
    dp.message.register(
        on_other_message
    )  # универсальный хендлер на все остальные типы сообщений
