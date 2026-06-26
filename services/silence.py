import random
import logging
from datetime import datetime, timedelta
from telegram.ext import ContextTypes
from state import manager as state_manager

logger = logging.getLogger(__name__)

SILENCE_TIMEOUT = 120  # seconds
SILENCE_JOB_PREFIX = "silence_"

_NUDGES = [
    "Ну так что скажете?",
    "Я вас слушаю...",
    "Есть ещё вопросы?",
    "Вы ещё здесь?",
    "Могу ещё что-то рассказать?",
]


async def _silence_callback(context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id: int = context.job.data["user_id"]
    chat_id: int = context.job.data["chat_id"]
    state = state_manager.get_or_create(user_id)

    if state.mode != "training" or state.turn_count == 0:
        return

    elapsed = (datetime.utcnow() - state.last_message_at).total_seconds()
    if elapsed < SILENCE_TIMEOUT - 5:
        return

    nudge = random.choice(_NUDGES)
    state.history.append({"role": "assistant", "content": nudge})
    logger.info("silence_nudge | user_id=%d elapsed=%.0fs", user_id, elapsed)
    await context.bot.send_message(chat_id=chat_id, text=f"🛒 *Покупатель:* {nudge}", parse_mode="Markdown")


def schedule_silence_job(context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int) -> None:
    state = state_manager.get_or_create(user_id)
    job_name = f"{SILENCE_JOB_PREFIX}{user_id}"

    # Cancel previous job if any
    for job in context.job_queue.get_jobs_by_name(job_name):
        job.schedule_removal()

    state.last_message_at = datetime.utcnow()
    state.silence_job_name = job_name
    context.job_queue.run_once(
        _silence_callback,
        when=SILENCE_TIMEOUT,
        data={"user_id": user_id, "chat_id": chat_id},
        name=job_name,
    )


def cancel_silence_job(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    state = state_manager.get_or_create(user_id)
    for job in context.job_queue.get_jobs_by_name(state.silence_job_name):
        job.schedule_removal()
    state.silence_job_name = ""
