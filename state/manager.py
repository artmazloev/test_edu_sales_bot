from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
from config import DEFAULT_SCENARIO

@dataclass
class UserState:
    mode: Literal["training", "coaching"] = "training"
    scenario_key: str = DEFAULT_SCENARIO
    history: list[dict] = field(default_factory=list)
    turn_count: int = 0
    coaching_history: list[dict] = field(default_factory=list)
    coaching_started: bool = False
    last_message_at: datetime = field(default_factory=datetime.utcnow)
    silence_job_name: str = ""

_store: dict[int, UserState] = {}

def get_or_create(user_id: int) -> UserState:
    if user_id not in _store:
        _store[user_id] = UserState()
    return _store[user_id]

def reset(user_id: int) -> None:
    scenario_key = _store[user_id].scenario_key if user_id in _store else DEFAULT_SCENARIO
    _store[user_id] = UserState(scenario_key=scenario_key)
