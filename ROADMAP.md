# Roadmap

## Выполнено ✅

| # | Задача |
|---|---|
| [#3](https://github.com/artmazloev/test_edu_sales_bot/issues/3) | Убрать автоматическую расшифровку голосовых в чат |
| [#5](https://github.com/artmazloev/test_edu_sales_bot/issues/5) | Промежуточное сообщение «покупатель думает» |
| [#6](https://github.com/artmazloev/test_edu_sales_bot/issues/6) | Логирование: события, API-вызовы, ошибки |
| [#4](https://github.com/artmazloev/test_edu_sales_bot/issues/4) | Форматирование ОС: заголовки, эмодзи, цитата ошибки |
| [#2](https://github.com/artmazloev/test_edu_sales_bot/issues/2) | Коучинг → разбор + Q&A с тренером по технике продаж |
| [#1](https://github.com/artmazloev/test_edu_sales_bot/issues/1) | Навигация: постоянные кнопки, смена сценария, команды бота |
| [#8](https://github.com/artmazloev/test_edu_sales_bot/issues/8) | Убрать паузу между исчезновением «думает» и ответом покупателя |
| [#14](https://github.com/artmazloev/test_edu_sales_bot/issues/14) | Дублирование «Выберите сценарий» при /start |
| [#15](https://github.com/artmazloev/test_edu_sales_bot/issues/15) | Убрать кнопку ОС из inline-клавиатуры после каждого сообщения |
| [#17](https://github.com/artmazloev/test_edu_sales_bot/issues/17) | Кнопка «Завершить и получить ОС» в постоянной Reply Keyboard |
| [#18](https://github.com/artmazloev/test_edu_sales_bot/issues/18) | Переименовать «Сбросить диалог» → «Начать сначала» |
| —  | Фоллбэк на текст при заблокированных голосовых + инструкция |
| —  | Текст → аудио+подпись; голос → только аудио |
| —  | Два сценария: премиум-смартфон (технарь) и смартфон в подарок |
| —  | Переключение модели на gpt-4o-mini для экономичного тестирования |

---

## В работе / Следующий спринт 🔜

### UX и диалог
- [ ] [#7](https://github.com/artmazloev/test_edu_sales_bot/issues/7) Обработка сетевых ошибок (таймаут, потеря соединения) — friendly retry message
- [ ] [#9](https://github.com/artmazloev/test_edu_sales_bot/issues/9) Ограничение диалога (MAX_TURNS ~15) + счётчик ходов «ход 3 из ~15»
- [ ] [#10](https://github.com/artmazloev/test_edu_sales_bot/issues/10) ChatAction: TYPING / RECORD_VOICE пока бот «думает»
- [ ] [#12](https://github.com/artmazloev/test_edu_sales_bot/issues/12) Приветственное сообщение от покупателя при старте сценария — бот первым задаёт тон
- [ ] [#13](https://github.com/artmazloev/test_edu_sales_bot/issues/13) Кнопка «Повторить сценарий» после коучинга
- [ ] [#16](https://github.com/artmazloev/test_edu_sales_bot/issues/16) Расширить разбор ОС: 3–5 конкретных ошибок с цитатами
- [ ] [#11](https://github.com/artmazloev/test_edu_sales_bot/issues/11) Реакция покупателя на долгое молчание (>2 мин) через JobQueue
- [ ] Возможность переспросить покупателя без потери контекста (`/retry`)

### Коучинг
- [ ] Сравнение двух диалогов — прогресс продавца между сессиями
- [ ] Краткая ОС после каждых 3 ходов (необязательная, по кнопке)
- [ ] Выбор методологии коучинга: SPIN / SNAP / классическая работа с возражениями

### Сценарии
- [ ] Добавить 3–5 новых сценариев (авто, недвижимость, B2B-услуги)
- [ ] Настраиваемый уровень сложности покупателя: лёгкий / средний / агрессивный
- [ ] Редактор сценариев через команду бота или веб-интерфейс

### Техническое
- [ ] Персистентное хранилище (SQLite или Redis) — история между перезапусками
- [ ] Многопользовательская изоляция с rate limiting
- [ ] Деплой на сервер (Docker + systemd)
- [ ] Метрики: среднее время ответа, количество сессий, распределение оценок

---

## Долгосрочно 🔭

- [ ] Веб-дашборд для руководителя: статистика команды продавцов
- [ ] Интеграция с CRM для загрузки реальных сценариев из воронки
- [ ] Видеоразбор: запись экрана симуляции с субтитрами
- [ ] Мультиязычность (EN, KZ)
