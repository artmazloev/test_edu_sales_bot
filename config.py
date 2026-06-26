import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

SCENARIOS: dict[str, dict] = {
    "b2b_software": {
        "name": "CRM для бизнеса",
        "product": "CRM-система для отдела продаж",
        "buyer_role": "IT-директор среднего предприятия (50–200 сотрудников)",
        "typical_objections": [
            "у нас уже есть решение",
            "слишком дорого",
            "нет времени на внедрение",
            "не уверен в безопасности данных",
        ],
    },
    "b2c_insurance": {
        "name": "Страхование КАСКО",
        "product": "Страховой полис КАСКО для автомобиля",
        "buyer_role": "Частный автовладелец, 35 лет, бережливый",
        "typical_objections": [
            "это слишком дорого",
            "мне это не нужно",
            "подумаю позже",
            "у других компаний дешевле",
        ],
    },
    "b2b_consulting": {
        "name": "Бизнес-консалтинг",
        "product": "Услуги бизнес-консалтинга по оптимизации процессов",
        "buyer_role": "Генеральный директор малого бизнеса, прагматичный скептик",
        "typical_objections": [
            "не вижу конкретного результата",
            "мои сотрудники справятся сами",
            "был плохой опыт с консультантами",
            "бюджет ограничен",
        ],
    },
}

DEFAULT_SCENARIO = "b2b_software"
