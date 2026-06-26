import logging
from config import SCENARIOS
from state.manager import UserState
from prompts.buyer import build_buyer_prompt
from prompts.coach import COACH_PROMPT, COACH_QA_PROMPT
from services.openai_client import chat

logger = logging.getLogger(__name__)


async def get_buyer_opener(state: UserState) -> str:
    """Generate the buyer's opening remark to kick off the scenario."""
    scenario = SCENARIOS[state.scenario_key]
    system_prompt = build_buyer_prompt(
        product=scenario["product"],
        buyer_role=scenario["buyer_role"],
        typical_objections=scenario["typical_objections"],
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": (
            "Ты только что вошёл в магазин электроники. Продавец ещё не подошёл. "
            "Произнеси одну короткую фразу (1–2 предложения), которая показывает, что ты чем-то интересуешься или просто осматриваешься. "
            "Не раскрывай сразу всех деталей — просто дай продавцу повод подойти."
        )},
    ]
    opener = await chat(messages)
    state.history.append({"role": "assistant", "content": opener})
    logger.info("buyer_opener | scenario=%s", state.scenario_key)
    return opener


async def get_buyer_reply(state: UserState, user_message: str) -> str:
    scenario = SCENARIOS[state.scenario_key]
    system_prompt = build_buyer_prompt(
        product=scenario["product"],
        buyer_role=scenario["buyer_role"],
        typical_objections=scenario["typical_objections"],
    )
    state.history.append({"role": "user", "content": user_message})
    messages = [{"role": "system", "content": system_prompt}] + state.history
    reply = await chat(messages)
    state.history.append({"role": "assistant", "content": reply})
    state.turn_count += 1
    return reply


async def get_coaching_feedback(state: UserState) -> str:
    if not state.history:
        return "Диалог пока пуст. Начните тренировку — отправьте сообщение покупателю."

    transcript_lines = []
    for msg in state.history:
        role_label = "Продавец" if msg["role"] == "user" else "Покупатель"
        transcript_lines.append(f"{role_label}: {msg['content']}")
    transcript = "\n".join(transcript_lines)

    user_msg = {"role": "user", "content": f"Стенограмма диалога:\n\n{transcript}"}
    messages = [{"role": "system", "content": COACH_PROMPT}, user_msg]
    feedback = await chat(messages)

    state.coaching_history = [
        user_msg,
        {"role": "assistant", "content": feedback},
    ]
    state.coaching_started = True
    logger.info("coaching_feedback | turns=%d", state.turn_count)
    return feedback


async def get_coaching_reply(state: UserState, user_message: str) -> str:
    state.coaching_history.append({"role": "user", "content": user_message})
    messages = [{"role": "system", "content": COACH_QA_PROMPT}] + state.coaching_history
    reply = await chat(messages)
    state.coaching_history.append({"role": "assistant", "content": reply})
    logger.info("coaching_reply | coaching_turns=%d", len(state.coaching_history))
    return reply
