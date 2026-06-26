from telegram import Update
from telegram.ext import ContextTypes
from config import SCENARIOS
from state import manager as state_manager
from services.dialogue import get_coaching_feedback
from keyboards import mode_keyboard, scenario_keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state_manager.reset(user_id)
    await update.message.reply_text(
        "👋 Привет! Я бот для тренировки навыков продаж.\n\n"
        "🎯 *Режим тренировки* — я играю роль покупателя, вы продаёте мне продукт. "
        "Общайтесь голосом или текстом.\n\n"
        "📚 *Режим коучинга* — я анализирую ваш диалог и даю обратную связь.\n\n"
        "Выберите сценарий для начала:",
        parse_mode="Markdown",
        reply_markup=scenario_keyboard(),
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state_manager.reset(user_id)
    await update.message.reply_text(
        "🔄 Диалог сброшен. Начните новую тренировку!",
        reply_markup=scenario_keyboard(),
    )


async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state = state_manager.get_or_create(user_id)
    await update.message.reply_text("⏳ Анализирую диалог...")
    fb = await get_coaching_feedback(state)
    await update.message.reply_text(fb, reply_markup=mode_keyboard())


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    state = state_manager.get_or_create(user_id)
    data = query.data

    if data.startswith("scenario:"):
        key = data.split(":", 1)[1]
        if key not in SCENARIOS:
            await query.message.reply_text("Неизвестный сценарий.")
            return
        state_manager.reset(user_id)
        state = state_manager.get_or_create(user_id)
        state.scenario_key = key
        scenario = SCENARIOS[key]
        await query.message.reply_text(
            f"✅ Выбран сценарий: *{scenario['name']}*\n"
            f"Продукт: {scenario['product']}\n"
            f"Покупатель: {scenario['buyer_role']}\n\n"
            "Я в роли покупателя. Начинайте продавать — отправьте голосовое или текстовое сообщение!",
            parse_mode="Markdown",
        )

    elif data.startswith("mode:"):
        new_mode = data.split(":", 1)[1]
        if new_mode == "coaching":
            if state.turn_count == 0:
                await query.message.reply_text(
                    "Сначала проведите диалог в режиме тренировки, отправив несколько сообщений покупателю."
                )
                return
            state.mode = "coaching"
            await query.message.reply_text("⏳ Анализирую диалог...")
            fb = await get_coaching_feedback(state)
            await query.message.reply_text(fb, reply_markup=mode_keyboard())
        else:
            state.mode = "training"
            await query.message.reply_text(
                "🎯 Режим тренировки активирован. Продолжайте диалог с покупателем!",
                reply_markup=None,
            )
