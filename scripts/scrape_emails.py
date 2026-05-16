"""
Задача 1 — сбор базы. Из сид-списка компаний (data/seed_companies.py)
ходит по сайтам, тащит email-ы со страниц контактов / о компании / футера.

Выход: output/leads.csv с колонками:
    company, site, category, contact_name, email, all_emails

contact_name остаётся пустой — заполняется вручную (Apollo/LinkedIn)
или скриптом персонализации, если ЛПР удаётся вытащить с сайта.
"""

import re
import csv
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data"))
from seed_companies import COMPANIES  # noqa: E402

# --- настройки ---------------------------------------------------------------

# Страницы, которые обычно содержат контактные email-ы
CONTACT_PATHS = [
    "", "/contacts", "/contact", "/contacts/", "/contact-us",
    "/about", "/about-us", "/о-компании", "/о-нас", "/company",
    "/team", "/komanda", "/partners", "/b2b",
]

EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
)

# Префиксы email-ов в порядке убывания «полезности» для B2B-аутрича.
# Сначала ищем human/decision-maker, потом отдел продаж, потом любые общие.
PREFIX_PRIORITY = [
    "ceo", "founder", "co.founder", "owner",
    "bd", "partner", "partners", "b2b",
    "sales", "commercial",
    "hello", "info", "contact", "office",
    "marketing", "pr", "press", "media",
    "support", "help",
]

# Хвосты, которые НЕ настоящие email-ы (трекеры, картинки, заглушки)
BAD_SUBSTRINGS = (
    "sentry.io", "wixpress.com", "example.com", "example.ru",
    "noreply", "no-reply", "donotreply",
    ".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp", ".ico",
    "@2x", "@3x",
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml",
}

REQUEST_TIMEOUT = 8
SLEEP_BETWEEN_PAGES = 0.15
MAX_WORKERS = 8

# --- утилиты -----------------------------------------------------------------

def root_domain(url: str) -> str:
    """example.com из https://www.example.com/path"""
    netloc = urlparse(url).netloc.lower().lstrip("www.")
    parts = netloc.split(".")
    return parts[-2] if len(parts) >= 2 else netloc

def fetch(url: str) -> str:
    try:
        r = requests.get(
            url, headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        if r.status_code == 200 and "text/html" in r.headers.get("Content-Type", ""):
            r.encoding = r.apparent_encoding or r.encoding
            return r.text
    except requests.RequestException:
        pass
    return ""

def extract_emails(html: str) -> set[str]:
    """Тащит email-ы из HTML и из href=mailto: ссылок (на случай obfuscation)."""
    if not html:
        return set()
    out = set()
    # 1. mailto: ссылки — они почти всегда чистые
    try:
        soup = BeautifulSoup(html, "lxml")
        for a in soup.select("a[href^=mailto:]"):
            href = a.get("href", "")
            mail = href.replace("mailto:", "").split("?")[0].strip()
            if "@" in mail:
                out.add(mail.lower())
    except Exception:
        pass
    # 2. Любые email-подобные строки в тексте
    for m in EMAIL_RE.findall(html):
        out.add(m.lower())
    # фильтр мусора
    clean = {e for e in out if not any(bad in e for bad in BAD_SUBSTRINGS)}
    return clean

def pick_best_email(emails: list[str], company_root: str) -> str:
    """Выбирает «лучший» email под B2B-аутрич."""
    if not emails:
        return ""
    # 1) приоритет домену самой компании
    same = [e for e in emails if company_root in e.split("@")[-1]]
    pool = same or emails
    # 2) ранжируем по префиксу
    def rank(e: str) -> int:
        local = e.split("@")[0]
        for i, p in enumerate(PREFIX_PRIORITY):
            if local == p or local.startswith(p + ".") or local.startswith(p + "_"):
                return i
            if local.startswith(p):
                return i + len(PREFIX_PRIORITY)
        return 999
    pool.sort(key=rank)
    return pool[0]

def crawl_company(name: str, url: str, category: str) -> dict:
    domain = root_domain(url)
    found: set[str] = set()
    for path in CONTACT_PATHS:
        target = urljoin(url, path) if path else url
        html = fetch(target)
        new = extract_emails(html)
        found |= new
        # достаточно — если уже нашли что-то осмысленное на контактной странице
        if path and any(domain in e for e in new):
            break
        time.sleep(SLEEP_BETWEEN_PAGES)
    best = pick_best_email(sorted(found), domain)
    return {
        "company": name,
        "site": url,
        "category": category,
        "contact_name": "",          # обогащается вручную / в Apollo
        "email": best,
        "all_emails": "; ".join(sorted(found)),
    }

# --- main --------------------------------------------------------------------

def main() -> None:
    out_path = ROOT / "output" / "leads.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    total = len(COMPANIES)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {
            ex.submit(crawl_company, name, url, cat): (i, name)
            for i, (name, url, cat) in enumerate(COMPANIES, 1)
        }
        done = 0
        for fut in as_completed(futures):
            i, name = futures[fut]
            done += 1
            try:
                row = fut.result()
            except Exception as e:
                row = {"company": name, "site": "", "category": "", "contact_name": "",
                       "email": "", "all_emails": f"[error: {e}]"}
            rows.append(row)
            print(f"[{done:>2}/{total}] {row['company']:<25} {row['email'] or '—'}", flush=True)

    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["company", "site", "category", "contact_name", "email", "all_emails"],
        )
        w.writeheader()
        w.writerows(rows)

    hits = sum(1 for r in rows if r["email"])
    print(f"\nГотово. {hits}/{total} компаний с email. Результат: {out_path}")

if __name__ == "__main__":
    main()
