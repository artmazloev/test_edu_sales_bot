import logging
from telegram import Update, BotCommand
from telegram.ext import ContextTypes
from config import SCENARIOS
from state import manager as state_manager
from services.dialogue import get_coaching_feedback
from keyboards import mode_keyboard, scenario_keyboard, main_reply_keyboard

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state_manager.reset(user_id)
    logger.info("start | user_id=%d", user_id)
    await update.message.reply_text(
        "👋 Привет! Я бот для тренировки навыков продаж.\n\n"
        "🎯 Отправляйте голосовые или текстовые сообщения — я буду играть роль покупателя.\n"
        "🏁 Когда закончите — нажмите *«Завершить и получить ОС»* для разбора диалога.\n\n"
        "Выберите сценарий:",
        parse_mode="Markdown",
        reply_markup=main_reply_keyboard(),
    )
    await update.message.reply_text(
        "👇 Выберите сценарий:",
        reply_markup=scenario_keyboard(),
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state_manager.reset(user_id)
    logger.info("reset | user_id=%d", user_id)
    await update.message.reply_text(
        "🔁 Начинаем сначала. Выберите сценарий:",
        reply_markup=scenario_keyboard(),
    )


async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state = state_manager.get_or_create(user_id)
    logger.info("feedback | user_id=%d turns=%d", user_id, state.turn_count)
    await update.message.reply_text("⏳ Анализирую диалог...")
    fb = await get_coaching_feedback(state)
    state.mode = "coaching"
    await update.message.reply_text(fb, parse_mode="Markdown", reply_markup=mode_keyboard())


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    state = state_manager.get_or_create(user_id)
    data = query.data

    if data == "show:scenarios":
        await query.message.reply_text(
            "Выберите сценарий (текущий диалог будет сброшен):",
            reply_markup=scenario_keyboard(),
        )

    elif data.startswith("scenario:"):
        key = data.split(":", 1)[1]
        if key not in SCENARIOS:
            await query.message.reply_text("Неизвестный сценарий.")
            return
        state_manager.reset(user_id)
        state = state_manager.get_or_create(user_id)
        state.scenario_key = key
        scenario = SCENARIOS[key]
        logger.info("scenario | user_id=%d key=%s", user_id, key)
        await query.message.reply_text(
            f"✅ Сценарий: *{scenario['name']}*\n"
            f"Покупатель: _{scenario['buyer_role']}_\n\n"
            "Напишите первое сообщение покупателю или отправьте голосовое 🎙",
            parse_mode="Markdown",
        )

    elif data.startswith("mode:"):
        new_mode = data.split(":", 1)[1]
        if new_mode == "coaching":
            if state.turn_count == 0:
                await query.message.reply_text(
                    "Сначала проведите несколько реплик в тренировке, потом запросите обратную связь."
                )
                return
            state.mode = "coaching"
            state.coaching_started = False
            logger.info("mode:coaching | user_id=%d turns=%d", user_id, state.turn_count)
            await query.message.reply_text("⏳ Анализирую диалог...")
            fb = await get_coaching_feedback(state)
            await query.message.reply_text(fb, parse_mode="Markdown", reply_markup=mode_keyboard())
        else:
            state.mode = "training"
            logger.info("mode:training | user_id=%d", user_id)
            await query.message.reply_text(
                "🎯 Продолжаем тренировку. Отправьте сообщение покупателю!",
            )


async def setup_commands(app) -> None:
    await app.bot.set_my_commands([
        BotCommand("start", "Начать заново / выбрать сценарий"),
        BotCommand("feedback", "Получить обратную связь по диалогу"),
        BotCommand("reset", "Начать сначала"),
    ])
