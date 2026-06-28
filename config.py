import os
import logging
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Выбор провайдера моделей: "yandex" (по умолчанию) или "openai".
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "yandex").lower()

if LLM_PROVIDER == "openai":
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
elif LLM_PROVIDER == "yandex":
    YANDEX_API_KEY = os.environ["YANDEX_API_KEY"]
    YANDEX_FOLDER_ID = os.environ["YANDEX_FOLDER_ID"]
    # Тариф модели: "yandexgpt" (Pro) или "yandexgpt-lite".
    YANDEX_GPT_MODEL = os.getenv("YANDEX_GPT_MODEL", "yandexgpt")
    YANDEX_TTS_VOICE = os.getenv("YANDEX_TTS_VOICE", "filipp")
    YANDEX_STT_LANG = os.getenv("YANDEX_STT_LANG", "ru-RU")
else:
    raise RuntimeError(
        f"Неизвестный LLM_PROVIDER={LLM_PROVIDER!r}. Допустимо: 'yandex' или 'openai'."
    )

SCENARIOS: dict[str, dict] = {
    "smartphone_premium": {
        "name": "Смартфон премиум-класса",
        "product": "Смартфоны премиум-сегмента (iPhone 15/16, Samsung Galaxy S24+, Google Pixel 9 Pro) ценой от 80 000 до 150 000 рублей",
        "buyer_role": (
            "Технически грамотный мужчина 28–35 лет, разработчик ПО. "
            "Хорошо знает характеристики: процессоры (Snapdragon, A17/A18, Tensor), "
            "матрицы камер, частоту обновления экрана, SAR, версии Bluetooth/Wi-Fi. "
            "Сравнивает модели между собой и с конкурентами. "
            "Готов потратить 100–130 тысяч рублей, но хочет быть уверен, что переплата оправдана. "
            "Текущий телефон — Samsung Galaxy S21, доволен Android, к iOS относится скептически."
        ),
        "typical_objections": [
            "чем этот телефон лучше конкурента по такой же цене",
            "не понимаю, за что такая переплата по сравнению с прошлым годом",
            "у конкурента лучше характеристики камеры на бумаге",
            "мне важен Android, не хочу переходить на iOS",
            "подожду следующего поколения через полгода",
            "видел плохие отзывы о перегреве / автономности",
        ],
    },
    "smartphone_budget": {
        "name": "Смартфон в подарок",
        "product": "Смартфоны среднего сегмента (Samsung A55, Xiaomi 14C, realme 12+) ценой 20 000–40 000 рублей",
        "buyer_role": (
            "Женщина 45 лет, покупает смартфон в подарок сыну-студенту. "
            "Сама плохо разбирается в технике, ориентируется на бренд и внешний вид. "
            "Беспокоится о надёжности, боится переплатить или купить «не то». "
            "Бюджет — до 30 000 рублей, но может немного выйти за него, если убедят."
        ),
        "typical_objections": [
            "а вдруг он сломается быстро",
            "сын просил Samsung, а вы предлагаете другой бренд",
            "это дороговато, есть что-то подешевле",
            "мне надо посоветоваться с сыном",
            "а в интернете дешевле, зачем покупать у вас",
        ],
    },
}

DEFAULT_SCENARIO = "smartphone_premium"
MAX_TURNS = 15
