from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import SCENARIOS


def mode_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎯 Продолжить тренировку", callback_data="mode:training"),
            InlineKeyboardButton("🔄 Сменить сценарий", callback_data="show:scenarios"),
        ]
    ])


def scenario_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(data["name"], callback_data=f"scenario:{key}")]
        for key, data in SCENARIOS.items()
    ]
    return InlineKeyboardMarkup(buttons)


def training_keyboard() -> InlineKeyboardMarkup:
    """Shown after every buyer reply during training."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Получить обратную связь", callback_data="mode:coaching"),
            InlineKeyboardButton("🔄 Сменить сценарий", callback_data="show:scenarios"),
        ]
    ])
