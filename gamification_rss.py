import feedparser
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo
from jinja2 import Environment, FileSystemLoader

from config import (
    SOURCE_RSS,
    DAYS_LIMIT,
    TIMEZONE,
    PAGE_TITLE,
    FOOTER_TEXT
)

all_entries = []
seen = set()

cutoff_date = datetime.now(ZoneInfo("UTC")) - timedelta(days=DAYS_LIMIT)

def safe_parse_date(entry):
    for key in ("published", "updated", "created"):
        raw = getattr(entry, key, None)
        if raw:
            try:
                dt = parsedate_to_datetime(raw)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=ZoneInfo("UTC"))
                return dt.astimezone(ZoneInfo("UTC"))
            except Exception:
                continue
    return datetime.now(ZoneInfo("UTC"))

for url in SOURCE_RSS:
    feed = feedparser.parse(url)
    source = getattr(feed.feed, "title", "Fonte sconosciuta")

    for entry in feed.entries:

        title = getattr(entry, "title", "").strip()
        link = getattr(entry, "link", "").strip()

        entry_id = link or title

        if not entry_id or entry_id in seen:
            continue

        parsed_date = safe_parse_date(entry)

        if parsed_date < cutoff_date:
            continue

        seen.add(entry_id)

        all_entries.append({
            "title": title or "Senza titolo",
            "link": link,
            "summary": getattr(entry, "summary", ""),
            "published": parsed_date.strftime("%d/%m/%Y %H:%M"),
            "source": source,
            "parsed_date": parsed_date,
        })

# ordinamento stabile (anche in caso di pari data)
all_entries.sort(
    key=lambda x: (x["parsed_date"], x["title"]),
    reverse=True
)

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("homepage.html")

html = template.render(
    page_title=PAGE_TITLE,
    footer_text=FOOTER_TEXT,
    updated_at=datetime.now(TIMEZONE).strftime("%d/%m/%Y %H:%M"),
    articles=all_entries
)

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("HTML generato: index.html")
