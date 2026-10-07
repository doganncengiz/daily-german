# AGENTS.md — Daily German course site

Canonical project brief for AI coding agents working in this repo (Claude Code
and Codex both read this). If you're an agent: read this whole file before
editing anything. If either tool's understanding of the project drifts from
what's written here, fix this file, don't let a second copy diverge.

## What this project is

A static website for a B1/B2 German class of working adults in Germany, whose
first languages include English, Turkish, Albanian, Ukrainian, Arabic,
Persian, Spanish, French, and Italian. Each weekday there's a new "lesson":
a short reading text built from
current German news, plus vocabulary, useful phrases, grammar notes, and an
exercise. Students open the site, read the day's lesson, and work through the
exercise. There's also a searchable class-wide dictionary.

The public-facing course name is **BSK70 – Deutsch täglich**, with the tagline
**Lesen · Wortschatz · Übungen**.

The end goal (not yet fully reached — see Gaps below): every lesson page
should let a student read the text *and* do an exercise with instant
feedback, not just read.

## Status snapshot (2026-10-06)

- 80 lessons exist (2026-07-09 → 2026-10-07), all as HTML in `lektionen/`.
  The first 14 (07-09 → 07-23) started as plain `.md` and were backfilled
  into the standard HTML lesson format by `convert_md_lessons.py` — see
  Build pipeline. Both the `.md` source and the generated `.html` are kept.
- **27 lessons** (2026-09-10 → 2026-10-07) have a real exercise
  (multiple-choice + a "Lösungen" answers tab). The other 53 have five tabs
  but no graded exercise — see Gaps.
- `vocab.json` has 584 entries. Six target languages cover all 80 lessons;
  Spanish, French, and Italian begin with the 2026-09-17 lesson and continue
  forward. The July gap was closed on 2026-09-16 by adding 91 deduplicated
  entries with merged date arrays.
- A separate **Verben mit Präpositionen** reference contains 154 connections
  across 14 prepositions, with three examples per entry, search/filter tools,
  a shared-language dropdown (English only so far, see Data schemas below),
  and a mistake-weighted ten-question game with a saved best score and best
  streak. Its source data lives in `praepositionsverben.json`;
  `build_prep_verbs.py` generates the page.
- Existing translations are machine-generated and **not yet checked by
  native speakers**. `PROMPTS.md` has a ready-to-use ChatGPT prompt for a
  first-pass QA sweep.
- The site is live on GitHub Pages at
  `https://doganncengiz.github.io/daily-german/`. The public homepage, latest
  lesson, and dictionary were verified with HTTP 200 responses on 2026-09-16.
- A local git repository was initialized on 2026-09-16 and is connected to
  `https://github.com/doganncengiz/daily-german`. The Pages workflow at
  `.github/workflows/pages.yml` builds and publishes `website/` after every
  push to `main`.

## Two lesson formats (since 2026-09-19)

Which format a lesson uses depends on the weekday. The scheduled task's prompt
decides this first, before anything else.

**Monday–Friday — Tagesausgabe.** One topic, one reading text of 200–350 words,
5–10 vocabulary words (1–2 of them `(Wiederholung)`), 3–5 expressions,
1–2 grammar points, 3 multiple-choice questions, 3 writing tasks, 1 Sprechanlass.
This is the original format; every lesson up to 2026-09-18 uses it.

**Saturday and Sunday — Wochenend-Ausgabe.** A newspaper-style issue with three
short articles inside the `lese` panel, ~200–230 words each (~600–700 total),
in a fixed order: **Wirtschaft**, **Freizeit**, **Sport**. Each article sits in
its own `.card` with an `.art-kicker` (the section name) and an `.art-title`
(its own headline); the panel's single `<h2 class="heading">` is the issue
headline and is what the archive index shows. Then 12–14 vocabulary words
grouped by section with **one `(Wiederholung)` per section**, 5–6 expressions,
2 grammar points, 6 multiple-choice questions (two per article), 4 writing
tasks, 1 Sprechanlass. First examples: `German_Lesson_2026-09-19.html` and
`German_Lesson_2026-09-20.html`.

The weekend layout needs four extra CSS rules appended after the shared style
block — `.art-kicker`, `.art-title`, `.card + .card`, `th.group`. Everything
else (the `<style>` prefix, the whole `<script>`, the five source tabs, the
five-entry `tabOrder`, the single vocabulary table, the
`<h3>Verständnisfragen</h3>` + `<ol>` block) is identical to a weekday lesson,
because the patch scripts depend on all of it. In the weekend vocabulary table
the three groups are separated by `<tr><th class="group" colspan="4">Wirtschaft</th></tr>`
rows; `patch_vocab_lang.py` skips any row that is not four `<td>` cells, so
these pass through harmlessly.

## Read-aloud (lesson narration, added 2026-09-30)

Every `.card` inside `<section id="lese">` gets a custom player (one per
card — one for a weekday lesson, three for a weekend one, one per article):
accessible play/pause, -15s, +15s, a saved 0.75×/1×/1.25× speed control,
and an elapsed/total time readout, styled to match
the site's existing pill-button look (not the browser's native `<audio
controls>` widget — `patch_audio.py` hides the real `<audio>` element and
drives it from four buttons instead). Plays a pre-generated MP3 of that
card's paragraph text, read aloud in German.

**v1 was browser-based `window.speechSynthesis` (no files, but poor/uneven
quality and no punctuation-aware pacing). Replaced same-day** after hearing
the actual quality — too inconsistent across devices, didn't pause properly
at commas/periods. v2 uses a local neural TTS engine instead:

- **`generate_audio.py`** synthesizes one MP3 per Lesetext card using
  **Piper** (github.com/OHF-Voice/piper1-gpl), an open-source offline neural
  TTS engine. Genuinely free — no API key, no per-character cost, runs
  entirely on this machine. Output: `audio/<lesson-date>-<card-index>.mp3`
  (48kbps mono, via `lameenc` — no `ffmpeg` needed either).
- **Voice: `thorsten-high` by default**, confirmed by ear on 2026-09-30
  against 5 alternatives (a medium-quality Thorsten variant + 4 speakers
  from a 236-speaker multi-voice model) — stays the default because it's
  the only "high" quality-tier German voice available and clearly the most
  natural overall. `thorsten-emotional-medium` (same speaker, different
  model, lower quality tier) sounded more natural for *some* specific texts
  despite that, so it's available as a **per-lesson opt-in override**, not
  a wholesale switch: add `{"YYYY-MM-DD": "thorsten-emotional-medium"}` to
  `voice_overrides.json` (project root, git-tracked, `{}` by default) —
  applies to every card in that lesson. `VOICES` in `generate_audio.py` is
  the registry of known voices if a third one is ever added. Changes to a
  lesson's reading text, voice override, model, or synthesis settings are
  detected through `audio/manifest.json`; rerunning the generator rebuilds
  only the affected MP3s.
- It needs its own Python environment because piper-tts/lameenc are real
  dependencies, unlike every other script in this repo (stdlib-only by
  design): `.venv-audio/` (gitignored, created by
  `python3 -m venv .venv-audio && ./.venv-audio/bin/pip install piper-tts lameenc`).
  Run generation with `./.venv-audio/bin/python3 generate_audio.py`, **not**
  plain `python3`.
- First run downloads the ~114MB voice model into `.tts-voices/`
  (gitignored) automatically. Downloads are written atomically and verified
  against the SHA-256 checksums in `VOICES`. Piper's macOS wheel (1.8.0) has
  a packaging bug where its own bundled espeak-ng phoneme data fails to load in place;
  the fix is a *copy* of that data at `.tts-espeak-data/` (gitignored, also
  built automatically), pointed to via the `ESPEAK_DATA_PATH` env var. This
  was found by trial and error, not fully understood — if a future
  piper-tts release fixes the underlying bug, this workaround can go.
- **`audio/*.mp3` files and `audio/manifest.json` ARE committed** (unlike `.venv-audio/`,
  `.tts-voices/`, `.tts-espeak-data/`) — they're lesson content that took
  real local compute to produce, not reproducible tooling, same reasoning
  as committing `lektionen/*.html` rather than regenerating it from
  scratch each time.
- Generation is idempotent and incremental: it fingerprints normalized text,
  the selected voice, model checksum, and synthesis settings. It skips an MP3
  only when the stored fingerprint still matches, so edits automatically
  regenerate stale narration while unchanged files remain untouched
  (~15–25 seconds of local compute per changed card).
- `build_site.py` copies `audio/*.mp3` into `website/audio/` before running
  `patch_audio.py`, which only inserts a player for a card if that MP3
  already exists in the target — a lesson with no generated audio yet
  simply gets no player (same "best effort" pattern as `patch_uebung.py`
  and its `uebung_*.json` files). **So: after adding a new lesson, run
  `./.venv-audio/bin/python3 generate_audio.py` before `python3
  build_site.py`**, or the new lesson will publish without narration until
  the next time both are run.

`patch_audio.py` only touches `website/*.html` (like the other patch
scripts) — it does not modify `lektionen/` sources. It's idempotent (skips
files that already have a `.lese-player` element) — and since website/
lesson HTML is always freshly copied from `lektionen/` at the start of
every `build_site.py` run, a player-design change here takes effect on the
very next build with no extra step.

## Repository layout

```
lektionen/                      all source lesson files, see below
vocab.json                      master dictionary: vocab from all 80 lessons
praepositionsverben.json        154 verb/preposition entries imported from the teacher workbook
uebung_YYYY-MM-DD.json          exercise content for one lesson (27 exist so far)
build_site.py                   orchestrator: builds website/index.html + copies lessons, then calls the five scripts below
build_dict.py                   generates website/woerterbuch.html from vocab.json
build_prep_verbs.py             generates website/verben-mit-praepositionen.html (reference + 10-question game)
patch_vocab_lang.py             injects the language dropdown into each lesson's vocab table (mutates website/*.html)
patch_uebung.py                 converts a lesson's exercise into a/b/c multiple choice + adds a Lösungen tab (mutates website/*.html), only for lessons with a matching uebung_*.json
patch_audio.py                  inserts an <audio> player into every Lesetext card that has a matching audio/*.mp3 (mutates website/*.html) — see below
generate_audio.py               generates audio/<date>-<i>.mp3 lesson narration via local Piper TTS — needs .venv-audio/, see below
voice_overrides.json            {} by default — maps specific lesson dates to a non-default TTS voice, see below
audio/                          generated MP3 narration, one file per Lesetext card — COMMITTED (unlike website/), see below
audio/manifest.json             generated fingerprints that keep MP3 narration in sync with lesson text and voice settings — COMMITTED
convert_md_lessons.py           one-off/rerunnable: turns a lektionen/German_Lesson_*.md into the standard *.html format (see below)
website/                        GENERATED OUTPUT — this is what would be uploaded to a static host
PROMPTS.md                      ready-to-paste prompts: ChatGPT translation/text QA, Claude Design visual-design prompt
README.md                       short project/build/publishing overview for GitHub
.github/workflows/pages.yml     builds the site and deploys website/ to GitHub Pages
material/                       background reference only — NOT wired into the build, see below
```

### `lektionen/` — source lesson files

```
German_Lesson_YYYY-MM-DD.html   one per lesson, 71 total (2026-07-09 → 2026-09-29)
German_Lesson_YYYY-MM-DD.md     the 14 earliest lessons (07-09..07-23) in their original
                                 plain-Markdown form, kept alongside the .html generated
                                 from them — treat the .md as the source of truth for
                                 those dates; if you need to fix content, consider
                                 whether to edit the .md and reconvert, or edit the .html
                                 directly (simpler for a one-off fix, but drifts from the .md)
```
`build_site.py` reads lessons from `lektionen/` (falls back to the project
root if that folder doesn't exist, for backward compatibility). Everything
else — `vocab.json`, `uebung_*.json`, all the scripts — stays at the project
root.

### `material/` — the physical coursebook track (separate from the website pipeline)

This is a second, older material track that predates the daily-news-lesson
website and is **not currently connected to it** — nothing in `build_site.py`
reads from `material/`, and none of its vocabulary has been cross-checked
against `vocab.json`. Treat it as reference the teacher works from, not as
build input, unless the user explicitly asks to wire it in.

```
material/notizen/           BSK70_2026-07-16.docx, ...-07-20.docx, ...-07-21.docx
                             Teacher's own dated class notes: grammar points
                             (e.g. "demnach"/"zufolge" + dative, "denken an/über"),
                             short writing tasks, and answers to workbook
                             exercises (referenced as "KB 82", "KB 84" — page
                             numbers in the printed Kursbuch). Renamed from the
                             original "BSK70.docx" / "BSK70 (1).docx" / "BSK70
                             (2).docx" to carry the class date, matching the
                             German_Lesson_YYYY-MM-DD naming convention.
material/kursbuch-seiten/   17 photographed pages from the class's printed
                             coursebook (a B1/B2 workplace-German Kursbuch).
                             Mostly "Wortschatz" fill-in-the-blank vocabulary
                             pages (seen: pages 182, 272, 302, 303) organized
                             by Modul/topic (e.g. "Pendeln oder umziehen?",
                             "Das ist mir wichtig", "Mit freundlichen Grüßen"),
                             plus at least one "Schreibtraining" spread
                             (pages 288-289, formal workplace reports/Berichte).
                             Filenames are just capture timestamps — not yet
                             sorted or labeled by page number.
```

If the goal ever becomes "pull coursebook vocabulary into `vocab.json`" or
"turn a Kursbuch module into a lesson", that's new work (OCR/transcription +
a decision on how it merges with the news-lesson format), not something the
current build already does.

## Build pipeline

Run from the project root:

```
python3 build_site.py
```

### Git and deployment handoff

- GitHub repository: `https://github.com/doganncengiz/daily-german`
- Live site: `https://doganncengiz.github.io/daily-german/`
- `.github/workflows/pages.yml` rebuilds the source and deploys `website/`
  whenever `main` is pushed. Do not commit `website/`; it is ignored and
  regenerated in GitHub Actions.
- The user publishes through GitHub Desktop. HTTPS pushes from the terminal
  are not authenticated on this Mac and fail with a username/credential
  error. Do not replace the remote, create tokens, or alter authentication
  unless the user explicitly asks; make local commits and ask the user to
  click **Push origin** in GitHub Desktop.
- `material/` is intentionally gitignored because it contains local teaching
  references and photographed coursebook pages that should not be placed in
  the public repository.

This regenerates everything under `website/`:
1. Copies each `lektionen/German_Lesson_*.html` into `website/`, adding a
   mobile viewport tag and an "← Alle Lektionen" back link.
2. Copies `audio/*.mp3` into `website/audio/`, if the `audio/` folder exists.
3. Builds `website/index.html` (archive, newest first, grouped by month).
4. Calls `build_dict.py` → `website/woerterbuch.html`.
5. Calls `build_prep_verbs.py` → generates the searchable prepositional-verbs
   reference and its random ten-question game.
6. Calls `patch_vocab_lang.py` → adds the language dropdown to every lesson's
   vocab table in `website/`.
7. Calls `patch_uebung.py` → adds the MCQ exercise + Lösungen tab to any
   lesson in `website/` that has a matching `uebung_YYYY-MM-DD.json`.
8. Calls `patch_audio.py` → adds an `<audio>` player to every `.card` inside
   each lesson's `lese` panel that has a matching `audio/*.mp3`. See
   "Read-aloud" below — **you need to run `generate_audio.py` separately
   first**, this step only wires up files that already exist.

**Never hand-edit files inside `website/`.** They're regenerated from
scratch (well, mutated in place by the patch scripts) every run. Edit the
source in `lektionen/`, `vocab.json`, or `uebung_*.json`, then rerun
`build_site.py`. If you change a patch script's logic, delete and
re-copy the affected `website/*.html` first (the patch scripts are
idempotent-guarded — they check for a marker like `id="loesungen"` and skip
already-patched files — so re-running after a script change won't re-apply
your fix).

**`convert_md_lessons.py`** is separate from the main pipeline — it's what
turned the 14 early `.md` lessons into `.html`. It skips any `.md` that
already has a matching `.html` next to it, so it's safe to rerun; it only
does something if a new `.md`-only lesson shows up in `lektionen/` again.
Run it manually (`python3 convert_md_lessons.py`) before `build_site.py` if
that happens.

## Data schemas

**`vocab.json`** — flat array, one object per word/phrase:
```json
{
  "de": "abbilden",
  "en": "to reflect, to represent",
  "erk": "Etwas zeigt in Zahlen, wie die Realität aussieht.",
  "bsp": "Diese Kennzahl bildet den Aufwand nicht richtig ab.",
  "dates": ["2026-09-09"],
  "sq": "...", "tr": "...", "uk": "...", "ar": "...", "fa": "...",
  "es": "...", "fr": "...", "it": "..."
}
```
`dates` accumulates every lesson date the word appeared in (shown as an "n×"
badge in the dictionary). `erk` = simple German explanation, `bsp` = example
sentence. `sq/tr/uk/ar/fa` are Albanian/Turkish/Ukrainian/Arabic/Persian and
are required for every entry. `es/fr/it` are Spanish/French/Italian and are
required for entries used on or after 2026-09-17; older entries may omit them.

**`uebung_YYYY-MM-DD.json`** — one file per lesson with an exercise:
```json
{
  "mc": [ { "q": "...", "o": ["optA","optB","optC"], "c": 1, "why": "..." } ],
  "schreib": ["example sentence with <b>highlighted</b> pattern", "..."],
  "sprech": { "phrases": ["...", "..."], "modell": "model answer paragraph" }
}
```
`mc` = comprehension multiple-choice (`c` = index of correct option, `why` =
explanation shown after answering). `schreib` = model written sentences.
`sprech` = speaking-prompt phrases + one model answer.

**`praepositionsverben.json`** — flat array imported from the teacher's
`Preposition mit Verben.xlsx` workbook. Each entry stores the verb,
preposition and case, Präteritum, Perfekt, exactly three German examples, a
source sheet/row pointer, and two **per-language objects**:
```json
"meaning": {"en": "...", "tr": "", "sq": "", "uk": "", "ar": "", "fa": "", "es": "", "fr": "", "it": ""},
"explanation": {"en": "...", "tr": "", ...}
```
Same 9 language codes and the same shared `localStorage["dg-lang"]` key as
the dictionary and every lesson's vocab table (see Design system below) —
so a student's language choice carries over to this page automatically.
**Only "en" is populated as of 2026-10-07**; the page's JS falls back to
English for any entry/language that's still `""`, so it's correct today,
just English-only until the rest is translated. `PROMPTS.md` section 4 has
a ready-to-paste Codex prompt for that translation pass, matching the
pattern already used for `vocab.json` (section 3).

The generated page is searchable and grouped by preposition; its game picks
ten entries per round and its question-selection is **mistake-weighted**,
not purely random: `localStorage["dg-prep-mistakes"]` tracks a per-entry
miss count (keyed `verb|prep`), halved on a correct answer and incremented
on a wrong one, and entries with more past misses get proportionally more
likely to reappear (simple spaced repetition). Best score
(`localStorage["dg-prep-best"]`) and best streak-within-a-round
(`localStorage["dg-prep-best-streak"]`) are both tracked across sessions.

A content bug worth knowing about if you touch this data: `denken|an`,
`denken|über`, and `nachdenken|über` are three separate, legitimately
different entries (different meanings) — a prior AI-assisted import mixed
up a `denken|über` example sentence with `nachdenken`'s (the sentence used
the separable prefix "nach"); that one instance was fixed 2026-10-07, but
given this came from a bulk Excel import, there could be other
example/verb mismatches not yet caught — same caveat as the unreviewed
`vocab.json` translations.

## Design system / hard constraints

These are load-bearing — breaking any of them breaks the site for students on
phones or with screen readers. (Same list lives in `PROMPTS.md`'s Claude
Design prompt; keep both in sync if either changes.)

- **Every page is one self-contained HTML file.** Inline CSS and JS only. No
  external files, no CDN, no framework, no build step, no React/Tailwind.
  Plain HTML/CSS/vanilla JS — this is intentional so the whole thing is just
  a folder of files on a static host.
- **Must work on phones** — many students have no laptop. The vocab table
  collapses to stacked cards under 760px; preserve that breakpoint pattern
  for any new tabular content.
- **Arabic and Persian are RTL.** Translation cells in `ar`/`fa` carry
  `dir="rtl"` and stay right-aligned.
- **Language selection is shared via `localStorage["dg-lang"]`** across the
  dictionary page and every lesson's vocab table. Don't change this key or
  the mechanism. Lessons before 2026-09-17 expose the six fully backfilled
  languages; lessons from that date onward also expose Spanish, French, and
  Italian.
- **Tabs swap a CSS `active` class**, no page reload, no routing. Tab order
  is `['lese','vokabular','ausdruecke','grammatik','uebung']`, extended to
  `[...,'loesungen']` once `patch_uebung.py` has run on a lesson.
- **German stays the UI language everywhere.** Only the vocab meaning column
  (and the dictionary's translation column) switches language.
- Color tokens, font stack, and general visual tone (calm, editorial,
  cream cards `#f6f2e9` on white, no gradients/shadows) are documented in
  `PROMPTS.md` — treat that palette as fixed unless the user asks for a
  redesign.

## Gaps / open tasks

Roughly in priority order for reaching the "read + do an exercise" goal:

1. **53 of 80 lessons have no exercise.** Only 2026-09-10 through 2026-10-07
   have a `uebung_*.json`. Backfilling older lessons (or accepting that
   exercises start from Sep 10 onward) is an open decision, not made yet.
2. **584 existing vocab translations are unreviewed machine output.**
   `PROMPTS.md`'s ChatGPT prompt does a first pass in batches of 30-50; real
   reliability needs a native speaker per language, which hasn't happened yet.
3. **No automated verification.** Testing is manual: open the generated file
   in a browser. If you add JS logic (new exercise types etc.), sanity-check
   it in a real browser before calling it done.
4. **`material/` (coursebook photos + teacher's notes) isn't connected to
   the site at all.** It's unsorted (screenshots aren't labeled by page
   number) and untranscribed. Whether/how it should feed into `vocab.json`
   or become its own lesson track is an open question, not a plan yet.

## Working here — rules for both agents

- Treat this file as the shared source of truth. `CLAUDE.md` in this repo is
  just a pointer to this file — don't fork content into it.
- Edit sources, not `website/` output (see Build pipeline above).
- Keep the single-file-HTML-no-framework constraint even when adding new
  exercise types — follow the existing pattern (a small per-lesson JSON +
  a patch script), don't introduce a bundler or framework to do it.
- After any change to lesson content, vocab, or exercises, rerun
  `python3 build_site.py` and spot-check the relevant page in `website/`
  before considering the task done.
- After adding a new lesson, also run
  `./.venv-audio/bin/python3 generate_audio.py` (before `build_site.py`) so
  it gets narration too — it's a separate step on purpose, see "Read-aloud".
- If you're about to do something structural (restructure folders, change the
  hosting target, rewrite a build script's approach), check with the user
  first — this file documents current state, it doesn't pre-authorize
  architecture changes.

## Reference

`PROMPTS.md` — ready-to-paste prompts for: (1) ChatGPT translation/text QA
review of `vocab.json` and lesson texts, (2) a Claude Design prompt for
visual design work on the archive/dictionary/header, written with the same
hard constraints listed above baked in.
