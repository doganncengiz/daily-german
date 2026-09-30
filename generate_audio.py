#!/usr/bin/env python3
"""Generate per-card MP3 narration for each lesson's Lesetext, using a local
neural TTS engine (Piper, https://github.com/OHF-Voice/piper1-gpl) — free,
offline, no API key, no per-lesson cost.

Run with the dedicated venv (has piper-tts + lameenc installed; created by
`python3 -m venv .venv-audio && ./.venv-audio/bin/pip install piper-tts lameenc`
if it doesn't exist yet):

    ./.venv-audio/bin/python3 generate_audio.py

First run downloads the ~114MB German voice model ("Thorsten", high quality)
into .tts-voices/ if it isn't already there. Writes one MP3 per card in each
lesson's `lese` panel to audio/<date>-<card-index>.mp3, e.g.
audio/2026-09-24-0.mp3 for a weekday lesson (one card) or
audio/2026-09-19-0.mp3 / -1.mp3 / -2.mp3 for a weekend one (three articles).

Skips any <date>-<i>.mp3 that already exists, so reruns after adding new
lessons only generate the new files — safe and cheap to rerun. This also
means: if you change a date's voice in voice_overrides.json AFTER its MP3s
already exist, you must delete those MP3s yourself before rerunning, or the
old file is kept as-is (the script has no way to know the existing file was
made with a different voice).

Voice: "thorsten-high" (VOICES/DEFAULT_VOICE below) is used for every
lesson by default. voice_overrides.json (project root, git-tracked, `{}` by
default) can map specific lesson dates to a different voice, e.g.
`{"2026-10-03": "thorsten-emotional-medium"}` — picked per lesson (all of
that lesson's cards use it), not per card. Confirmed by ear on 2026-09-30:
thorsten-high stays the default (best overall fidelity); thorsten-emotional
-medium sounds more natural for some texts despite being lower quality tier,
hence the override rather than a wholesale switch.

Why the ESPEAK_DATA_PATH workaround: the piper-tts wheel on PyPI (as of
1.8.0) has a packaging bug on macOS — its bundled espeak-ng phoneme data
doesn't load from its own installed location, but a *copy* of that same
data elsewhere, pointed to via the ESPEAK_DATA_PATH env var, works. This
was confirmed by hand; the workaround is mechanical, not well understood.
If a future piper-tts release fixes this, ensure_espeak_data() and the env
var can be dropped.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from html import unescape
from pathlib import Path

GEN = Path(__file__).parent
LEKTIONEN = GEN / "lektionen"
AUDIO_OUT = GEN / "audio"
VOICE_DIR = GEN / ".tts-voices"
ESPEAK_DATA = GEN / ".tts-espeak-data"
OVERRIDES_FILE = GEN / "voice_overrides.json"

VOICES = {
    "thorsten-high": {
        "file": "de_DE-thorsten-high.onnx",
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx",
        "speaker": None,
    },
    "thorsten-emotional-medium": {
        "file": "de_DE-thorsten_emotional-medium.onnx",
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten_emotional/medium/de_DE-thorsten_emotional-medium.onnx",
        "speaker": 0,  # the Thorsten-emotional speaker heard and approved 2026-09-30
    },
}
DEFAULT_VOICE = "thorsten-high"


def ensure_venv():
    if "piper" not in sys.modules:
        try:
            import piper  # noqa: F401
        except ImportError:
            sys.exit(
                "piper-tts is not installed in this Python.\n"
                "Run with the project's audio venv instead:\n"
                "  python3 -m venv .venv-audio  # if it doesn't exist yet\n"
                "  ./.venv-audio/bin/pip install piper-tts lameenc\n"
                "  ./.venv-audio/bin/python3 generate_audio.py"
            )


def ensure_voice(voice_key: str):
    VOICE_DIR.mkdir(exist_ok=True)
    voice = VOICES[voice_key]
    for suffix in ("", ".json"):
        name = voice["file"] + suffix
        dest = VOICE_DIR / name
        if not dest.exists():
            print(f"Downloading {name} (one-time) ...")
            subprocess.run(
                ["curl", "-sL", "-o", str(dest), voice["url"] + suffix], check=True
            )


def ensure_espeak_data():
    if (ESPEAK_DATA / "phontab").exists():
        return
    import piper

    src = Path(piper.__file__).parent / "espeak-ng-data"
    shutil.copytree(src, ESPEAK_DATA, dirs_exist_ok=True)


def extract_card_texts(html: str) -> list[str]:
    m = re.search(r'<section id="lese"[^>]*>(.*?)</section>', html, re.S)
    if not m:
        return []
    inner = m.group(1)
    cards = re.split(r'<div class="card">', inner)[1:]
    texts = []
    for card in cards:
        paras = re.findall(r"<p>(.*?)</p>", card, re.S)
        joined = " ".join(paras)
        joined = re.sub(r"<[^>]+>", " ", joined)
        joined = unescape(joined)
        texts.append(re.sub(r"\s+", " ", joined).strip())
    return texts


def synth(text: str, out_mp3: Path, voice_key: str):
    import lameenc

    voice = VOICES[voice_key]
    piper_bin = Path(sys.executable).parent / "piper"
    env = {**os.environ, "ESPEAK_DATA_PATH": str(ESPEAK_DATA)}
    cmd = [
        str(piper_bin),
        "-m",
        str(VOICE_DIR / voice["file"]),
        "--sentence-silence",
        "0.35",
        "--output-raw",
    ]
    if voice["speaker"] is not None:
        cmd += ["--speaker", str(voice["speaker"])]
    proc = subprocess.run(
        cmd,
        input=text.encode("utf-8"),
        capture_output=True,
        env=env,
        check=True,
    )
    enc = lameenc.Encoder()
    enc.set_bit_rate(48)
    enc.set_in_sample_rate(22050)
    enc.set_channels(1)
    enc.set_quality(2)
    mp3 = enc.encode(proc.stdout) + enc.flush()
    out_mp3.write_bytes(mp3)


def load_overrides() -> dict:
    if not OVERRIDES_FILE.exists():
        return {}
    overrides = json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
    unknown = set(overrides.values()) - set(VOICES)
    if unknown:
        sys.exit(f"voice_overrides.json names unknown voice(s): {unknown}. Known: {list(VOICES)}")
    return overrides


def main():
    ensure_venv()
    overrides = load_overrides()
    needed_voices = {DEFAULT_VOICE, *overrides.values()}
    for key in needed_voices:
        ensure_voice(key)
    ensure_espeak_data()
    AUDIO_OUT.mkdir(exist_ok=True)

    generated = skipped = 0
    for f in sorted(LEKTIONEN.glob("German_Lesson_*.html")):
        m = re.match(r"German_Lesson_(\d{4}-\d{2}-\d{2})", f.stem)
        if not m:
            continue
        date_str = m.group(1)
        voice_key = overrides.get(date_str, DEFAULT_VOICE)
        html = f.read_text(encoding="utf-8")
        for i, text in enumerate(extract_card_texts(html)):
            if not text:
                continue
            out = AUDIO_OUT / f"{date_str}-{i}.mp3"
            if out.exists():
                skipped += 1
                continue
            print(f"  {out.name} ({len(text)} chars, voice={voice_key}) ...", flush=True)
            synth(text, out, voice_key)
            generated += 1

    print(f"audio: {generated} generated, {skipped} already existed -> {AUDIO_OUT}")


if __name__ == "__main__":
    main()
