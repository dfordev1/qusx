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
- **Mushaf mode** — each print layout uses its matching script face, laid out as a continuous flowing page (not per-verse boxes):
  - **Madani V1 / V2** — real KFGQPC per-page QCF glyph fonts (+ optional **Tajweed** COLRv1 on V2)
  - **Madani V4 Tajweed** — same V2 glyph codes with V4 colored fonts always on
  - **Qatar** — UthmanicHafs Unicode + Qatar page/line breaks
  - **IndoPak / Nastaleeq** — IndoPak or KFGQPC Nastaleeq Unicode + that edition's page/line breaks
- **Browse letters** — step through the recitation one letter at a time, each letter's own audio clip
- Word-tap-to-seek, word morphology tooltips (root/stem/lemma from QUSX), juz/hizb/rub/manzil/page/ruku/sajda milestones rendered as real break markers (not flat text labels), Bismillah headers, Makkan/Madinan tagging

## Data sources

| Source | What it provides | How it's used |
|---|---|---|
| **QUSX** (this repo) | Canonical Uthmani text, word morphology (root/stem/lemma), and the full milestone structure (juz/hizb/rub/manzil/ruku/page/line/sajda/ayah pins) per print layout | Fetched live per-surah from `raw.githubusercontent.com`, parsed client-side as the flat pin-stream it is — see `build_app.py`'s `loadSurah()` for the walking logic |
| [Qur'anic Universal Audio](https://huggingface.co/datasets/hetchyy/quranic-universal-ayahs) (QUA) | Phoneme-aligned audio + per-letter/per-word timestamps, 36 reciters | Fetched live via HF's `datasets-server` REST API, paginated in ≤100-row chunks |
| [Tarteel QUL](https://qul.tarteel.ai) / [Quran Foundation fonts](https://verses.quran.foundation/fonts/) | QPC V1/V2 glyph codes + QCF V1/V2/V4 page fonts; IndoPak / KFGQPC Nastaleeq Unicode faces | Mushaf mode script rendering (glyphs for Madani, Nastaleeq for IndoPak layouts) |

## Repo structure

```
index.html            The shipped app — self-contained, no build step. Open directly or serve as-is.
build_app.py           Python script that GENERATES index.html from a template. Edit this, not index.html directly.
surah_index.json       114-entry surah metadata (name, ayah count, revelation place, bismillah flag) — sourced from this repo's own per-surah XML root attributes
qpc_v2_glyphs.json     Per-word QPC V2 glyph codes (Tarteel QUL "QPC V2 Glyph - Word by Word")
qpc_v1_glyphs.json     Per-word QPC V1 glyph codes (from Quran.com API `code_v1`; regenerate with fetch_qpc_v1_glyphs.py)
fetch_qpc_v1_glyphs.py Regenerates qpc_v1_glyphs.json
reciters.json          The 36 reciter configs available in the QUA dataset, with display names
```

**To make a change:** edit `build_app.py`, then run `python3 build_app.py` — it regenerates `index.html` by embedding `surah_index.json`, glyph JSONs, and `reciters.json` directly into the page (so the shipped file has no external data dependencies beyond the three live APIs above).

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

- **Mushaf mode isn't pixel-identical to a printed mushaf.** Real mushaf justification (kashida — stretching letters to fill a line edge-to-edge) needs a dedicated shaping engine (e.g. DigitalKhatt); this app uses natural word spacing instead of naive CSS `justify`, which produced huge ugly gaps on short lines. Structure (real per-page/per-line breaks from QUSX, real KFGQPC glyphs on Madani layouts / Nastaleeq on IndoPak) is authentic; the fine typesetting isn't kashida-perfect. IndoPak layouts still use QUSX's Uthmani word text in a Nastaleeq face — not a separate IndoPak orthography corpus.
- **Letter-level highlighting doesn't work in Mushaf mode.** The QCF glyph fonts represent a whole word as a single precomposed character — there's no way to address individual letters within it. Letter mode uses a normal Unicode font (Scheherazade New) specifically so per-letter spans are possible.
- **Tajweed colors (COLRv1)** render natively in Chrome/Edge/Safari; Firefox falls back to plain (uncolored) glyph shapes. The Tajweed toggle applies on Madani V2; Madani V4 Tajweed layout is always colored.
- A handful of recordings contain genuine reciter retakes/repeats (verified against QUA's own `segments` field) — the app handles this correctly (repeats re-light the same on-screen word/letter rather than duplicating text), but it's worth knowing this exists in the underlying audio data.
