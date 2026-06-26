# Конфигурация моделей

## Текущая (качество)

| Компонент | Модель / голос | Файл |
|---|---|---|
| LLM | `gpt-4o` | `services/openai_client.py`, строка 29 |
| TTS | `tts-1-hd` | `services/openai_client.py`, строка 58 |
| TTS голос — премиум сценарий | `onyx` | `config.py` → `smartphone_premium.tts_voice` |
| TTS голос — бюджет сценарий | `nova` | `config.py` → `smartphone_budget.tts_voice` |
| STT | `whisper-1` | `services/openai_client.py`, строка 44 |

---

## Экономичная (для отката)

| Компонент | Модель / голос |
|---|---|
| LLM | `gpt-4o-mini` |
| TTS | `tts-1` |
| TTS голос (оба сценария) | `alloy` |
| STT | `whisper-1` (без альтернатив) |

### Как откатить

1. `services/openai_client.py`:
   - строка 29: `model: str = "gpt-4o"` → `"gpt-4o-mini"`
   - строка 58: `model="tts-1-hd"` → `"tts-1"`
2. `config.py`: в обоих сценариях `"tts_voice": "alloy"` (или убрать поле — дефолт `onyx`)

### Разница в стоимости (1 сессия ~15 реплик)

| Конфиг | Примерная стоимость |
|---|---|
| Экономичный | ~$0.002 |
| Качественный | ~$0.015 |
