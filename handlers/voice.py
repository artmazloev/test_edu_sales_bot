import random
import logging
from telegram import Update, InputFile
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from io import BytesIO
from config import MAX_TURNS
from state import manager as state_manager
from services.llm import transcribe, speak
from services.errors import LLMNetworkError
from services.dialogue import get_buyer_reply, get_coaching_feedback, get_coaching_reply
from services.silence import schedule_silence_job, cancel_silence_job
from keyboards import training_keyboard, mode_keyboard
from phrases import THINKING_PHRASES

_NETWORK_ERROR_MSG = (
    "⚠️ Нет связи с сервером. Проверьте интернет и попробуйте ещё раз."
)

logger = logging.getLogger(__name__)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state = state_manager.get_or_create(user_id)
    logger.info("voice | user_id=%d mode=%s", user_id, state.mode)

    voice = update.message.voice
    tg_file = await context.bot.get_file(voice.file_id)
    ogg_bytes = bytes(await tg_file.download_as_bytearray())

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.RECORD_VOICE)
    thinking_msg = await update.message.reply_text(random.choice(THINKING_PHRASES))
    try:
        transcript = await transcribe(ogg_bytes)
    except LLMNetworkError:
        await thinking_msg.delete()
        logger.warning("voice | transcribe network error user_id=%d", user_id)
        await update.message.reply_text(_NETWORK_ERROR_MSG)
        return

    if state.mode == "coaching":
        try:
            if not state.coaching_started:
                await update.message.reply_text("⏳ Анализирую диалог...")
                fb = await get_coaching_feedback(state)
                await update.message.reply_text(fb, parse_mode="Markdown", reply_markup=mode_keyboard())
            else:
                reply = await get_coaching_reply(state, transcript)
                await update.message.reply_text(reply, reply_markup=mode_keyboard())
        except LLMNetworkError:
            logger.warning("voice | coaching network error user_id=%d", user_id)
            await update.message.reply_text(_NETWORK_ERROR_MSG)
        await thinking_msg.delete()
        return

    try:
        reply_text = await get_buyer_reply(state, transcript)
    except LLMNetworkError:
        await thinking_msg.delete()
        logger.warning("voice | buyer_reply network error user_id=%d", user_id)
        await update.message.reply_text(_NETWORK_ERROR_MSG, reply_markup=training_keyboard())
        return

    try:
        ogg_reply = await speak(reply_text)
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

    # Turn counter + auto-finish when limit reached
    turns = state.turn_count
    if turns >= MAX_TURNS:
        cancel_silence_job(context, user_id)
        state.mode = "coaching"
        state.coaching_started = False
        await update.message.reply_text(
            f"🏁 Диалог завершён — достигнут лимит {MAX_TURNS} ходов.\n⏳ Анализирую диалог..."
        )
        fb = await get_coaching_feedback(state)
        await update.message.reply_text(fb, parse_mode="Markdown", reply_markup=mode_keyboard())
    else:
        schedule_silence_job(context, user_id, update.effective_chat.id)
        remaining = MAX_TURNS - turns
        await update.message.reply_text(
            f"_Ход {turns} из {MAX_TURNS} — осталось {remaining}_",
            parse_mode="Markdown",
        )
