"""Фасад над LLM-провайдерами. Выбор бэкенда — по config.LLM_PROVIDER.

Условный импорт гарантирует, что модуль неиспользуемого провайдера (и его ключи)
не загружается, поэтому держать оба набора ключей одновременно не нужно.
"""
from config import LLM_PROVIDER
from services.errors import LLMNetworkError  # noqa: F401 — реэкспорт для удобства импорта

if LLM_PROVIDER == "yandex":
    from services import yandex_client as _backend
elif LLM_PROVIDER == "openai":
    from services import openai_client as _backend
else:  # pragma: no cover — config уже валидирует значение
    raise RuntimeError(f"Unknown LLM_PROVIDER={LLM_PROVIDER}")

chat = _backend.chat
transcribe = _backend.transcribe
speak = _backend.speak
