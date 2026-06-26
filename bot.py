import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from config import TELEGRAM_TOKEN, LOG_LEVEL
from handlers.commands import start, reset, feedback, handle_callback, setup_commands
from handlers.voice import handle_voice
from handlers.text import handle_text

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def post_init(app: Application) -> None:
    await setup_commands(app)


def main() -> None:
    app = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("feedback", feedback))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
