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

Keeps `audio/manifest.json` with a fingerprint of each card's normalized text,
selected voice, model, and synthesis settings. Reruns skip matching MP3s and
automatically regenerate only narration whose inputs changed. On the first run
after this manifest feature was introduced, existing MP3s are adopted without
being regenerated; subsequent runs verify them through their fingerprints.

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
import hashlib
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
MANIFEST_FILE = AUDIO_OUT / "manifest.json"
MANIFEST_VERSION = 1
SENTENCE_SILENCE = 0.35
MP3_BIT_RATE = 48
MP3_QUALITY = 2

VOICES = {
    "thorsten-high": {
        "file": "de_DE-thorsten-high.onnx",
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx",
        "sha256": "9df1c43c61149ef9b39e618e2b861fbe41e1fcea9390b2dac62e8761573ea4f1",
        "config_sha256": "6de734444e4c3f9e33b7ebe2746dbc19b71e85f613e79c65acf623200b99a76a",
        "sample_rate": 22050,
        "speaker": None,
    },
    "thorsten-emotional-medium": {
        "file": "de_DE-thorsten_emotional-medium.onnx",
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten_emotional/medium/de_DE-thorsten_emotional-medium.onnx",
        "sha256": "c1764e652266cd6dcebf1b95c61973df5970a5f5272e94b655ff1ddf9a99d1ff",
        "config_sha256": "92895b9e99f7cfc13f4a9879da615c3d6e0baa4d660e26d7b685abdd27a6d1d3",
        "sample_rate": 22050,
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ensure_voice(voice_key: str):
    VOICE_DIR.mkdir(exist_ok=True)
    voice = VOICES[voice_key]
    for suffix in ("", ".json"):
        name = voice["file"] + suffix
        dest = VOICE_DIR / name
        expected = voice["config_sha256"] if suffix else voice["sha256"]
        if dest.exists() and sha256_file(dest) == expected:
            continue
        if dest.exists():
            print(f"Checksum mismatch for {name}; downloading a clean copy ...")
        else:
            print(f"Downloading {name} (one-time) ...")
        temp = dest.with_name(dest.name + ".download")
        temp.unlink(missing_ok=True)
        try:
            subprocess.run(
                ["curl", "-fL", "--retry", "3", "-o", str(temp), voice["url"] + suffix],
                check=True,
            )
            actual = sha256_file(temp)
            if actual != expected:
                sys.exit(
                    f"Checksum mismatch after downloading {name}:\n"
                    f"  expected {expected}\n  received {actual}"
                )
            temp.replace(dest)
        finally:
            temp.unlink(missing_ok=True)


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
        str(SENTENCE_SILENCE),
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
    enc.set_bit_rate(MP3_BIT_RATE)
    enc.set_in_sample_rate(voice["sample_rate"])
    enc.set_channels(1)
    enc.set_quality(MP3_QUALITY)
    mp3 = enc.encode(proc.stdout) + enc.flush()
    temp = out_mp3.with_name(out_mp3.name + ".tmp")
    try:
        temp.write_bytes(mp3)
        temp.replace(out_mp3)
    finally:
        temp.unlink(missing_ok=True)


def audio_fingerprint(text: str, voice_key: str) -> str:
    """Hash every input that can materially change the generated narration."""
    voice = VOICES[voice_key]
    payload = {
        "text": text,
        "voice": voice_key,
        "model_sha256": voice["sha256"],
        "speaker": voice["speaker"],
        "sample_rate": voice["sample_rate"],
        "sentence_silence": SENTENCE_SILENCE,
        "mp3_bit_rate": MP3_BIT_RATE,
        "mp3_quality": MP3_QUALITY,
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_manifest() -> tuple[dict, bool]:
    """Return (entries, first_run). Existing MP3s are adopted on first run."""
    if not MANIFEST_FILE.exists():
        return {}, True
    data = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    if data.get("version") != MANIFEST_VERSION or not isinstance(data.get("files"), dict):
        sys.exit(
            f"Unsupported or invalid audio manifest: {MANIFEST_FILE}. "
            "Remove it and rerun to adopt the current MP3 files."
        )
    return data["files"], False


def save_manifest(entries: dict):
    data = {"version": MANIFEST_VERSION, "files": dict(sorted(entries.items()))}
    temp = MANIFEST_FILE.with_name(MANIFEST_FILE.name + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(MANIFEST_FILE)


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
    manifest, first_run = load_manifest()
    current_files = set()

    generated = regenerated = skipped = adopted = 0
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
            current_files.add(out.name)
            fingerprint = audio_fingerprint(text, voice_key)
            entry = manifest.get(out.name)
            if out.exists() and entry and entry.get("fingerprint") == fingerprint:
                skipped += 1
                continue
            if first_run and out.exists():
                manifest[out.name] = {"fingerprint": fingerprint, "voice": voice_key}
                adopted += 1
                continue
            action = "regenerating" if out.exists() else "generating"
            print(
                f"  {action} {out.name} ({len(text)} chars, voice={voice_key}) ...",
                flush=True,
            )
            synth(text, out, voice_key)
            manifest[out.name] = {"fingerprint": fingerprint, "voice": voice_key}
            if action == "regenerating":
                regenerated += 1
            else:
                generated += 1

    manifest = {name: entry for name, entry in manifest.items() if name in current_files}
    save_manifest(manifest)
    print(
        f"audio: {generated} generated, {regenerated} regenerated, "
        f"{skipped} unchanged, {adopted} adopted -> {AUDIO_OUT}"
    )


if __name__ == "__main__":
    main()
