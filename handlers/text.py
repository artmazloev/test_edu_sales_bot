from telegram import Update
from telegram.ext import ContextTypes
from state import manager as state_manager
from services.dialogue import get_buyer_reply, get_coaching_feedback
from keyboards import feedback_nudge_keyboard, mode_keyboard


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state = state_manager.get_or_create(user_id)
    text = update.message.text

    if state.mode == "coaching":
        await update.message.reply_text("⏳ Анализирую диалог...")
        fb = await get_coaching_feedback(state)
        await update.message.reply_text(fb, reply_markup=mode_keyboard())
        return

    reply = await get_buyer_reply(state, text)

    markup = None
    if state.turn_count > 0 and state.turn_count % 5 == 0:
        markup = feedback_nudge_keyboard()

    await update.message.reply_text(reply, reply_markup=markup)
