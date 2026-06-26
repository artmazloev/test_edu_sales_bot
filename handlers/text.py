import random
import logging
from io import BytesIO
from telegram import Update, InputFile, ChatAction
from telegram.ext import ContextTypes
from openai import APIConnectionError, APITimeoutError
from config import MAX_TURNS
from state import manager as state_manager
from services.dialogue import get_buyer_reply, get_coaching_feedback, get_coaching_reply
from services.openai_client import speak
from services.audio import mp3_to_ogg
from keyboards import training_keyboard, mode_keyboard, scenario_keyboard
from phrases import THINKING_PHRASES

logger = logging.getLogger(__name__)

_NETWORK_ERROR_MSG = (
    "⚠️ Нет связи с сервером. Проверьте интернет и попробуйте ещё раз."
)

REPLY_KB_FINISH = "🏁 Завершить и получить ОС"
REPLY_KB_SCENARIO = "🔄 Сменить сценарий"
REPLY_KB_RESET = "🔁 Начать сначала"


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state = state_manager.get_or_create(user_id)
    text = update.message.text

    if text == REPLY_KB_FINISH:
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
            "🔁 Начинаем сначала. Выберите сценарий:",
            reply_markup=scenario_keyboard(),
        )
        return

    logger.info("text | user_id=%d mode=%s chars=%d", user_id, state.mode, len(text))

    if state.mode == "coaching":
        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            if not state.coaching_started:
                await update.message.reply_text("⏳ Анализирую диалог...")
                fb = await get_coaching_feedback(state)
                await update.message.reply_text(fb, parse_mode="Markdown", reply_markup=mode_keyboard())
            else:
                thinking_msg = await update.message.reply_text("💭 Тренер обдумывает ответ...")
                reply = await get_coaching_reply(state, text)
                await update.message.reply_text(reply, reply_markup=mode_keyboard())
                await thinking_msg.delete()
        except (APIConnectionError, APITimeoutError):
            logger.warning("text | coaching network error user_id=%d", user_id)
            await update.message.reply_text(_NETWORK_ERROR_MSG)
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.RECORD_VOICE)
    thinking_msg = await update.message.reply_text(random.choice(THINKING_PHRASES))
    try:
        reply_text = await get_buyer_reply(state, text)
    except (APIConnectionError, APITimeoutError):
        await thinking_msg.delete()
        logger.warning("text | buyer_reply network error user_id=%d", user_id)
        await update.message.reply_text(_NETWORK_ERROR_MSG, reply_markup=training_keyboard())
        return

    try:
        mp3_bytes = await speak(reply_text)
        ogg_reply = mp3_to_ogg(mp3_bytes)
        await context.bot.send_voice(
            chat_id=update.effective_chat.id,
            voice=InputFile(BytesIO(ogg_reply), filename="reply.ogg"),
            caption=f"🤖 {reply_text}",
            reply_markup=training_keyboard(),
        )
        await thinking_msg.delete()
    except Exception as e:
        await thinking_msg.delete()
        is_forbidden = "voice_messages_forbidden" in str(e).lower()
        if is_forbidden:
            logger.warning("text | send_voice forbidden for user_id=%d", user_id)
            await update.message.reply_text(
                "⚠️ У вас отключено получение голосовых сообщений от ботов.\n\n"
                "Можно:\n"
                "• Продолжить тренировку *текстом* — просто пишите в чат\n"
                "• Включить голос: Настройки → Конфиденциальность → Голосовые сообщения → Все\n\n"
                f"🤖 {reply_text}",
                parse_mode="Markdown",
                reply_markup=training_keyboard(),
            )
        else:
            logger.exception("text | send_voice failed for user_id=%d", user_id)
            await update.message.reply_text(reply_text, reply_markup=training_keyboard())

    # Turn counter + auto-finish when limit reached
    turns = state.turn_count
    if turns >= MAX_TURNS:
        state.mode = "coaching"
        state.coaching_started = False
        await update.message.reply_text(
            f"🏁 Диалог завершён — достигнут лимит {MAX_TURNS} ходов.\n⏳ Анализирую диалог..."
        )
        fb = await get_coaching_feedback(state)
        await update.message.reply_text(fb, parse_mode="Markdown", reply_markup=mode_keyboard())
    else:
        remaining = MAX_TURNS - turns
        await update.message.reply_text(
            f"_Ход {turns} из {MAX_TURNS} — осталось {remaining}_",
            parse_mode="Markdown",
        )
