"""
Задача 2 — персонализация.

На входе: output/leads.csv (после Задачи 1).
На выходе: output/leads_personalized.csv с дополнительной колонкой
"Персонализация" — 1–2 предложения про компанию или ЛПР, основанные
на реальном содержимом сайта компании (без выдумок).

Движок LLM: Claude Code CLI (`claude -p`) — использует уже залогиненную
подписку, отдельный API-ключ не нужен. Если CLI не найден / не залогинен,
fallback на Anthropic API (env ANTHROPIC_API_KEY).
"""

import os
import csv
import sys
import json
import time
import shutil
import argparse
import subprocess
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}

# --- LLM-обёртка -------------------------------------------------------------

def _find_claude_cli() -> str | None:
    """Ищет исполняемый файл claude — сначала на PATH, потом стандартные места."""
    found = shutil.which("claude") or shutil.which("claude.cmd")
    if found:
        return found
    candidates = [
        Path(os.environ.get("APPDATA", "")) / "npm" / "claude.cmd",
        Path(os.environ.get("USERPROFILE", "")) / "AppData/Roaming/npm/claude.cmd",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None

def call_claude_cli(prompt: str, model: str = "claude-haiku-4-5") -> str:
    """Зовёт claude CLI в headless-режиме (`claude -p`)."""
    cli = _find_claude_cli()
    if not cli:
        raise RuntimeError("claude CLI не найден. Поставь: npm i -g @anthropic-ai/claude-code")
    result = subprocess.run(
        [cli, "-p", "--model", model, "--output-format", "text"],
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI error: {result.stderr.strip()}")
    return result.stdout.strip()

def call_anthropic_api(prompt: str, model: str = "claude-haiku-4-5") -> str:
    """Fallback через Anthropic API (нужен ANTHROPIC_API_KEY)."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY не задан")
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["content"][0]["text"].strip()

def llm(prompt: str, *, engine: str = "auto", model: str = "claude-haiku-4-5") -> str:
    """Универсальная точка вызова. engine: auto | cli | api"""
    if engine == "cli":
        return call_claude_cli(prompt, model)
    if engine == "api":
        return call_anthropic_api(prompt, model)
    # auto: пробуем CLI, затем API
    try:
        return call_claude_cli(prompt, model)
    except Exception as e:
        if os.environ.get("ANTHROPIC_API_KEY"):
            return call_anthropic_api(prompt, model)
        raise

# --- Сбор фактов о компании --------------------------------------------------

def fetch_site_text(url: str, max_chars: int = 6000) -> str:
    """Скачивает главную, возвращает чистый текст (без HTML/JS)."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        if r.status_code != 200:
            return ""
        r.encoding = r.apparent_encoding or r.encoding
        soup = BeautifulSoup(r.text, "lxml")
        for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
            tag.decompose()
        text = " ".join(soup.get_text(" ").split())
        return text[:max_chars]
    except Exception:
        return ""

# --- Генерация персонализации ------------------------------------------------

PROMPT_TEMPLATE = """Ты помогаешь B2B-аутрич-агентству писать персонализированные холодные письма.

Компания: {company}
Сайт: {site}
Категория: {category}

Вот текст с главной страницы их сайта (обрезано):
\"\"\"
{site_text}
\"\"\"

Задача: написать ОДНУ персонализационную фразу (1–2 предложения, до 30 слов) для холодного письма этой компании.

Жёсткие правила:
- Опирайся ТОЛЬКО на факты из текста сайта выше. Если фактов нет — верни строку «—» (одно тире).
- НЕ выдумывай цифры, кейсы, имена клиентов, награды.
- НЕ начинай со штампов типа «Заметил, что у вас», «Видел на сайте», «Поздравляю с».
- Формат: естественное наблюдение, которое можно вставить в начало письма.
- Без воды и эпитетов. Конкретика: продукт / специализация / ниша клиента / фича.
- Ответь ОДНОЙ фразой, без преамбулы и кавычек.

Пример хорошего: "Ваша платформа закрывает онбординг сотрудников «под ключ» — от оффера до адаптации, причём упор на крупный ритейл."
Пример плохого:  "Я заметил, что вы — классная CRM-система для бизнеса!"

Ответ:"""

def make_personalization(company: str, site: str, category: str, *, engine: str, model: str) -> str:
    site_text = fetch_site_text(site)
    if not site_text:
        return "—"
    prompt = PROMPT_TEMPLATE.format(
        company=company, site=site, category=category, site_text=site_text,
    )
    try:
        out = llm(prompt, engine=engine, model=model)
    except Exception as e:
        return f"[error: {e}]"
    # подрезаем кавычки/пунктуацию, если модель всё-таки обернула
    out = out.strip().strip('"“”«»').strip()
    return out or "—"

# --- main --------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=str(ROOT / "output" / "leads.csv"))
    ap.add_argument("--out", default=str(ROOT / "output" / "leads_personalized.csv"))
    ap.add_argument("--engine", choices=["auto", "cli", "api"], default="auto")
    ap.add_argument("--model", default="claude-haiku-4-5")
    ap.add_argument("--limit", type=int, default=0, help="обработать первые N строк (0 = все)")
    args = ap.parse_args()

    with open(args.inp, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    if args.limit:
        rows = rows[: args.limit]

    out_fields = list(rows[0].keys())
    if "personalization" not in out_fields:
        out_fields.append("personalization")

    with open(args.out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        for i, row in enumerate(rows, 1):
            print(f"[{i:>2}/{len(rows)}] {row['company']:<25}", end=" ", flush=True)
            p = make_personalization(
                row["company"], row["site"], row.get("category", ""),
                engine=args.engine, model=args.model,
            )
            row["personalization"] = p
            w.writerow(row)
            f.flush()
            print(p[:80] + ("…" if len(p) > 80 else ""))
            time.sleep(0.3)

    print(f"\nГотово: {args.out}")

if __name__ == "__main__":
    main()
