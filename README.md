# Polza Agency — тестовое задание «Вайбкодер-аутричер»

База B2B-лидов + персонализация + цепочка писем для outbound-кампании Polza Agency.

## ЦА
Российские B2B SaaS / IT-сервисы для бизнеса (CRM, маркетинг-автоматизация,
HR-tech, customer support, аналитика, cloud, кибербез). 66 компаний в сид-листе.

## Структура

```
polza_test/
├── data/
│   └── seed_companies.py        # курированный сид-лист компаний
├── scripts/
│   ├── scrape_emails.py         # Задача 1: парсинг email-ов с сайтов
│   └── personalize.py           # Задача 2: персонализация через Claude CLI
├── output/
│   ├── leads.csv                # результат Задачи 1
│   └── leads_personalized.csv   # результат Задачи 2 (+колонка personalization)
├── emails/
│   └── sequence.md              # Задача 3: 3 письма с {{персонализация}}
├── requirements.txt
├── STACK.md                     # вайбкод-стек
└── README.md
```

## Запуск

```bash
# 1. зависимости
pip install -r requirements.txt

# 2. собрать базу email-ов (Задача 1, ~2–3 минуты)
python scripts/scrape_emails.py

# 3. предпосылка к Задаче 2 — установить и залогинить Claude Code CLI
#    (один раз, использует подписку Claude — отдельный API-ключ не нужен)
npm install -g @anthropic-ai/claude-code
claude /login

# 4. персонализация (Задача 2)
python scripts/personalize.py
# или с явным движком и моделью:
python scripts/personalize.py --engine cli --model claude-haiku-4-5
# fallback на Anthropic API (если выставлен ANTHROPIC_API_KEY):
python scripts/personalize.py --engine api
```

## Что куда идёт в Google Sheets

`output/leads_personalized.csv` импортируется в Google Sheets через
**Файл → Импорт → Загрузить → CSV → Заменить лист**. Кодировка UTF-8 (BOM),
разделитель — запятая. Цепочка писем — отдельный лист, скопированный
из `emails/sequence.md`.

## Заметки про данные

- Email-ы добыты автопарсером с публичных страниц компаний (контакты, о компании,
  футер, `mailto:` ссылки). Это, как правило, корпоративные ящики уровня
  `sales@`, `b2b@`, `hello@` — рабочие для первого касания, но для попадания
  в конкретного ЛПР нужен дополнительный пробив через Apollo / Snov.io / LinkedIn.
- Колонка `contact_name` оставлена пустой осознанно — её заполняют вручную
  после пробива (имя из подписи на сайте «О компании» или из LinkedIn).
- Колонка `all_emails` хранит все найденные ящики (чтобы можно было руками
  выбрать другой, если основной не подойдёт).
