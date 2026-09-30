#!/usr/bin/env python3
"""Add a custom audio player (play/pause, -15s, +15s, saved playback speed,
elapsed/total time) to each card in the Lesetext panel, pointing at the pre-generated MP3
narration for that card (see generate_audio.py).

One player per `.card` inside <section id="lese">: weekday lessons have one
card (one player), weekend lessons have three (one per article). The player
is inserted right before each card's first <p>, so it sits above the
paragraphs and below any article kicker/title.

Only inserts a player for a card if the matching audio/<date>-<i>.mp3
already exists in the target dir (copied there by build_site.py from the
project's audio/ folder) — a lesson with no generated audio yet just gets no
player, same "best effort" pattern as patch_uebung.py's exercises.

Only touches website/*.html (build output), same as the other patch_*.py
scripts. Skips files that already have a `.lese-player` element (idempotent,
safe to rerun) — but since website/ lesson HTML is always freshly copied
from lektionen/ at the start of every build_site.py run, a changed player
design here takes effect on the very next build without any extra step.
"""
import re
import sys
from pathlib import Path

CSS = """
  .lese-player{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin:0 0 16px 0;}
  .lese-player audio{display:none;}
  .lp-btn{
    border:1px solid var(--border-soft);background:#ffffff;
    color:var(--tab-inactive-text);border-radius:999px;
    width:36px;height:36px;flex:0 0 auto;
    display:flex;align-items:center;justify-content:center;
    font-size:0.95rem;cursor:pointer;transition:all .15s ease;
  }
  .lp-btn:hover{border-color:#d8d2bf;color:var(--heading);}
  .lp-btn:focus-visible{outline:2px solid var(--badge-date-text);outline-offset:2px;}
  .lp-btn:disabled{opacity:.45;cursor:not-allowed;}
  .lp-play{
    width:auto;min-width:94px;height:42px;padding:0 14px;gap:7px;font-size:.86rem;
    background:var(--tab-active-bg);color:var(--tab-active-text);
    border-color:var(--tab-active-bg);
  }
  .lp-play:hover{color:var(--tab-active-text);}
  .lp-play-icon{font-size:1rem;line-height:1;}
  .lp-seek{width:44px;font-size:.78rem;font-weight:700;}
  .lp-rate{width:48px;font-size:.78rem;font-weight:700;}
  .lp-time{
    font-size:0.78rem;color:var(--label-grey);
    font-variant-numeric:tabular-nums;margin-left:2px;
  }
"""

JS = """
  // --- Lesetext-Player (Audio, -15s/+15s) -------------------------------
  const LP_RATE_KEY = 'dg-audio-rate';
  const LP_RATES = [1, 0.75, 1.25];
  let lpRate = 1;
  try {
    const savedRate = Number(localStorage.getItem(LP_RATE_KEY));
    if (LP_RATES.includes(savedRate)) lpRate = savedRate;
  } catch (e) {}

  function lpFormat(s){
    if (!isFinite(s) || s < 0) return '0:00';
    s = Math.round(s);
    return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
  }

  function lpApplyRate(rate){
    lpRate = rate;
    document.querySelectorAll('.lese-player').forEach(player => {
      const playerAudio = player.querySelector('audio');
      const rateBtn = player.querySelector('.lp-rate');
      playerAudio.playbackRate = rate;
      playerAudio.defaultPlaybackRate = rate;
      if ('preservesPitch' in playerAudio) playerAudio.preservesPitch = true;
      rateBtn.textContent = String(rate).replace('.', ',') + '×';
      rateBtn.setAttribute(
        'aria-label', 'Geschwindigkeit: ' + String(rate).replace('.', ',') + '-fach'
      );
    });
    try { localStorage.setItem(LP_RATE_KEY, String(rate)); } catch (e) {}
  }

  document.querySelectorAll('.lese-player').forEach(wrap => {
    const audio = wrap.querySelector('audio');
    const playBtn = wrap.querySelector('.lp-play');
    const playIcon = wrap.querySelector('.lp-play-icon');
    const playText = wrap.querySelector('.lp-play-text');
    const backBtn = wrap.querySelector('.lp-back');
    const fwdBtn = wrap.querySelector('.lp-fwd');
    const rateBtn = wrap.querySelector('.lp-rate');
    const timeEl = wrap.querySelector('.lp-time');

    function setPlaying(playing){
      playIcon.textContent = playing ? '⏸' : '▶';
      playText.textContent = playing ? 'Pause' : 'Vorlesen';
      playBtn.setAttribute('aria-label', playing ? 'Pausieren' : 'Abspielen');
      playBtn.setAttribute('aria-pressed', String(playing));
    }
    function updateTime(){
      timeEl.textContent = lpFormat(audio.currentTime) + ' / ' + lpFormat(audio.duration);
    }
    function updateSeekButtons(){
      const ready = Number.isFinite(audio.duration);
      backBtn.disabled = !ready;
      fwdBtn.disabled = !ready;
    }
    audio.addEventListener('loadedmetadata', () => {
      updateTime();
      updateSeekButtons();
      lpApplyRate(lpRate);
    });
    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('play', () => { setPlaying(true); });
    audio.addEventListener('pause', () => { setPlaying(false); });
    audio.addEventListener('ended', () => { setPlaying(false); });

    playBtn.addEventListener('click', () => {
      document.querySelectorAll('.lese-player audio').forEach(a => {
        if (a !== audio) a.pause();
      });
      if (audio.paused) {
        const started = audio.play();
        if (started) started.catch(() => setPlaying(false));
      } else {
        audio.pause();
      }
    });
    backBtn.addEventListener('click', () => {
      if (!Number.isFinite(audio.duration)) return;
      audio.currentTime = Math.max(0, audio.currentTime - 15);
    });
    fwdBtn.addEventListener('click', () => {
      if (!Number.isFinite(audio.duration)) return;
      audio.currentTime = Math.min(audio.duration, audio.currentTime + 15);
    });
    rateBtn.addEventListener('click', () => {
      const index = LP_RATES.indexOf(lpRate);
      lpApplyRate(LP_RATES[(index + 1) % LP_RATES.length]);
    });

    setPlaying(false);
    updateSeekButtons();
    updateTime();
  });
  lpApplyRate(lpRate);
"""


def player_html(date_str: str, i: int) -> str:
    src = f"audio/{date_str}-{i}.mp3"
    return (
        f'<div class="lese-player">'
        f'<audio class="lese-audio" preload="metadata" src="{src}">'
        "Dein Browser unterstützt das Audio-Element nicht.</audio>"
        f'<button class="lp-btn lp-seek lp-back" type="button" aria-label="15 Sekunden zurück" disabled>−15</button>'
        f'<button class="lp-btn lp-play" type="button" aria-label="Abspielen" aria-pressed="false">'
        f'<span class="lp-play-icon" aria-hidden="true">▶</span>'
        f'<span class="lp-play-text">Vorlesen</span></button>'
        f'<button class="lp-btn lp-seek lp-fwd" type="button" aria-label="15 Sekunden vor" disabled>+15</button>'
        f'<button class="lp-btn lp-rate" type="button" aria-label="Geschwindigkeit: 1-fach">1×</button>'
        f'<span class="lp-time" aria-live="off">0:00 / 0:00</span>'
        f'</div>\n      '
    )


def patch_lese_section(html: str, date_str: str, audio_dir: Path) -> tuple[str, int]:
    m = re.search(r'(<section id="lese"[^>]*>)(.*?)(</section>)', html, re.S)
    if not m:
        return html, 0

    inner = m.group(2)
    parts = re.split(r'(<div class="card">)', inner)
    rebuilt = [parts[0]]
    i = 1
    card_index = 0
    added = 0
    while i < len(parts):
        marker = parts[i]
        content = parts[i + 1] if i + 1 < len(parts) else ""
        p_pos = content.find("<p>")
        has_audio = (audio_dir / f"{date_str}-{card_index}.mp3").exists()
        if p_pos == -1 or not has_audio:
            rebuilt.append(marker + content)
        else:
            rebuilt.append(
                marker + content[:p_pos] + player_html(date_str, card_index) + content[p_pos:]
            )
            added += 1
        if p_pos != -1:
            card_index += 1
        i += 2

    new_inner = "".join(rebuilt)
    new_html = html[: m.start(2)] + new_inner + html[m.end(2):]
    return new_html, added


def patch(path: Path, audio_dir: Path) -> str:
    html = path.read_text(encoding="utf-8")
    if 'class="lese-player"' in html:
        return "already"

    m = re.match(r"German_Lesson_(\d{4}-\d{2}-\d{2})", path.stem)
    if not m:
        return "skip (name)"
    date_str = m.group(1)

    new_html, added = patch_lese_section(html, date_str, audio_dir)
    if not added:
        return "no audio yet"

    new_html = new_html.replace("</style>", CSS + "</style>", 1)
    new_html = new_html.replace("</script>", JS + "</script>", 1)
    path.write_text(new_html, encoding="utf-8")
    return f"ok ({added} player(s))"


target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
audio_dir = target / "audio"
results = {}
for f in sorted(target.glob("German_Lesson_*.html")):
    results[f.name] = patch(f, audio_dir)
ok = sum(1 for v in results.values() if v.startswith("ok"))
no_audio = sum(1 for v in results.values() if v == "no audio yet")
print(f"Vorlesen (audio): {ok}/{len(results)} lessons ({no_audio} without generated audio yet)")
