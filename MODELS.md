# Конфигурация моделей

Провайдер выбирается переменной `LLM_PROVIDER` (`yandex` по умолчанию или `openai`).
Этот файл описывает модели **OpenAI-пути** (`LLM_PROVIDER=openai`) и его экономичный откат.
Модели Яндекса (`yandexgpt`, SpeechKit) настраиваются через env-переменные `YANDEX_*` —
см. README.

## Яндекс (по умолчанию)

| Компонент | Модель / голос | Где задаётся |
|---|---|---|
| LLM | `yandexgpt` (Pro) | `YANDEX_GPT_MODEL` |
| STT | SpeechKit STT | `services/yandex_client.py` |
| TTS | SpeechKit TTS | `YANDEX_TTS_VOICE` / per-scenario `tts_voice.yandex` |
| TTS голос — премиум | `filipp` | `config.py` → `smartphone_premium.tts_voice.yandex` |
| TTS голос — бюджет | `alena` | `config.py` → `smartphone_budget.tts_voice.yandex` |
| Темп речи TTS | `1.2` (0.1–3.0) | `YANDEX_TTS_SPEED` |

Список доступных голосов с образцами: <https://yandex.cloud/ru/docs/speechkit/tts/voices>

---

## OpenAI — текущая (качество)

| Компонент | Модель / голос | Файл |
|---|---|---|
| LLM | `gpt-4o` | `services/openai_client.py` (def chat) |
| TTS | `tts-1-hd` | `services/openai_client.py` (def speak) |
| TTS голос — премиум сценарий | `onyx` | `config.py` → `smartphone_premium.tts_voice.openai` |
| TTS голос — бюджет сценарий | `nova` | `config.py` → `smartphone_budget.tts_voice.openai` |
| STT | `whisper-1` | `services/openai_client.py` (def transcribe) |

---

## OpenAI — экономичная (для отката)

| Компонент | Модель / голос |
|---|---|
| LLM | `gpt-4o-mini` |
| TTS | `tts-1` |
| TTS голос (оба сценария) | `alloy` |
| STT | `whisper-1` (без альтернатив) |

### Как откатить

1. `services/openai_client.py`:
   - `def chat`: `model: str = "gpt-4o"` → `"gpt-4o-mini"`
   - `def speak`: `model="tts-1-hd"` → `"tts-1"`
2. `config.py`: в обоих сценариях у ключа `openai` поставить `"alloy"`
   (например `"tts_voice": {"openai": "alloy", "yandex": "filipp"}`)

### Разница в стоимости (1 сессия ~15 реплик)

| Конфиг | Примерная стоимость |
|---|---|
| Экономичный | ~$0.002 |
| Качественный | ~$0.015 |
