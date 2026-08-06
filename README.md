# Qur'an Follow-Along

A single-file, no-build-step web app for reading and listening to the Qur'an with
letter/word-level highlighting synced to audio — built on top of **QUSX** (canonical
text, morphology, and milestone structure from [usxv2](https://github.com/dfordev1/usxv2))
plus open audio and mushaf glyph datasets.

**[Live demo](https://dfordev1.github.io/qusx/)** *(once GitHub Pages is enabled — see below)*

## What it does

- Browse by **surah** or **juz**, with live audio + word/letter timing
- **Letter mode** — soft glow on the current letter; light wash on the active word
- **Word mode** — light boxed highlight on the recited word
- **Mushaf mode** — each print layout uses its matching script face, laid out as continuous mushaf pages:
  - **Madani V1 / V2** — KFGQPC per-page QCF glyph fonts (+ optional **Tajweed** COLRv1 on V2)
  - **Madani V4 Tajweed** — V2 glyph codes with V4 colored fonts always on
  - **Qatar** — UthmanicHafs Unicode + Qatar page/line breaks
  - **IndoPak / Nastaleeq** — IndoPak or KFGQPC Nastaleeq Unicode + that edition's page/line breaks
- **Page-by-page** mushaf browse (crosses surah/juz boundaries) or scroll-all pages
- **Resume last read** — surah/ayah/time restored after refresh
- **Playback speed** — 0.75× / 1× / 1.25×
- **Follow scroll** — keep the recited word above the player, or only scroll when off-screen
- Grammar hover/click panels (root/lemma/stem + spoken gloss) — **off by default**
- **Browse letters** — step one letter at a time with its own clip
- Compact chrome (surah/juz + theme; reciter/layout/font/pages under ⋯)
- Word-tap-to-seek; juz/hizb/rub/manzil/page/ruku/sajda milestones from QUSX

### Optional: Al-Hadr local alignments

When served with a local `local_alhadr/` pack (manifest + juz `.ogg` audio), the app
can use **Al-Hadr** word alignments offline, with Archive.org as a remote fallback.
That pack is **not** shipped in this repo (too large); keep it beside the app when
developing locally.

## Data sources

| Source | What it provides | How it's used |
|---|---|---|
| **QUSX** ([usxv2](https://github.com/dfordev1/usxv2)) | Canonical Uthmani text, word morphology (root/stem/lemma), milestone structure per print layout | Fetched live per-surah from `raw.githubusercontent.com` |
| [Qur'anic Universal Audio](https://huggingface.co/datasets/hetchyy/quranic-universal-ayahs) (QUA) | Phoneme-aligned audio + timings, 36 reciters | Fetched live via HF `datasets-server` |
| [Tarteel QUL](https://qul.tarteel.ai) / [Quran Foundation fonts](https://verses.quran.foundation/fonts/) | QPC V1/V2 glyphs + QCF page fonts; Nastaleeq faces | Mushaf mode script rendering |
| Al-Hadr (optional local) | Juz opus/ogg + word alignments | Offline follow-along when `local_alhadr/` is present |

## Repo structure

```
index.html            The shipped app — self-contained. Open or serve as-is.
build_app.py          GENERATES index.html — edit this, then rebuild.
surah_index.json      114-entry surah metadata
qpc_v2_glyphs.json    Per-word QPC V2 glyph codes
qpc_v1_glyphs.json    Per-word QPC V1 glyph codes
fetch_qpc_v1_glyphs.py Regenerates qpc_v1_glyphs.json
reciters.json         QUA reciter configs + display names
tradition_diffs.json  Ayah-count diffs across numbering traditions (display-only)
```

**To make a change:** edit `build_app.py`, then run `python build_app.py` — it regenerates
`index.html` by embedding the JSON data files.

## Running it

```bash
python build_app.py   # regenerate index.html after edits
python -m http.server 8765   # recommended (local Al-Hadr + CORS-friendly)
# open http://127.0.0.1:8765/
```

Opening `index.html` as a file works for the online QUA path; local Al-Hadr audio
needs HTTP. The app also needs network access for QUSX XML, fonts, and (unless
fully local) audio.

## Enabling the GitHub Pages live demo

1. Push/merge so `index.html` is at the repo root of the branch Pages serves.
2. **Settings → Pages → Deploy from a branch**, pick that branch and `/ (root)`.
3. Demo: `https://dfordev1.github.io/qusx/`

## Known limitations

- **Mushaf mode isn't pixel-identical to a printed mushaf** (no full kashida engine).
- **Letter-level highlighting doesn't work in Mushaf mode** (QCF = one glyph per word).
- **Tajweed COLRv1** — Chrome/Edge/Safari; Firefox falls back to plain glyphs.
- **Al-Hadr pack** is incomplete for some juz (e.g. 24 / 30 gaps in the alignment release).
- Some QUA recordings contain reciter retakes; the app re-lights the same on-screen word.
