# Вайбкод-стек

**IDE:** Claude Code (Claude Desktop, Windows MS Store, v1.7196)
**Основная модель в Claude Code:** Claude Opus 4.7 (`claude-opus-4-7`) — планирование, код.
**LLM в скрипте персонализации:** Claude Haiku 4.5 (`claude-haiku-4-5`) через `claude -p` CLI — быстро и дёшево по подписке, без отдельного API-ключа.

**Язык / рантайм:** Python 3.14.3 (Windows).
**Библиотеки:** `requests`, `beautifulsoup4`, `lxml`.

**Связка с LLM:** скрипт `scripts/personalize.py` вызывает Claude Code CLI через `subprocess`, fallback на Anthropic API (если выставлен `ANTHROPIC_API_KEY`).

**Источники данных:**
- Сид-список компаний — собран вручную из публичной памяти о рынке + сверка через каталоги startpack.ru / soware.ru.
- Email-ы и факты для персонализации — парсинг публичных сайтов компаний (`/contacts`, `/about`, главная).
