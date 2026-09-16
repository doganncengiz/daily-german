#!/usr/bin/env python3
"""Turn Verständnisfragen into a/b/c multiple choice and add a Lösungen tab.

Only lessons that have a matching uebung_<date>.json file are touched.
"""
import json, re, sys
from pathlib import Path

GEN = Path(__file__).parent
LETTERS = "abc"

CSS = """
  .mcq{margin-bottom:22px;}
  .mcq:last-of-type{margin-bottom:0;}
  .mcq-q{font-size:1rem !important;font-weight:600;color:var(--heading);
    margin:0 0 10px 0 !important;line-height:1.5;}
  .opt{display:flex;gap:10px;align-items:flex-start;width:100%;text-align:left;
    font-family:inherit;font-size:0.95rem;line-height:1.5;color:var(--body-text);
    background:#fff;border:1px solid var(--border-soft);border-radius:12px;
    padding:11px 14px;margin-bottom:7px;cursor:pointer;transition:all .13s ease;}
  .opt:hover:not(.done){border-color:#d3cbb4;}
  .opt .ltr{flex:0 0 auto;font-weight:700;color:#a39d8c;
    text-transform:lowercase;}
  .opt.right{background:#e6f0e1;border-color:#cfe0c7;color:#3f6b3f;}
  .opt.right .ltr{color:#3f6b3f;}
  .opt.wrong{background:#f4e6e1;border-color:#e6d2ca;color:#8a4b3c;}
  .opt.wrong .ltr{color:#8a4b3c;}
  .opt.done{cursor:default;}
  .opt.dim{opacity:.55;}
  .mcq-fb{display:none;font-size:0.9rem;line-height:1.65;color:#55514a;
    margin:8px 0 0 0 !important;padding-left:4px;}
  .mcq-fb.show{display:block;}
  .mcq-fb b{color:var(--heading);}
  .sol{margin-bottom:18px;}
  .sol:last-child{margin-bottom:0;}
  .sol-n{font-weight:700;color:var(--heading);}
  .sol-a{color:#3f6b3f;font-weight:600;}
  .sol p{font-size:0.97rem !important;line-height:1.7;margin:0 0 6px 0 !important;}
  ul.redemittel{list-style:none;padding:0;margin:0 0 16px 0;}
  ul.redemittel li{padding:7px 0;border-bottom:1px solid #e9e3d2;
    font-size:0.95rem;color:#55514a;}
  ul.redemittel li:last-child{border-bottom:none;}
  .modell{background:#fffdf8;border-radius:14px;padding:16px 18px;
    font-size:0.97rem;line-height:1.75;color:#45413a;}
  .modell b{color:var(--heading);}
  .hint{font-style:italic;color:#a39d8c;font-size:0.85em;font-weight:400;}
  ol.schreibliste li{margin-bottom:10px;line-height:1.6;}
"""

def build_mc(mc):
    out = []
    for i, q in enumerate(mc):
        opts = "".join(
            f'<button class="opt" data-o="{j}">'
            f'<span class="ltr">{LETTERS[j]})</span><span>{o}</span></button>'
            for j, o in enumerate(q["o"]))
        out.append(
            f'<div class="mcq" data-c="{q["c"]}">'
            f'<p class="mcq-q">{i+1}. {q["q"]}</p>{opts}'
            f'<p class="mcq-fb">{q["why"]}</p></div>')
    return "\n          ".join(out)

def build_loesungen(d):
    ans = []
    for i, q in enumerate(d["mc"]):
        c = q["c"]
        ans.append(
            f'<div class="sol"><p><span class="sol-n">{i+1}.</span> {q["q"]}</p>'
            f'<p><span class="sol-a">{LETTERS[c]}) {q["o"][c]}</span></p>'
            f'<p>{q["why"]}</p></div>')
    saetze = "".join(f"<li>{s}</li>" for s in d["schreib"])
    phrases = "".join(f"<li>{p}</li>" for p in d["sprech"]["phrases"])
    return f"""
  <section id="loesungen" class="panel">
    <div class="label">Lösungen</div>
    <h2 class="heading">Lösungen &amp; Beispiele</h2>
    <div class="card">
      <div class="uebung-block">
        <h3>Verständnisfragen</h3>
        {"".join(ans)}
      </div>
      <div class="uebung-block">
        <h3>Gute Beispielsätze</h3>
        <ol class="schreibliste">{saetze}</ol>
      </div>
      <div class="uebung-block">
        <h3>Sprechanlass — Redemittel</h3>
        <ul class="redemittel">{phrases}</ul>
        <h3>Modellantwort</h3>
        <div class="modell">{d["sprech"]["modell"]}</div>
      </div>
      <div class="next-btn" onclick="goNext()">↓</div>
    </div>
  </section>
"""

JS = """
  // --- Multiple Choice -------------------------------------------------
  document.querySelectorAll('.mcq').forEach(box => {
    const correct = +box.dataset.c;
    const opts = [...box.querySelectorAll('.opt')];
    const fb = box.querySelector('.mcq-fb');
    opts.forEach(btn => btn.addEventListener('click', () => {
      if (opts.some(o => o.classList.contains('done'))) return;
      const picked = +btn.dataset.o;
      opts.forEach((o, j) => {
        o.classList.add('done');
        if (j === correct) o.classList.add('right');
        else if (j === picked) o.classList.add('wrong');
        else o.classList.add('dim');
      });
      fb.classList.add('show');
    }));
  });
"""

def patch(path: Path, data: dict):
    h = path.read_text(encoding="utf-8")
    if 'id="loesungen"' in h:
        return "already"

    # 1. replace the Verständnisfragen list with a/b/c blocks
    m = re.search(
        r'(<h3>Verständnisfragen</h3>\s*)<ol>.*?</ol>', h, re.S)
    if not m:
        return "no Verständnisfragen block"
    h = h[:m.start()] + m.group(1) + build_mc(data["mc"]) + h[m.end():]

    # 2. nav button
    h = h.replace(
        '<button data-tab="uebung">Übung</button>',
        '<button data-tab="uebung">Übung</button>\n'
        '    <button data-tab="loesungen">Lösungen</button>', 1)

    # 3. give the Übung card a next-button if it lacks one
    ue = re.search(r'<section id="uebung".*?</section>', h, re.S).group(0)
    if 'next-btn' not in ue:
        new_ue = ue.replace("    </div>\n  </section>",
                            '      <div class="next-btn" onclick="goNext()">↓</div>\n'
                            "    </div>\n  </section>")
        if new_ue == ue:  # fallback: insert before the final closing div
            idx = ue.rstrip().rfind("</div>")
            idx = ue.rstrip().rfind("</div>", 0, idx)
            new_ue = ue[:idx] + '  <div class="next-btn" onclick="goNext()">↓</div>\n      ' + ue[idx:]
        h = h.replace(ue, new_ue, 1)

    # 4. Lösungen section, right after the Übung section
    ue = re.search(r'<section id="uebung".*?</section>', h, re.S).group(0)
    h = h.replace(ue, ue + build_loesungen(data), 1)

    # 5. tab order + css + js
    h = h.replace("const tabOrder = ['lese','vokabular','ausdruecke','grammatik','uebung'];",
                  "const tabOrder = ['lese','vokabular','ausdruecke','grammatik','uebung','loesungen'];", 1)
    h = h.replace("</style>", CSS + "</style>", 1)
    h = h.replace("</script>", JS + "</script>", 1)
    path.write_text(h, encoding="utf-8")
    return "ok"

target = Path(sys.argv[1])
done = 0
for f in sorted(GEN.glob("uebung_*.json")):
    date = f.stem.replace("uebung_", "")
    lesson = target / f"German_Lesson_{date}.html"
    if not lesson.exists():
        print("  missing lesson:", lesson.name); continue
    r = patch(lesson, json.loads(f.read_text(encoding="utf-8")))
    print(f"  {lesson.name} -> {r}")
    done += r == "ok"
print(f"Übung+Lösungen: {done} lessons")
