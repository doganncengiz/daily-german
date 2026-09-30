# BSK70 – Deutsch täglich

A static B1/B2 German course website for working adults. Each lesson combines
a current-affairs reading text with vocabulary, useful phrases, grammar notes,
and—where available—an interactive exercise. Each reading text also has
audio narration, generated locally with a free neural TTS engine (Piper).

## Build locally

```sh
python3 build_site.py
```

The command generates the deployable site in `website/`. Do not edit files in
that directory directly; edit the source lessons, vocabulary, exercises, or
build scripts and rebuild.

## Generating lesson audio

```sh
python3 -m venv .venv-audio  # once
./.venv-audio/bin/pip install piper-tts lameenc  # once
./.venv-audio/bin/python3 generate_audio.py
```

Run this before `build_site.py` whenever a new lesson is added. It's
incremental — already-generated files are skipped — and free (runs fully
offline, no API key). See AGENTS.md's "Read-aloud" section for details.

## Publishing

Pushing the `main` branch to GitHub runs `.github/workflows/pages.yml`. The
workflow rebuilds the site and publishes the generated `website/` directory to
GitHub Pages.

Translations are AI-generated and have not yet been fully reviewed by native
speakers.
