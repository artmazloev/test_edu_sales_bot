from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import SCENARIOS


def mode_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎯 Тренировка", callback_data="mode:training"),
            InlineKeyboardButton("📚 Коучинг", callback_data="mode:coaching"),
        ]
    ])


def scenario_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(data["name"], callback_data=f"scenario:{key}")]
        for key, data in SCENARIOS.items()
    ]
    return InlineKeyboardMarkup(buttons)


def feedback_nudge_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Получить обратную связь", callback_data="mode:coaching")]
    ])
