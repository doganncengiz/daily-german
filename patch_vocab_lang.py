#!/usr/bin/env python3
"""Add a language dropdown to each lesson's vocabulary table.

Only column 2 (the meaning) changes. Everything else stays German.
The choice is stored under the same key the dictionary page uses,
so picking a language once applies everywhere.
"""
import json, re, sys
from pathlib import Path
from html import unescape

GEN = Path(__file__).parent
vocab = {e["de"].lower(): e
         for e in json.loads((GEN / "vocab.json").read_text(encoding="utf-8"))}

# code -> (German column label, is_rtl)
LANGS = [
    ("en", "Englisch",   0),
    ("tr", "Türkisch",   0),
    ("sq", "Albanisch",  0),
    ("uk", "Ukrainisch", 0),
    ("ar", "Arabisch",   1),
    ("fa", "Persisch",   1),
]
NATIVE = {"en": "English", "tr": "Türkçe", "sq": "Shqip",
          "uk": "Українська", "ar": "العربية", "fa": "فارسی"}

SELECT_CSS = """
  .langbar{display:flex;justify-content:flex-end;margin:-6px 0 12px;}
  .langbar select{
    font-family:inherit;font-size:0.82rem;font-weight:600;
    color:#8c8778;background:#ffffff;
    border:1px solid var(--border-soft);border-radius:999px;
    padding:8px 14px;cursor:pointer;outline:none;}
  .langbar select:hover{border-color:#d8d2bf;}
  .langbar select:focus{border-color:#c9c0a6;}
  td.meaning[dir="rtl"]{text-align:right;font-size:1rem;}
"""

def clean(cell_html):
    s = re.sub(r'<span class="rep">.*?</span>', '', cell_html, flags=re.S)
    # Cross-reference/repetition notes are display annotations, not part of
    # the dictionary headword. Keep useful forms such as plurals in <i> tags.
    s = re.sub(r'<i>\((?:Wiederholung|verwandt:).*?</i>', '', s, flags=re.S)
    return unescape(re.sub(r"<[^>]+>", "", s)).strip()

def patch(path: Path):
    h = path.read_text(encoding="utf-8")
    if 'class="langbar"' in h:
        return "already"

    tm = re.search(r"(<table>)(.*?)(</table>)", h, re.S)
    if not tm:
        return "no table"
    table_inner = tm.group(2)

    rows = re.findall(r"<tr>.*?</tr>", table_inner, re.S)
    new_inner = table_inner
    data, idx, misses = [], 0, []

    for row in rows:
        if "<th>" in row:
            # tag the second header cell so we can relabel it
            new_row = re.sub(r"<th>Englisch</th>",
                             '<th id="thMeaning">Englisch</th>', row, count=1)
            new_inner = new_inner.replace(row, new_row, 1)
            continue
        cells = re.findall(r"<td>(.*?)</td>", row, re.S)
        if len(cells) != 4:
            continue
        de = clean(cells[0])
        entry = vocab.get(de.lower())
        if entry:
            data.append({c: entry[c] for c, _, _ in LANGS})
        else:
            misses.append(de)
            data.append({c: (cells[1] if c == "en" else "") for c, _, _ in LANGS})
        # tag the meaning cell
        new_row = row.replace(f"<td>{cells[1]}</td>",
                              f'<td class="meaning" data-i="{idx}">{cells[1]}</td>', 1)
        new_inner = new_inner.replace(row, new_row, 1)
        idx += 1

    h = h.replace(tm.group(0), tm.group(1) + new_inner + tm.group(3), 1)

    # dropdown, right-aligned just above the vocabulary card
    opts = "".join(
        f'<option value="{c}"{" selected" if c=="en" else ""}>'
        f'Deutsch &ndash; {NATIVE[c]}</option>' for c, _, _ in LANGS)
    bar = (f'<div class="langbar"><select id="vocabLang" '
           f'aria-label="Sprache der Bedeutung">{opts}</select></div>\n      ')
    h = h.replace('<h2 class="heading">Schlüsselvokabular</h2>\n    <div class="card">',
                  '<h2 class="heading">Schlüsselvokabular</h2>\n    '
                  + bar + '<div class="card">', 1)

    h = h.replace("</style>", SELECT_CSS + "</style>", 1)

    script = f"""
  // --- Vokabel-Sprache -------------------------------------------------
  const VOC = {json.dumps(data, ensure_ascii=False, separators=(",", ":"))};
  const VOC_LABEL = {json.dumps({c: lab for c, lab, _ in LANGS}, ensure_ascii=False)};
  const VOC_RTL = {json.dumps([c for c, _, r in LANGS if r])};
  const VOC_KEY = "dg-lang";
  const vocSel = document.getElementById('vocabLang');

  function applyVocabLang(){{
    const code = vocSel.value;
    const rtl = VOC_RTL.includes(code);
    document.getElementById('thMeaning').textContent = VOC_LABEL[code];
    document.querySelectorAll('td.meaning').forEach(td => {{
      const row = VOC[+td.dataset.i];
      td.textContent = (row && row[code]) ? row[code] : '\\u2014';
      if (rtl) {{ td.setAttribute('dir','rtl'); td.setAttribute('lang',code); }}
      else {{ td.removeAttribute('dir'); td.removeAttribute('lang'); }}
    }});
  }}
  try {{
    const s = localStorage.getItem(VOC_KEY);
    if (s && VOC_LABEL[s]) vocSel.value = s;
  }} catch(e) {{}}
  vocSel.addEventListener('change', () => {{
    try {{ localStorage.setItem(VOC_KEY, vocSel.value); }} catch(e) {{}}
    applyVocabLang();
  }});
  applyVocabLang();
"""
    h = h.replace("</script>", script + "</script>", 1)
    path.write_text(h, encoding="utf-8")
    return f"ok ({idx} rows" + (f", {len(misses)} unmatched: {misses}" if misses else "") + ")"

target = Path(sys.argv[1])
results = {}
for f in sorted(target.glob("German_Lesson_*.html")):
    results[f.name] = patch(f)
ok = sum(1 for v in results.values() if v.startswith("ok"))
print(f"patched {ok}/{len(results)} lessons")
for k, v in results.items():
    if not v.startswith("ok") or "unmatched" in v:
        print(" ", k, "->", v)
