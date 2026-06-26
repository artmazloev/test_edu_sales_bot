from config import SCENARIOS
from state.manager import UserState
from prompts.buyer import build_buyer_prompt
from prompts.coach import COACH_PROMPT
from services.openai_client import chat


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

    messages = [
        {"role": "system", "content": COACH_PROMPT},
        {"role": "user", "content": f"Стенограмма диалога:\n\n{transcript}"},
    ]
    return await chat(messages)
