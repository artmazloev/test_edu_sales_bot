# Sales Training Bot

Telegram-бот для тренировки навыков продаж. Бот играет роль покупателя, продавец практикует диалог голосом или текстом, после чего получает разбор от виртуального тренера.

## Возможности

- **Режим тренировки** — бот симулирует реалистичного покупателя: выдвигает возражения, задаёт неудобные вопросы, меняет уровень интереса в зависимости от качества аргументов
- **Режим коучинга** — структурированный разбор диалога: что получилось, цитата ошибки, альтернативная фраза, оценка 1–10
- **Q&A с тренером** — после разбора можно задавать вопросы по технике продаж (SPIN, работа с возражениями, язык выгоды и т.д.)
- **Голосовые сообщения** — принимает OGG от пользователя (Whisper STT), отвечает голосом (TTS). Текст → аудио+подпись, голос → только аудио
- **Несколько сценариев** — премиум-смартфон (технарь) и смартфон в подарок (неопытный покупатель)

## Стек

| Компонент | Технология |
|---|---|
| Бот | python-telegram-bot 21 (async) |
| LLM | GPT-4o-mini |
| STT | OpenAI Whisper |
| TTS | OpenAI TTS (alloy) |
| Аудио | pydub + ffmpeg |
| Состояние | In-memory (dict по user_id) |

## Установка

### Требования
- Python 3.11+
- ffmpeg

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
# Вставить TELEGRAM_TOKEN и OPENAI_API_KEY в .env

python bot.py
```

## Переменные окружения

| Переменная | Описание |
|---|---|
| `TELEGRAM_TOKEN` | Токен бота от @BotFather |
| `OPENAI_API_KEY` | API-ключ OpenAI |
| `LOG_LEVEL` | Уровень логирования (default: `INFO`) |

## Структура проекта

```
bot.py                  # Точка входа, регистрация хэндлеров
config.py               # Токены, сценарии
keyboards.py            # Inline и Reply клавиатуры
phrases.py              # Фразы "покупатель думает..."
handlers/
  commands.py           # /start /reset /feedback + callback
  text.py               # Текстовые сообщения
  voice.py              # Голосовой пайплайн
services/
  openai_client.py      # chat() / transcribe() / speak()
  dialogue.py           # get_buyer_reply() / get_coaching_feedback() / get_coaching_reply()
  audio.py              # mp3_to_ogg()
state/
  manager.py            # UserState, in-memory хранилище
prompts/
  buyer.py              # Промпт покупателя (шаблон)
  coach.py              # Промпт тренера + Q&A промпт
```

## Команды бота

| Команда | Действие |
|---|---|
| `/start` | Начать заново, выбрать сценарий |
| `/feedback` | Получить обратную связь по текущему диалогу |
| `/reset` | Сбросить диалог |

Кнопки внизу чата дублируют основные действия без необходимости вводить команды.

## Оценка стоимости

Одна тестовая сессия (~10 реплик) на GPT-4o-mini: **~$0.001**

| Сервис | Модель | Цена |
|---|---|---|
| LLM | gpt-4o-mini | $0.15 / 1M токенов |
| STT | whisper-1 | $0.006 / мин |
| TTS | tts-1 | $15 / 1M символов |
