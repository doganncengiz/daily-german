# Daily German

A static B1/B2 German course website for working adults. Each lesson combines
a current-affairs reading text with vocabulary, useful phrases, grammar notes,
and—where available—an interactive exercise.

## Build locally

```sh
python3 build_site.py
```

The command generates the deployable site in `website/`. Do not edit files in
that directory directly; edit the source lessons, vocabulary, exercises, or
build scripts and rebuild.

## Publishing

Pushing the `main` branch to GitHub runs `.github/workflows/pages.yml`. The
workflow rebuilds the site and publishes the generated `website/` directory to
GitHub Pages.

Translations are AI-generated and have not yet been fully reviewed by native
speakers.
