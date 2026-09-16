#!/usr/bin/env python3
"""Generate woerterbuch.html (the class dictionary) from vocab.json."""
import json, sys
from pathlib import Path

GEN = Path(__file__).parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else GEN
vocab = json.loads((GEN / "vocab.json").read_text(encoding="utf-8"))

LANGS = [
    ("en", "English",    "English",    0),
    ("tr", "Türkçe",     "Turkish",    0),
    ("sq", "Shqip",      "Albanian",   0),
    ("uk", "Українська", "Ukrainian",  0),
    ("ar", "العربية",     "Arabic",     1),
    ("fa", "فارسی",       "Persian",    1),
]
rtl = [c for c, _, _, r in LANGS if r]

rows = []
for e in vocab:
    tr = {c: e[c] for c, _, _, _ in LANGS}
    rows.append({"de": e["de"], "erk": e["erk"], "bsp": e["bsp"],
                 "n": len(e["dates"]), "t": tr})

payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
opts = "\n".join(
    f'      <option value="{c}"{" selected" if c=="en" else ""}>{native} — {eng}</option>'
    for c, native, eng, _ in LANGS)

html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wörterbuch — Deutsch täglich</title>
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
    color:var(--body-text);margin:0;padding:26px 24px 80px;}}
  .wrap{{max-width:980px;margin:0 auto;}}
  .back{{font-size:0.85rem;margin:0 0 16px;}}
  .back a{{color:#8c8778;text-decoration:none;}}
  .meta-row{{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:18px;}}
  .badge{{display:inline-block;padding:8px 16px;border-radius:999px;
    font-size:0.85rem;font-weight:600;}}
  .badge-date{{background:var(--badge-date-bg);color:var(--badge-date-text);}}
  .badge-level{{background:var(--badge-level-bg);color:var(--badge-level-text);}}
  h1{{font-size:1.55rem;font-weight:700;color:var(--heading);margin:0 0 8px;}}
  .intro{{font-size:0.97rem;line-height:1.7;color:#55514a;margin:0 0 20px;}}

  .controls{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;
    margin-bottom:8px;}}
  .controls input,.controls select{{
    font-family:inherit;font-size:0.9rem;color:var(--body-text);
    background:#fff;border:1px solid var(--border-soft);border-radius:999px;
    padding:10px 16px;outline:none;}}
  .controls input{{flex:1 1 240px;min-width:0;}}
  .controls input:focus,.controls select:focus{{border-color:#c9c0a6;}}
  .controls select{{cursor:pointer;font-weight:600;}}
  .count{{font-size:0.8rem;color:var(--label-grey);margin:0 0 14px;}}

  .card{{background:var(--card-bg);border-radius:20px;padding:22px 24px;}}
  table{{width:100%;border-collapse:collapse;font-size:0.93rem;}}
  th,td{{text-align:left;padding:11px 8px;border-bottom:1px solid #e9e3d2;
    vertical-align:top;}}
  th{{color:var(--label-grey);font-size:0.72rem;text-transform:uppercase;
    letter-spacing:.08em;font-weight:700;white-space:nowrap;}}
  tbody tr:last-child td{{border-bottom:none;}}
  td.de{{font-weight:600;color:var(--heading);width:22%;}}
  td.tr{{width:24%;}}
  td.erk{{color:#55514a;}}
  td.bsp{{color:#6b6558;font-style:italic;}}
  td[dir="rtl"]{{text-align:right;font-size:1rem;line-height:1.7;}}
  .reps{{display:inline-block;margin-left:6px;font-size:0.72rem;
    color:#a39d8c;font-weight:400;font-style:italic;}}
  .empty{{padding:28px 8px;color:var(--label-grey);text-align:center;}}
  .note{{margin-top:22px;font-size:0.8rem;color:#a39d8c;font-style:italic;
    line-height:1.75;}}

  @media (max-width:760px){{
    body{{padding:20px 12px 70px;}}
    .card{{padding:16px 14px;border-radius:16px;}}
    thead{{display:none;}}
    tbody tr{{display:block;padding:14px 2px;
      border-bottom:1px solid #e9e3d2;}}
    tbody tr:last-child{{border-bottom:none;}}
    td{{display:block;border:none;padding:2px 0;width:auto !important;}}
    td.de{{font-size:1.05rem;}}
    td.tr{{color:#3f6b3f;font-weight:600;}}
    td.erk,td.bsp{{font-size:0.9rem;}}
  }}
</style>
</head>
<body>
<div class="wrap">
  <p class="back"><a href="index.html">&larr; Alle Lektionen</a></p>

  <div class="meta-row">
    <span class="badge badge-date">{len(rows)} Wörter</span>
    <span class="badge badge-level">B1/B2 Niveau</span>
  </div>

  <h1>Wörterbuch</h1>
  <p class="intro">Alle Vokabeln aus den bisherigen Lektionen, alphabetisch
  geordnet. Wähle oben deine Sprache — die Übersetzungsspalte passt sich an
  und bleibt gespeichert. Erklärung und Beispielsatz bleiben auf Deutsch:
  Genau da passiert das Lernen.</p>

  <div class="controls">
    <input id="q" type="search" placeholder="Suchen … (Deutsch oder Übersetzung)"
           autocomplete="off">
    <select id="lang" aria-label="Sprache wählen">
{opts}
    </select>
  </div>
  <p class="count" id="count"></p>

  <div class="card">
    <table>
      <thead><tr>
        <th>Deutsch</th>
        <th id="thLang">English</th>
        <th>Einfache Erklärung</th>
        <th>Beispielsatz</th>
      </tr></thead>
      <tbody id="body"></tbody>
    </table>
  </div>

  <p class="note">Hinweis für den Unterricht: Die Übersetzungen wurden
  maschinell erstellt und sind noch nicht von Muttersprachlern geprüft.
  Erklärung und Beispielsatz auf Deutsch sind die verlässliche Grundlage —
  die Übersetzung ist nur eine erste Orientierung. Korrekturen sind
  willkommen.</p>
</div>

<script>
const DATA = {payload};
const RTL = {json.dumps(rtl)};
const LABEL = {json.dumps({c: native for c, native, _, _ in LANGS})};
const KEY = "dg-lang";

const body = document.getElementById("body");
const q = document.getElementById("q");
const sel = document.getElementById("lang");
const thLang = document.getElementById("thLang");
const count = document.getElementById("count");

function esc(s){{return s.replace(/[&<>"]/g, c =>
  ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}})[c]);}}

function render(){{
  const lang = sel.value;
  const isRtl = RTL.includes(lang);
  const term = q.value.trim().toLowerCase();
  thLang.textContent = LABEL[lang];

  const hits = DATA.filter(e =>
    !term ||
    e.de.toLowerCase().includes(term) ||
    (e.t[lang] || "").toLowerCase().includes(term) ||
    e.erk.toLowerCase().includes(term));

  body.innerHTML = hits.length ? hits.map(e => {{
    const reps = e.n > 1
      ? ` <span class="reps">${{e.n}}&times;</span>` : "";
    const tr = esc(e.t[lang] || "—");
    return `<tr>
      <td class="de">${{esc(e.de)}}${{reps}}</td>
      <td class="tr"${{isRtl ? ' dir="rtl" lang="' + lang + '"' : ""}}>${{tr}}</td>
      <td class="erk">${{esc(e.erk)}}</td>
      <td class="bsp">${{esc(e.bsp)}}</td>
    </tr>`;
  }}).join("") : `<tr><td colspan="4" class="empty">Keine Treffer.</td></tr>`;

  count.textContent = term
    ? `${{hits.length}} von ${{DATA.length}} Wörtern`
    : `${{DATA.length}} Wörter insgesamt`;
}}

try {{
  const saved = localStorage.getItem(KEY);
  if (saved && LABEL[saved]) sel.value = saved;
}} catch (e) {{}}

sel.addEventListener("change", () => {{
  try {{ localStorage.setItem(KEY, sel.value); }} catch (e) {{}}
  render();
}});
q.addEventListener("input", render);
render();
</script>
</body>
</html>
"""
(OUT / "woerterbuch.html").write_text(html, encoding="utf-8")
print(f"woerterbuch.html -> {OUT}  ({len(rows)} entries)")
