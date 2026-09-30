#!/usr/bin/env python3
"""Add a free, browser-based "Vorlesen" (read-aloud) button to the Lesetext
panel of every lesson, using the Web Speech API (window.speechSynthesis).

No audio files, no API keys, no build step beyond this script — the browser's
own German voice reads the text aloud. Quality/availability of that voice
varies by device, which is the accepted tradeoff for a zero-cost v1.

One button per `.card` inside <section id="lese">: weekday lessons have one
card (one button), weekend lessons have three (one per article). The button
is inserted right before each card's first <p>, so it sits above the
paragraphs and below any article kicker/title.

Only touches website/*.html (build output), same as the other patch_*.py
scripts. Skips files that already have a `.tts-btn` (idempotent, safe to
rerun).
"""
import json
import re
import sys
from html import unescape
from pathlib import Path

CSS = """
  .tts-btn{
    display:inline-flex;align-items:center;gap:6px;
    border:1px solid var(--border-soft);background:#ffffff;
    color:var(--tab-inactive-text);border-radius:999px;
    padding:8px 14px;font-size:0.82rem;font-weight:600;
    cursor:pointer;margin:0 0 16px 0;transition:all .15s ease;
  }
  .tts-btn:hover{border-color:#d8d2bf;color:var(--heading);}
  .tts-btn.playing{background:var(--tab-active-bg);color:var(--tab-active-text);border-color:var(--tab-active-bg);}
"""

JS_TEMPLATE = """
  // --- Vorlesen (Web Speech API, kostenlos, geraeteabhaengig) ----------
  const TTS_TEXTS = %s;
  let ttsPlayingIndex = null;

  function ttsPickVoice(){
    const voices = window.speechSynthesis.getVoices();
    return voices.find(v => v.lang && v.lang.toLowerCase().startsWith('de')) || null;
  }

  function ttsReset(){
    document.querySelectorAll('.tts-btn').forEach(b => {
      b.classList.remove('playing');
      b.textContent = '\\ud83d\\udd0a Vorlesen';
    });
    ttsPlayingIndex = null;
  }

  function toggleSpeech(i){
    if (!('speechSynthesis' in window)) {
      alert('Vorlesen wird von diesem Browser leider nicht unterstuetzt.');
      return;
    }
    const wasPlaying = ttsPlayingIndex === i;
    window.speechSynthesis.cancel();
    if (wasPlaying) { ttsReset(); return; }

    const u = new SpeechSynthesisUtterance(TTS_TEXTS[i]);
    u.lang = 'de-DE';
    const voice = ttsPickVoice();
    if (voice) u.voice = voice;
    u.rate = 0.95;
    u.onend = ttsReset;
    u.onerror = ttsReset;

    ttsReset();
    ttsPlayingIndex = i;
    const btn = document.querySelector('.tts-btn[data-i="' + i + '"]');
    if (btn) { btn.classList.add('playing'); btn.textContent = '\\u23f8 Stop'; }
    window.speechSynthesis.speak(u);
  }

  window.addEventListener('pagehide', () => {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  });
"""


def extract_text(card_html: str) -> str:
    paras = re.findall(r"<p>(.*?)</p>", card_html, re.S)
    joined = " ".join(paras)
    joined = re.sub(r"<[^>]+>", " ", joined)
    joined = unescape(joined)
    return re.sub(r"\s+", " ", joined).strip()


def button_html(i: int) -> str:
    return f'<button class="tts-btn" type="button" data-i="{i}" onclick="toggleSpeech({i})">🔊 Vorlesen</button>\n      '


def patch_lese_section(html: str) -> tuple[str, list[str]]:
    m = re.search(r'(<section id="lese"[^>]*>)(.*?)(</section>)', html, re.S)
    if not m:
        return html, []

    inner = m.group(2)
    parts = re.split(r'(<div class="card">)', inner)
    # parts[0] is the preamble (label + h2.heading); then alternating
    # marker/content pairs, one pair per card.
    texts = []
    rebuilt = [parts[0]]
    i = 1
    card_index = 0
    while i < len(parts):
        marker = parts[i]
        content = parts[i + 1] if i + 1 < len(parts) else ""
        p_pos = content.find("<p>")
        if p_pos == -1:
            rebuilt.append(marker + content)
        else:
            rebuilt.append(marker + content[:p_pos] + button_html(card_index) + content[p_pos:])
            texts.append(extract_text(content))
            card_index += 1
        i += 2

    new_inner = "".join(rebuilt)
    new_html = html[: m.start(2)] + new_inner + html[m.end(2):]
    return new_html, texts


def patch(path: Path) -> str:
    html = path.read_text(encoding="utf-8")
    if 'class="tts-btn"' in html:
        return "already"

    new_html, texts = patch_lese_section(html)
    if not texts:
        return "no lese card found"

    new_html = new_html.replace("</style>", CSS + "</style>", 1)
    js = JS_TEMPLATE % json.dumps(texts, ensure_ascii=False)
    new_html = new_html.replace("</script>", js + "</script>", 1)

    path.write_text(new_html, encoding="utf-8")
    return f"ok ({len(texts)} card(s))"


target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
results = {}
for f in sorted(target.glob("German_Lesson_*.html")):
    results[f.name] = patch(f)
ok = sum(1 for v in results.values() if v.startswith("ok"))
print(f"Vorlesen: {ok}/{len(results)} lessons")
for k, v in results.items():
    if not v.startswith("ok") and v != "already":
        print(" ", k, "->", v)
