import random
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram import InputFile
from io import BytesIO
from state import manager as state_manager
from services.openai_client import transcribe, speak
from services.audio import mp3_to_ogg
from services.dialogue import get_buyer_reply, get_coaching_feedback, get_coaching_reply
from keyboards import training_keyboard, mode_keyboard
from phrases import THINKING_PHRASES

logger = logging.getLogger(__name__)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state = state_manager.get_or_create(user_id)
    logger.info("voice | user_id=%d mode=%s", user_id, state.mode)

    voice = update.message.voice
    tg_file = await context.bot.get_file(voice.file_id)
    ogg_bytes = bytes(await tg_file.download_as_bytearray())

    thinking_msg = await update.message.reply_text(random.choice(THINKING_PHRASES))
    transcript = await transcribe(ogg_bytes)

    if state.mode == "coaching":
        if not state.coaching_started:
            await update.message.reply_text("⏳ Анализирую диалог...")
            fb = await get_coaching_feedback(state)
            await update.message.reply_text(fb, parse_mode="Markdown", reply_markup=mode_keyboard())
        else:
            reply = await get_coaching_reply(state, transcript)
            await update.message.reply_text(reply, reply_markup=mode_keyboard())
        await thinking_msg.delete()
        return

    reply_text = await get_buyer_reply(state, transcript)

    try:
        mp3_bytes = await speak(reply_text)
        ogg_reply = mp3_to_ogg(mp3_bytes)
        await context.bot.send_voice(
            chat_id=update.effective_chat.id,
            voice=InputFile(BytesIO(ogg_reply), filename="reply.ogg"),
            reply_markup=training_keyboard(),
        )
        await thinking_msg.delete()
    except Exception as e:
        await thinking_msg.delete()
        is_forbidden = "voice_messages_forbidden" in str(e).lower()
        if is_forbidden:
            logger.warning("voice | send_voice forbidden for user_id=%d", user_id)
            await update.message.reply_text(
                "⚠️ У вас отключено получение голосовых сообщений от ботов.\n\n"
                "Можно:\n"
                "• Продолжить тренировку *текстом* — просто пишите в чат\n"
                "• Включить голос: Настройки → Конфиденциальность → Голосовые сообщения → Все",
                parse_mode="Markdown",
                reply_markup=training_keyboard(),
            )
        else:
            logger.exception("voice | send_voice failed for user_id=%d", user_id)
            await update.message.reply_text(reply_text, reply_markup=training_keyboard())
