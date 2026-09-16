#!/usr/bin/env python3
"""Convert the early plain-Markdown lessons (2026-07-09..07-23) into the same
single-file HTML lesson format every other German_Lesson_*.html uses, so
build_site.py picks them up and they show up in the website archive.

Only touches lektionen/German_Lesson_*.md files that don't already have a
matching .html next to them (2026-07-24 exists as hand-authored HTML and is
left untouched).
"""
import re, sys
from pathlib import Path
from datetime import date

GEN = Path(__file__).parent
TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else GEN / "lektionen"

MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]
DAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag",
        "Samstag", "Sonntag"]


def inline(s):
    s = s.strip()
    s = re.sub(r"\*\(Wiederholung\)\*", '<span class="rep">(Wiederholung)</span>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    return s


def split_sections(text):
    return [p.strip() for p in re.split(r"\n-{3,}\n", text.strip())]


def parse_table(block):
    lines = [l for l in block.splitlines() if l.strip().startswith("|")]
    rows = []
    for l in lines[2:]:  # skip header row + |---|---| separator
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cells) == 4:
            rows.append([inline(c) for c in cells])
    return rows


def parse_bullets(block):
    return [inline(l.strip()[2:]) for l in block.splitlines() if l.strip().startswith("- ")]


def parse_numbered(block):
    items = []
    for l in block.splitlines():
        m = re.match(r"\s*\d+\.\s+(.*)", l)
        if m:
            items.append(inline(m.group(1)))
    return items


def parse_lesetext(block):
    hm = re.search(r"^###\s+(.+)$", block, re.M)
    headline = inline(hm.group(1)) if hm else ""
    paras = [inline(p) for p in re.split(r"\n\n+", block)
             if p.strip() and not p.strip().startswith("##")]
    return headline, paras


def parse_uebung(block):
    parts = re.split(r"(?m)^\*\*.+?\*\*\s*$", block)
    # parts[0] = leading "## 5. Mini-Übung" cruft, [1]=Verständnisfragen,
    # [2]=Schreibübung, [3]=Sprechübung
    verstaendnis = parse_numbered(parts[1]) if len(parts) > 1 else []
    schreib = parse_numbered(parts[2]) if len(parts) > 2 else []
    sprech = " ".join(l.strip() for l in parts[3].splitlines() if l.strip()) if len(parts) > 3 else ""
    return verstaendnis, schreib, inline(sprech)


def parse_quelle(block):
    if not block:
        return None
    m = re.search(r"Quelle:\s*(.+?)\*?\s*$", block, re.M)
    return inline(m.group(1)).rstrip("*").strip() if m else None


TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
  :root{{
    --page-bg:#ffffff;
    --card-bg:#f6f2e9;
    --badge-date-bg:#f3e6c8;
    --badge-date-text:#7a6535;
    --badge-level-bg:#e6f0e1;
    --badge-level-text:#3f6b3f;
    --label-grey:#9a9488;
    --heading:#1c1c1c;
    --body-text:#2c2c2a;
    --border-soft:#eae5d6;
    --tab-inactive-text:#8c8778;
    --tab-active-bg:#2c2c2a;
    --tab-active-text:#ffffff;
  }}
  *{{box-sizing:border-box;}}
  html{{font-size:14px;}}
  body{{
    font-family:"Segoe UI",Helvetica,Arial,sans-serif;
    background:var(--page-bg);
    color:var(--body-text);
    margin:0;
    padding:32px 24px 80px;
  }}
  .wrap{{max-width:760px;margin:0 auto;}}

  .meta-row{{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:22px;}}
  .badge{{display:inline-block;padding:8px 16px;border-radius:999px;font-size:0.85rem;font-weight:600;}}
  .badge-date{{background:var(--badge-date-bg);color:var(--badge-date-text);}}
  .badge-level{{background:var(--badge-level-bg);color:var(--badge-level-text);}}

  nav{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:28px;}}
  nav button{{
    border:1px solid var(--border-soft);
    background:#ffffff;
    color:var(--tab-inactive-text);
    border-radius:999px;
    padding:9px 16px;
    font-size:0.85rem;
    font-weight:600;
    cursor:pointer;
    transition:all .15s ease;
  }}
  nav button:hover{{border-color:#d8d2bf;}}
  nav button.active{{
    background:var(--tab-active-bg);
    color:var(--tab-active-text);
    border-color:var(--tab-active-bg);
  }}

  section.panel{{display:none;}}
  section.panel.active{{display:block;}}

  .label{{
    text-transform:uppercase;
    letter-spacing:.12em;
    font-size:0.78rem;
    color:var(--label-grey);
    font-weight:600;
    margin-bottom:8px;
  }}
  h2.heading{{font-size:1.5rem;font-weight:700;color:var(--heading);margin:0 0 20px 0;}}

  .card{{position:relative;background:var(--card-bg);border-radius:20px;padding:32px 34px;}}
  .card p{{font-size:1.02rem;line-height:1.75;margin:0 0 20px 0;}}
  .card p:last-child{{margin-bottom:0;}}

  .next-btn{{
    position:absolute;right:24px;bottom:-20px;width:44px;height:44px;
    border-radius:50%;background:#ffffff;border:1px solid var(--border-soft);
    box-shadow:0 4px 10px rgba(0,0,0,0.06);
    display:flex;align-items:center;justify-content:center;
    cursor:pointer;color:#8c8778;font-size:1.1rem;
  }}
  .next-btn:hover{{color:var(--heading);}}

  table{{width:100%;border-collapse:collapse;font-size:0.94rem;}}
  th,td{{text-align:left;padding:10px 8px;border-bottom:1px solid #e9e3d2;vertical-align:top;}}
  th{{color:var(--label-grey);font-size:0.72rem;text-transform:uppercase;letter-spacing:.08em;font-weight:700;}}
  td:first-child{{font-weight:600;color:var(--heading);}}
  tr:last-child td{{border-bottom:none;}}
  .rep{{font-style:italic;color:#a39d8c;font-weight:400;font-size:0.85em;}}

  ul.expr{{list-style:none;padding:0;margin:0;}}
  ul.expr li{{padding:14px 0;border-bottom:1px solid #e9e3d2;}}
  ul.expr li:last-child{{border-bottom:none;padding-bottom:0;}}
  ul.expr li b{{color:var(--heading);}}
  ul.expr li i{{color:#6b6558;}}

  .grammar-block{{margin-bottom:20px;}}
  .grammar-block:last-child{{margin-bottom:0;}}
  .grammar-block b{{color:var(--heading);}}

  .uebung-block{{margin-bottom:24px;}}
  .uebung-block:last-child{{margin-bottom:0;}}
  .uebung-block h3{{
    font-size:0.78rem;text-transform:uppercase;letter-spacing:.1em;
    color:var(--label-grey);font-weight:700;margin:0 0 12px 0;
  }}
  ol{{padding-left:20px;margin:0;}}
  ol li{{margin-bottom:8px;}}
  ol li:last-child{{margin-bottom:0;}}

  .source{{margin-top:34px;font-size:0.8rem;color:#a39d8c;font-style:italic;}}
</style>
</head>
<body>
<div class="wrap">

  <div class="meta-row">
    <span class="badge badge-date">{badge_date}</span>
    <span class="badge badge-level">B1/B2 Niveau</span>
  </div>

  <nav>
    <button data-tab="lese" class="active">Lesetext</button>
    <button data-tab="vokabular">Vokabular</button>
    <button data-tab="ausdruecke">Ausdrücke</button>
    <button data-tab="grammatik">Grammatik</button>
    <button data-tab="uebung">Übung</button>
  </nav>

  <section id="lese" class="panel active">
    <div class="label">Lesetext</div>
    <h2 class="heading">{headline}</h2>
    <div class="card">
      {lese_html}
      <div class="next-btn" onclick="goNext()">↓</div>
    </div>
  </section>

  <section id="vokabular" class="panel">
    <div class="label">Vokabular</div>
    <h2 class="heading">Schlüsselvokabular</h2>
    <div class="card">
      <table>
        <tr><th>Deutsch</th><th>Englisch</th><th>Einfache Erklärung</th><th>Beispielsatz</th></tr>
        {vocab_html}
      </table>
      <div class="next-btn" onclick="goNext()">↓</div>
    </div>
  </section>

  <section id="ausdruecke" class="panel">
    <div class="label">Ausdrücke</div>
    <h2 class="heading">Nützliche Ausdrücke</h2>
    <div class="card">
      <ul class="expr">
        {ausdruecke_html}
      </ul>
      <div class="next-btn" onclick="goNext()">↓</div>
    </div>
  </section>

  <section id="grammatik" class="panel">
    <div class="label">Grammatik</div>
    <h2 class="heading">Grammatikbewusstsein</h2>
    <div class="card">
      {grammar_html}
      <div class="next-btn" onclick="goNext()">↓</div>
    </div>
  </section>

  <section id="uebung" class="panel">
    <div class="label">Übung</div>
    <h2 class="heading">Mini-Übung</h2>
    <div class="card">
      <div class="uebung-block">
        <h3>Verständnisfragen</h3>
        <ol>
          {verstaendnis_html}
        </ol>
      </div>
      <div class="uebung-block">
        <h3>Schreibübungen</h3>
        <ol>
          {schreib_html}
        </ol>
      </div>
      <div class="uebung-block">
        <h3>Sprechanlass</h3>
        <p style="margin:0;">{sprech}</p>
      </div>
    </div>
  </section>
{source_html}</div>

<script>
  const tabOrder = ['lese','vokabular','ausdruecke','grammatik','uebung'];
  const buttons = document.querySelectorAll('nav button');
  const panels = document.querySelectorAll('section.panel');

  function activate(tabId){{
    buttons.forEach(b => b.classList.toggle('active', b.dataset.tab === tabId));
    panels.forEach(p => p.classList.toggle('active', p.id === tabId));
  }}
  buttons.forEach(btn => btn.addEventListener('click', () => activate(btn.dataset.tab)));

  function goNext(){{
    const current = document.querySelector('section.panel.active').id;
    const idx = tabOrder.indexOf(current);
    const next = tabOrder[(idx + 1) % tabOrder.length];
    activate(next);
    window.scrollTo({{top:0, behavior:'smooth'}});
  }}
</script>
</body>
</html>
"""


def convert(md_path: Path):
    html_path = md_path.with_suffix(".html")
    if html_path.exists():
        return "skip (html exists)"

    m = re.match(r"German_Lesson_(\d{4})-(\d{2})-(\d{2})", md_path.stem)
    if not m:
        return "skip (name)"
    y, mo, d = (int(x) for x in m.groups())
    dt = date(y, mo, d)

    text = md_path.read_text(encoding="utf-8")
    sections = split_sections(text)
    if len(sections) < 6:
        return f"skip (only {len(sections)} sections)"

    headline, lese_paras = parse_lesetext(sections[1])
    vocab_rows = parse_table(sections[2])
    ausdruecke = parse_bullets(sections[3])
    grammar_paras = [p for p in re.split(r"\n\n+", sections[4]) if p.strip() and not p.strip().startswith("##")]
    verstaendnis, schreib, sprech = parse_uebung(sections[5])
    quelle = parse_quelle(sections[6]) if len(sections) > 6 else None

    lese_html = "\n      ".join(f"<p>{p}</p>" for p in lese_paras)
    vocab_html = "\n        ".join(
        f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>" for r in vocab_rows)
    ausdruecke_html = "\n        ".join(f"<li>{a}</li>" for a in ausdruecke)
    grammar_html = "\n      ".join(f'<div class="grammar-block"><p>{inline(p)}</p></div>' for p in grammar_paras)
    verstaendnis_html = "\n          ".join(f"<li>{v}</li>" for v in verstaendnis)
    schreib_html = "\n          ".join(f"<li>{s}</li>" for s in schreib)
    source_html = f'  <p class="source">Quelle: {quelle}</p>\n' if quelle else ""

    html = TEMPLATE.format(
        title=f"Deutsch-Lektion — {dt.day}. {MONTHS[dt.month - 1]} {dt.year}",
        badge_date=f"{DAYS[dt.weekday()]}, {dt.day}. {MONTHS[dt.month - 1]} {dt.year}",
        headline=headline,
        lese_html=lese_html,
        vocab_html=vocab_html,
        ausdruecke_html=ausdruecke_html,
        grammar_html=grammar_html,
        verstaendnis_html=verstaendnis_html,
        schreib_html=schreib_html,
        sprech=sprech,
        source_html=source_html,
    )
    html_path.write_text(html, encoding="utf-8")
    return f"ok ({len(vocab_rows)} vocab, {len(ausdruecke)} ausdr., {len(verstaendnis)} q)"


results = {}
for f in sorted(TARGET.glob("German_Lesson_*.md")):
    results[f.name] = convert(f)
for k, v in results.items():
    print(f"  {k} -> {v}")
print(f"{sum(1 for v in results.values() if v.startswith('ok'))}/{len(results)} converted")
