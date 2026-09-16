#!/usr/bin/env python3
"""Build a static site from the Daily German lesson HTML files.

Creates <folder>/website/ containing:
  - index.html  (archive page, newest first)
  - one copy of each German_Lesson_YYYY-MM-DD.html

Re-run any time after new lessons are added.
"""
import re, shutil, sys
from pathlib import Path
from datetime import date

BASE = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
LESSON_DIR = BASE / "lektionen" if (BASE / "lektionen").is_dir() else BASE
OUT = BASE / "website"
OUT.mkdir(exist_ok=True)

MONTHS = ["Januar","Februar","März","April","Mai","Juni","Juli",
          "August","September","Oktober","November","Dezember"]
DAYS = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]

lessons = []
for f in sorted(LESSON_DIR.glob("German_Lesson_*.html")):
    m = re.match(r"German_Lesson_(\d{4})-(\d{2})-(\d{2})\.html$", f.name)
    if not m:
        continue
    y, mo, d = (int(x) for x in m.groups())
    html = f.read_text(encoding="utf-8", errors="replace")
    t = re.search(r'<h2 class="heading">(.*?)</h2>', html, re.S)
    title = re.sub(r"<[^>]+>", "", t.group(1)).strip() if t else f.stem
    lessons.append({"file": f, "date": date(y, mo, d), "title": title})

lessons.sort(key=lambda x: x["date"], reverse=True)

BACK_LINK = (
    '<p style="max-width:760px;margin:0 auto 18px;padding:0 24px;'
    'font-size:0.85rem;">'
    '<a href="index.html" style="color:#8c8778;text-decoration:none;">'
    '&larr; Alle Lektionen</a>'
    '<span style="color:#cfc8b4;margin:0 8px;">&middot;</span>'
    '<a href="woerterbuch.html" style="color:#8c8778;text-decoration:none;">'
    'Wörterbuch</a></p>'
)
VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1">'

def prepare(html):
    """Make a lesson page web/phone friendly: add viewport + back link."""
    if 'name="viewport"' not in html:
        html = html.replace("<meta charset=\"UTF-8\">",
                            "<meta charset=\"UTF-8\">\n" + VIEWPORT, 1)
    if 'href="index.html"' not in html:
        html = html.replace("<body>", "<body>\n" + BACK_LINK, 1)
    # let the cards breathe on narrow screens
    if "@media (max-width:560px)" not in html:
        html = html.replace(
            "</style>",
            "  @media (max-width:560px){\n"
            "    body{padding:20px 12px 70px;}\n"
            "    .card{padding:22px 18px;border-radius:16px;}\n"
            "    table{font-size:0.86rem;}\n"
            "    th,td{padding:8px 5px;}\n"
            "    h2.heading{font-size:1.3rem;}\n"
            "  }\n</style>", 1)
    return html

for L in lessons:
    (OUT / L["file"].name).write_text(
        prepare(L["file"].read_text(encoding="utf-8", errors="replace")),
        encoding="utf-8")

# group by month
groups = []
for L in lessons:
    key = (L["date"].year, L["date"].month)
    if not groups or groups[-1][0] != key:
        groups.append((key, []))
    groups[-1][1].append(L)

rows = []
for (y, mo), items in groups:
    rows.append(f'<div class="month">{MONTHS[mo-1]} {y}</div>')
    rows.append('<ul class="lessons">')
    for L in items:
        dt = L["date"]
        label = f"{DAYS[dt.weekday()]}, {dt.day}. {MONTHS[dt.month-1]}"
        rows.append(
            f'<li><a href="{L["file"].name}">'
            f'<span class="d">{label}</span>'
            f'<span class="t">{L["title"]}</span></a></li>'
        )
    rows.append("</ul>")
listing = "\n".join(rows)

newest = lessons[0] if lessons else None
latest_block = ""
if newest:
    dt = newest["date"]
    latest_block = (
        f'<a class="latest" href="{newest["file"].name}">'
        f'<span class="label">Neueste Lektion</span>'
        f'<span class="lt">{newest["title"]}</span>'
        f'<span class="ld">{DAYS[dt.weekday()]}, {dt.day}. {MONTHS[dt.month-1]} {dt.year}</span>'
        f'</a>'
    )

index = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BSK70 – Deutsch täglich | Lesen &amp; Üben</title>
<style>
  :root{{color-scheme:light;
    --page-bg:#ffffff; --card-bg:#f6f2e9;
    --badge-date-bg:#f3e6c8; --badge-date-text:#7a6535;
    --badge-level-bg:#e6f0e1; --badge-level-text:#3f6b3f;
    --label-grey:#9a9488; --heading:#1c1c1c; --body-text:#2c2c2a;
    --border-soft:#eae5d6;}}
  *{{box-sizing:border-box;}}
  html{{font-size:14px;}}
  body{{font-family:"Segoe UI",Helvetica,Arial,sans-serif;background:var(--page-bg);
    color:var(--body-text);margin:0;padding:32px 24px 80px;}}
  .wrap{{max-width:760px;margin:0 auto;}}
  .meta-row{{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:22px;}}
  .badge{{display:inline-block;padding:8px 16px;border-radius:999px;
    font-size:0.85rem;font-weight:600;}}
  .badge-date{{background:var(--badge-date-bg);color:var(--badge-date-text);}}
  .badge-level{{background:var(--badge-level-bg);color:var(--badge-level-text);}}
  .label{{text-transform:uppercase;letter-spacing:.12em;font-size:0.78rem;
    color:var(--label-grey);font-weight:600;margin-bottom:8px;display:block;}}
  h1{{font-size:1.65rem;font-weight:700;color:var(--heading);margin:0 0 10px 0;}}
  .tagline{{text-transform:uppercase;letter-spacing:.12em;font-size:0.78rem;
    color:var(--label-grey);font-weight:600;margin:0 0 12px;}}
  .intro{{font-size:1rem;line-height:1.7;color:#55514a;margin:0 0 28px 0;}}
  a.latest{{display:block;background:var(--card-bg);border-radius:20px;
    padding:26px 30px;text-decoration:none;margin-bottom:34px;}}
  a.latest .lt{{display:block;font-size:1.3rem;font-weight:700;
    color:var(--heading);margin:4px 0 8px;line-height:1.35;}}
  a.latest .ld{{display:block;font-size:0.88rem;color:#8c8778;}}
  a.latest:hover .lt{{text-decoration:underline;}}
  a.dict{{display:block;background:#eef3ea;border-radius:20px;
    padding:22px 26px;text-decoration:none;margin-bottom:14px;}}
  a.dict .dt{{display:block;font-size:1.12rem;font-weight:700;
    color:#2f4f2f;margin:4px 0 6px;}}
  a.dict .dd{{display:block;font-size:0.85rem;color:#5d7a5d;line-height:1.6;}}
  a.dict .label{{color:#6d8a6d;}}
  a.dict:hover .dt{{text-decoration:underline;}}
  .month{{text-transform:uppercase;letter-spacing:.12em;font-size:0.76rem;
    color:var(--label-grey);font-weight:700;margin:26px 0 10px;}}
  ul.lessons{{list-style:none;padding:0;margin:0;}}
  ul.lessons li{{border-bottom:1px solid var(--border-soft);}}
  ul.lessons li:last-child{{border-bottom:none;}}
  ul.lessons a{{display:flex;gap:16px;align-items:baseline;padding:13px 4px;
    text-decoration:none;}}
  ul.lessons a:hover{{background:#faf8f2;}}
  ul.lessons .d{{flex:0 0 140px;font-size:0.82rem;color:#a39d8c;}}
  ul.lessons .t{{font-size:0.98rem;color:var(--heading);font-weight:600;
    line-height:1.45;}}
  ul.lessons a:hover .t{{text-decoration:underline;}}
  .foot{{margin-top:40px;font-size:0.8rem;color:#a39d8c;font-style:italic;
    line-height:1.7;}}
  @media (max-width:560px){{
    ul.lessons a{{flex-direction:column;gap:3px;}}
    ul.lessons .d{{flex:none;}}
  }}
</style>
</head>
<body>
<div class="wrap">

  <div class="meta-row">
    <span class="badge badge-date">{len(lessons)} Lektionen</span>
    <span class="badge badge-level">B1/B2 Niveau</span>
  </div>

  <h1>BSK70 – Deutsch täglich</h1>
  <p class="tagline">Lesen &middot; Wortschatz &middot; Übungen</p>
  <p class="intro">Jeden Morgen eine kurze Lektion auf B1/B2-Niveau: ein
  aktueller Lesetext, Schlüsselvokabular, nützliche Ausdrücke, ein wenig
  Grammatik und eine Mini-Übung. Alle Themen kommen aus aktuellen deutschen
  Nachrichten — Wirtschaft, Sport, Technik und Alltag in Deutschland.</p>

  <a class="dict" href="woerterbuch.html">
    <span class="label">Wörterbuch</span>
    <span class="dt">Alle Vokabeln an einem Ort</span>
    <span class="dd">Suchbar &middot; 6 Sprachen: English, Türkçe, Shqip,
    Українська, العربية, فارسی</span>
  </a>

  {latest_block}

  <span class="label">Archiv</span>
  {listing}

  <p class="foot">Die Lesetexte sind eigene Zusammenfassungen aktueller
  Nachrichtenmeldungen; die jeweilige Quelle steht am Ende jeder Lektion.</p>
</div>
</body>
</html>
"""

(OUT / "index.html").write_text(index, encoding="utf-8")

# regenerate the dictionary too, if its generator sits alongside this script
import subprocess
_here = Path(__file__).parent
for _helper in ("build_dict.py", "patch_vocab_lang.py", "patch_uebung.py"):
    _p = _here / _helper
    if _p.exists():
        subprocess.run([sys.executable, str(_p), str(OUT)], check=True)
print(f"{len(lessons)} lessons -> {OUT}")
