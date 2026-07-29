# Qur'an Follow-Along

A single-file, no-build-step web app for reading and listening to the Qur'an with
letter/word-level highlighting synced to audio — built on top of **QUSX** (this
repo's own canonical text, morphology, and milestone structure) plus two other
open datasets.

**[Live demo](https://dfordev1.github.io/qusx/)** *(once GitHub Pages is enabled — see below)*

## What it does

- Browse all 114 surahs, any of 36 reciters, with live audio + phoneme-level timing
- **Letter mode** — every letter lights up as it's recited, with word-level highlighting layered inside it
- **Word mode** — the currently-recited word highlights as a whole
- **Mushaf mode** — real KFGQPC V2 calligraphic glyphs, laid out as a continuous flowing page exactly like a printed mushaf (not per-verse boxes), with an optional **Tajweed** color toggle (QCF V4 COLRv1 font)
- **Browse letters** — step through the recitation one letter at a time, each letter's own audio clip
- Word-tap-to-seek, word morphology tooltips (root/stem/lemma from QUSX), juz/hizb/rub/manzil/page/ruku/sajda milestones rendered as real break markers (not flat text labels), Bismillah headers, Makkan/Madinan tagging

## Data sources

| Source | What it provides | How it's used |
|---|---|---|
| **QUSX** (this repo) | Canonical Uthmani text, word morphology (root/stem/lemma), and the full milestone structure (juz/hizb/rub/manzil/ruku/page/line/sajda/ayah pins) | Fetched live per-surah from `raw.githubusercontent.com`, parsed client-side as the flat pin-stream it is — see `build_app.py`'s `loadSurah()` for the walking logic |
| [Qur'anic Universal Audio](https://huggingface.co/datasets/hetchyy/quranic-universal-ayahs) (QUA) | Phoneme-aligned audio + per-letter/per-word timestamps, 36 reciters | Fetched live via HF's `datasets-server` REST API, paginated in ≤100-row chunks |
| [Tarteel QUL](https://qul.tarteel.ai) | QPC V2 per-word glyph codes (`qpc_v2_glyphs.json`, bundled — see below) + the QCF V2/V4 mushaf font files (loaded live from Quran Foundation's open font CDN) | Mushaf mode's glyph rendering + tajweed coloring |

## Repo structure

```
index.html            The shipped app — self-contained, no build step. Open directly or serve as-is.
build_app.py           Python script that GENERATES index.html from a template. Edit this, not index.html directly.
surah_index.json       114-entry surah metadata (name, ayah count, revelation place, bismillah flag) — sourced from this repo's own per-surah XML root attributes
qpc_v2_glyphs.json     Per-word QPC V2 glyph codes for the whole Qur'an, from Tarteel QUL's "QPC V2 Glyph - Word by Word" resource (gated behind a free QUL account — bundled here so the app doesn't need to re-fetch it)
reciters.json          The 36 reciter configs available in the QUA dataset, with display names
```

**To make a change:** edit `build_app.py`, then run `python3 build_app.py` — it regenerates `index.html` by embedding `surah_index.json`, `qpc_v2_glyphs.json`, and `reciters.json` directly into the page (so the shipped file has no external data dependencies beyond the three live APIs above).

## Running it

No build step, no server required for local use — just open `index.html` directly in a browser. It needs real internet access (it live-fetches audio/timing from HF, text/morphology from this repo's raw GitHub content, and mushaf fonts from Quran Foundation's CDN), so a sandboxed/offline preview won't work.

To regenerate after editing `build_app.py`:
```bash
python3 build_app.py
# writes index.html
```

## Enabling the GitHub Pages live demo

1. Push this branch (or merge it) so `index.html` is at the repo root of whichever branch Pages serves.
2. In the repo: **Settings → Pages → Build and deployment → Source: Deploy from a branch**, pick this branch and `/ (root)`.
3. Save — GitHub publishes it at `https://dfordev1.github.io/qusx/` within a minute or two.

## Known limitations (documented, not silently hidden)

- **Mushaf mode isn't pixel-identical to a printed mushaf.** Real mushaf justification (kashida — stretching letters to fill a line edge-to-edge) needs a dedicated shaping engine (e.g. DigitalKhatt); this app uses natural word spacing instead of naive CSS `justify`, which produced huge ugly gaps on short lines. Structure (real per-page/per-line breaks from QUSX, real KFGQPC glyphs) is authentic; the fine typesetting isn't kashida-perfect.
- **Letter-level highlighting doesn't work in Mushaf mode.** The QCF glyph fonts represent a whole word as a single precomposed character — there's no way to address individual letters within it. Letter mode uses a normal Unicode font (QPC "Uthmanic Hafs") specifically so per-letter spans are possible.
- **Tajweed colors (COLRv1)** render natively in Chrome/Edge/Safari; Firefox falls back to plain (uncolored) glyph shapes.
- A handful of recordings contain genuine reciter retakes/repeats (verified against QUA's own `segments` field) — the app handles this correctly (repeats re-light the same on-screen word/letter rather than duplicating text), but it's worth knowing this exists in the underlying audio data.
