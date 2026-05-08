import feedparser
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

SOURCE_RSS = [
    "https://news.google.com/rss/search?q=gamification",
    "https://news.google.com/rss/search?q=gamification&hl=it&gl=IT&ceid=IT:it"
]

all_entries = []
seen = set()

# limite ultimi 30 giorni
cutoff_date = datetime.now().astimezone() - timedelta(days=30)

for url in SOURCE_RSS:
    feed = feedparser.parse(url)

    # nome della fonte RSS
    source = getattr(feed.feed, "title", "Fonte sconosciuta")

    for entry in feed.entries:

        title = entry.title.strip()

        # evita duplicati
        if title in seen:
            continue

        # recupera data articolo
        raw_date = getattr(entry, "published", "")

        try:
            parsed_date = parsedate_to_datetime(raw_date)

            # filtra ultimi 30 giorni
            if parsed_date < cutoff_date:
                continue

            published = parsed_date.strftime("%d/%m/%Y %H:%M")

        except:
            parsed_date = datetime.now().astimezone()
            published = "Data non disponibile"

        seen.add(title)

        all_entries.append({
            "title": title,
            "link": entry.link,
            "summary": getattr(entry, "summary", ""),
            "published": published,
            "source": source,
            "parsed_date": parsed_date,
        })

# ordina per data decrescente (più recente prima)
all_entries.sort(
    key=lambda x: x["parsed_date"],
    reverse=True
)

html = f"""
<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>Gamification News</title>
<link rel="stylesheet" href="static/style.css">
</head>

<body>

<h1>🎮 Gamification News</h1>

<p>Ultimo aggiornamento: {datetime.now().astimezone(ZoneInfo("Europe/Rome")).strftime("%d/%m/%Y %H:%M")}</p>
"""

for article in all_entries:
    html += f"""
    <div class="article">

        <div class="meta">
            <strong>Fonte:</strong> {article['source']} |
            <strong>Data:</strong> {article['published']}
        </div>

        <h2>
            <a href="{article['link']}" target="_blank">
                {article['title']}
            </a>
        </h2>

        <div class="summary">
            {article['summary']}
        </div>
    </div>
    """

html += """
<div class="footer">
Feed per temi di gamification. Parte del progetto "Questa è gamification!" di Giacomo D'angelo.
</div>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("HTML generato: index.html")
