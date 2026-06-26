import random
import logging
from telegram import Update
from telegram.ext import ContextTypes
from state import manager as state_manager
from services.dialogue import get_buyer_reply, get_coaching_feedback, get_coaching_reply
from keyboards import training_keyboard, mode_keyboard, scenario_keyboard
from phrases import THINKING_PHRASES

logger = logging.getLogger(__name__)

REPLY_KB_FEEDBACK = "📊 Обратная связь"
REPLY_KB_SCENARIO = "🔄 Сменить сценарий"
REPLY_KB_RESET = "🔁 Сбросить диалог"


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state = state_manager.get_or_create(user_id)
    text = update.message.text

    # Reply keyboard button handlers
    if text == REPLY_KB_FEEDBACK:
        if state.turn_count == 0:
            await update.message.reply_text(
                "Сначала проведите несколько реплик в тренировке, потом запросите обратную связь."
            )
            return
        state.mode = "coaching"
        state.coaching_started = False
        await update.message.reply_text("⏳ Анализирую диалог...")
        fb = await get_coaching_feedback(state)
        await update.message.reply_text(fb, parse_mode="Markdown", reply_markup=mode_keyboard())
        return

    if text == REPLY_KB_SCENARIO:
        await update.message.reply_text(
            "Выберите сценарий (текущий диалог будет сброшен):",
            reply_markup=scenario_keyboard(),
        )
        return

    if text == REPLY_KB_RESET:
        state_manager.reset(user_id)
        logger.info("reset via keyboard | user_id=%d", user_id)
        await update.message.reply_text(
            "🔄 Диалог сброшен. Выберите сценарий:",
            reply_markup=scenario_keyboard(),
        )
        return

    logger.info("text | user_id=%d mode=%s chars=%d", user_id, state.mode, len(text))

    if state.mode == "coaching":
        if not state.coaching_started:
            await update.message.reply_text("⏳ Анализирую диалог...")
            fb = await get_coaching_feedback(state)
            await update.message.reply_text(fb, parse_mode="Markdown", reply_markup=mode_keyboard())
        else:
            thinking_msg = await update.message.reply_text("💭 Тренер обдумывает ответ...")
            reply = await get_coaching_reply(state, text)
            await thinking_msg.delete()
            await update.message.reply_text(reply, reply_markup=mode_keyboard())
        return

    thinking_msg = await update.message.reply_text(random.choice(THINKING_PHRASES))
    reply = await get_buyer_reply(state, text)
    await thinking_msg.delete()

    await update.message.reply_text(reply, reply_markup=training_keyboard())
