# Sales Training Bot

Telegram-бот для тренировки навыков продаж. Бот играет роль покупателя, продавец практикует диалог голосом или текстом, после чего получает разбор от виртуального тренера.

## Возможности

- **Режим тренировки** — бот симулирует реалистичного покупателя: выдвигает возражения, задаёт неудобные вопросы, меняет уровень интереса в зависимости от качества аргументов
- **Открывающая реплика** — при старте сценария покупатель первым подаёт реплику, задавая тон диалогу
- **Счётчик ходов** — после каждого ответа покупателя показывается прогресс «Ход N из 15»; при достижении лимита диалог завершается автоматически
- **Режим коучинга** — структурированный разбор диалога: сильные моменты, цитата ошибки, альтернативная фраза, оценка 1–10
- **Q&A с тренером** — после разбора можно задавать вопросы по технике продаж (SPIN, работа с возражениями, язык выгоды и т.д.)
- **Голосовые сообщения** — принимает OGG от пользователя (STT), отвечает голосом (TTS). Текст → аудио+подпись, голос → только аудио
- **Два провайдера моделей** — Яндекс (по умолчанию) или OpenAI, переключаются одной переменной `LLM_PROVIDER`
- **Несколько сценариев** — премиум-смартфон (технарь-разработчик) и смартфон в подарок (неопытный покупатель)
- **Обработка сбоев** — авто-retry при потере соединения (до 3 попыток, 2s/5s/10s), понятное сообщение при неудаче

## Стек

| Компонент | Яндекс (по умолчанию) | OpenAI |
|---|---|---|
| Бот | python-telegram-bot 21 (async) | ← то же |
| LLM | YandexGPT Pro | GPT-4o |
| STT | SpeechKit STT | OpenAI Whisper |
| TTS | SpeechKit TTS (filipp / alena по сценарию) | OpenAI TTS HD (onyx / nova по сценарию) |
| Аудио | OggOpus напрямую (без ffmpeg) | pydub + ffmpeg |
| Состояние | In-memory (dict по user_id) | ← то же |

Выбор провайдера — переменная `LLM_PROVIDER=yandex` (по умолчанию) или `openai`. Логика диалога, промпты и сценарии для обоих провайдеров одинаковые; голос покупателя задаётся per-scenario для каждого провайдера.

> Для OpenAI-пути экономичная конфигурация (gpt-4o-mini + tts-1 + alloy) задокументирована в [MODELS.md](MODELS.md) для быстрого отката.

## Установка

### Требования
- Python 3.11+
- ffmpeg — **только** для провайдера `openai` (путь Яндекса работает с OggOpus напрямую)

```bash
# macOS
brew install ffmpeg python@3.11

# Linux
sudo apt install ffmpeg python3.11
```

### Запуск

```bash
git clone https://github.com/artmazloev/test_edu_sales_bot.git
cd test_edu_sales_bot

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Вставить TELEGRAM_TOKEN и ключи провайдера (см. ниже) в .env

python bot.py
```

## Настройка Yandex Cloud с нуля

Чтобы запустить бота на моделях Яндекса (`LLM_PROVIDER=yandex`):

1. Зарегистрируйтесь в [Yandex Cloud](https://console.cloud.yandex.ru/) и включите биллинг (есть стартовый грант).
2. Создайте **каталог** (folder) и скопируйте его **ID** → это `YANDEX_FOLDER_ID`.
3. Создайте **сервисный аккаунт** и выдайте ему роли:
   - `ai.languageModels.user` — YandexGPT;
   - `ai.speechkit-stt.user` — распознавание речи;
   - `ai.speechkit-tts.user` — синтез речи.
4. Создайте **API-ключ** сервисного аккаунта → это `YANDEX_API_KEY`.
5. Заполните `.env`, оставив `LLM_PROVIDER=yandex`.

## Переменные окружения

| Переменная | Описание |
|---|---|
| `TELEGRAM_TOKEN` | Токен бота от @BotFather |
| `LLM_PROVIDER` | Провайдер моделей: `yandex` (по умолчанию) или `openai` |
| `LOG_LEVEL` | Уровень логирования: `DEBUG`, `INFO`, `WARNING` (default: `INFO`) |

**Для `LLM_PROVIDER=yandex`:**

| Переменная | Описание |
|---|---|
| `YANDEX_API_KEY` | API-ключ сервисного аккаунта Yandex Cloud |
| `YANDEX_FOLDER_ID` | ID каталога Yandex Cloud |
| `YANDEX_GPT_MODEL` | Тариф модели: `yandexgpt` (Pro, по умолчанию) или `yandexgpt-lite` |
| `YANDEX_TTS_VOICE` | Голос SpeechKit TTS (default: `filipp`) |
| `YANDEX_TTS_SPEED` | Темп синтеза: `0.1`–`3.0`, по умолчанию `1.2` (живее, чем дефолтный 1.0) |
| `YANDEX_STT_LANG` | Язык распознавания/синтеза (default: `ru-RU`) |

**Для `LLM_PROVIDER=openai`:**

| Переменная | Описание |
|---|---|
| `OPENAI_API_KEY` | API-ключ OpenAI |

## Структура проекта

```
bot.py                  # Точка входа, регистрация хэндлеров
config.py               # Токены, сценарии, MAX_TURNS
keyboards.py            # Inline и Reply клавиатуры
phrases.py              # Фразы "покупатель думает..."
handlers/
  commands.py           # /start /reset /feedback + callback-хэндлер
  text.py               # Текстовые сообщения
  voice.py              # Голосовой пайплайн
services/
  llm.py                # Диспетчер провайдера: реэкспорт chat/transcribe/speak по LLM_PROVIDER
  yandex_client.py      # Бэкенд Яндекса: chat() / transcribe() / speak() (YandexGPT + SpeechKit)
  openai_client.py      # Бэкенд OpenAI: chat() / transcribe() / speak() с retry
  errors.py             # LLMNetworkError — общая сетевая ошибка провайдеров
  dialogue.py           # get_buyer_opener() / get_buyer_reply() / get_coaching_feedback() / get_coaching_reply()
  audio.py              # mp3_to_ogg() (нужен только пути OpenAI)
state/
  manager.py            # UserState, in-memory хранилище
prompts/
  buyer.py              # Промпт покупателя (шаблон по сценарию)
  coach.py              # Промпт тренера + Q&A промпт
```

## Навигация в боте

### Постоянная клавиатура (внизу чата)
| Кнопка | Действие |
|---|---|
| 🏁 Завершить и получить ОС | Завершить диалог и получить полный разбор |
| 🔄 Сменить сценарий | Выбрать другой сценарий (диалог сбрасывается) |
| 🔁 Начать сначала | Сбросить диалог и сценарий |

### Команды бота
| Команда | Действие |
|---|---|
| `/start` | Начать заново, выбрать сценарий |
| `/feedback` | Получить обратную связь по текущему диалогу |
| `/reset` | Сбросить диалог |

## Пайплайн голосового сообщения

```
Пользователь отправляет OGG
  → ChatAction.RECORD_VOICE (нативный индикатор)
  → STT (транскрипция)            — SpeechKit STT / Whisper
  → LLM (ответ покупателя)        — YandexGPT Pro / GPT-4o
  → TTS → OGG/Opus                — SpeechKit TTS (напрямую) / OpenAI TTS → MP3 → OGG
  → send_voice (только аудио, без подписи)
  → счётчик ходов
```

При входящем тексте — то же самое, но ответ отправляется как аудио + текстовая подпись.

> SpeechKit отдаёт OggOpus сразу, поэтому на пути Яндекса конвертация (ffmpeg/pydub) не нужна.
> Синхронное распознавание SpeechKit рассчитано на короткие голосовые (до ~30 с / 1 МБ).

## Оценка стоимости

Тарифицируется по выбранному провайдеру. Ориентиры:

**Яндекс** (`LLM_PROVIDER=yandex`) — оплата по прайсу [Yandex Cloud](https://yandex.cloud/ru/prices):
YandexGPT Pro — за 1000 токенов; SpeechKit STT — за секунды аудио; SpeechKit TTS — за символы синтеза.

**OpenAI** (`LLM_PROVIDER=openai`) — одна сессия ~15 реплик:

| Конфиг | Сессия ~15 реплик |
|---|---|
| Текущий (gpt-4o + tts-1-hd) | ~$0.015 |
| Экономичный (gpt-4o-mini + tts-1) | ~$0.002 |

| Сервис | Модель | Цена |
|---|---|---|
| LLM | gpt-4o | $2.50 / 1M входных токенов |
| STT | whisper-1 | $0.006 / мин |
| TTS | tts-1-hd | $30 / 1M символов |

Инструкция по переключению OpenAI-пути на экономичный режим — в [MODELS.md](MODELS.md).
