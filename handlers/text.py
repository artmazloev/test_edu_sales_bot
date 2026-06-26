import random
import logging
from telegram import Update
from telegram.ext import ContextTypes
from state import manager as state_manager
from services.dialogue import get_buyer_reply, get_coaching_feedback, get_coaching_reply
from keyboards import feedback_nudge_keyboard, mode_keyboard
from phrases import THINKING_PHRASES

logger = logging.getLogger(__name__)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state = state_manager.get_or_create(user_id)
    text = update.message.text
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

    markup = None
    if state.turn_count > 0 and state.turn_count % 5 == 0:
        markup = feedback_nudge_keyboard()

    await update.message.reply_text(reply, reply_markup=markup)
