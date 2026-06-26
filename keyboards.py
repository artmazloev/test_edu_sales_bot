from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from config import SCENARIOS


def main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Persistent bottom keyboard shown throughout the session."""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📊 Обратная связь"), KeyboardButton("🔄 Сменить сценарий")],
            [KeyboardButton("🔁 Сбросить диалог")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Скажите что-нибудь покупателю...",
    )


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
