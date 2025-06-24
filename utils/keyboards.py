from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def start_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Старт")]], resize_keyboard=True
    )
