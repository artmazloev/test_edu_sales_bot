from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from config import SCENARIOS

BTN_FINISH = "🏁 Завершить и получить ОС"
BTN_SCENARIO = "🔄 Сменить сценарий"
BTN_RESET = "🔁 Начать сначала"


def main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Persistent bottom keyboard shown throughout the session."""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_FINISH), KeyboardButton(BTN_SCENARIO)],
            [KeyboardButton(BTN_RESET)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Скажите что-нибудь покупателю...",
    )


def mode_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔁 Переиграть сценарий", callback_data="mode:replay"),
            InlineKeyboardButton("🔄 Сменить сценарий", callback_data="show:scenarios"),
        ],
        [
            InlineKeyboardButton("🎯 Продолжить тренировку", callback_data="mode:training"),
        ],
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
        [InlineKeyboardButton("🔄 Сменить сценарий", callback_data="show:scenarios")]
    ])
