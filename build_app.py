import json
import os

_DIR = os.path.dirname(os.path.abspath(__file__))

surah_index = json.load(open(os.path.join(_DIR, 'surah_index.json'), encoding='utf-8'))  # 114 entries: num, name, nameArabic, ayahCount
surah_index_json = json.dumps(surah_index, ensure_ascii=False)

# QPC V2 glyph data (Tarteel QUL, "QPC V2 Glyph - Word by Word"): for each
# surah:ayah, an array of per-word glyph characters in the KFGQPC V2 mushaf
# font's private-use-area encoding — position N is QUSX word position N,
# and the trailing extra entry (beyond QUSX's real word count) is the
# ornamental ayah-end number glyph baked into the font itself, matching a
# real mushaf page rather than our own drawn ayah-pin circle.
glyph_v2_json = open(os.path.join(_DIR, 'qpc_v2_glyphs.json'), encoding='utf-8').read()

# All 36 reciter configs available in the QUA dataset (hetchyy/quranic-
# universal-ayahs), with a readable display name for each — the raw HF
# config slugs are source-tagged machine names (e.g. "..._mp3quran",
# "..._tarteel", "..._qdc"), not meant for display.
reciters = json.load(open(os.path.join(_DIR, 'reciters.json'), encoding='utf-8'))
reciters_json = json.dumps(reciters, ensure_ascii=False)

# Per-surah ayah-count deltas across qira'at/riwayah numbering traditions
# (Warsh, Qalun, Ad-Duri, Shu'bah — QUSX's "pilot" traditions; see usxv2's
# data/diff-report.json), only for the 55 surahs where a tradition's count
# actually differs from Hafs/Kufi. QUSX's own pilot text/audio isn't
# synced to this app's Hafs-indexed recitation timing, so this is a
# display-only numbering comparison, not a full alternate-tradition read.
tradition_diffs = json.load(open(os.path.join(_DIR, 'tradition_diffs.json'), encoding='utf-8'))
tradition_diffs_json = json.dumps(tradition_diffs, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Qur'an Follow-Along — Letter Highlighting</title>
<script>
  // Applied before first paint so there's no dark-then-light flash: an
  // explicit prior choice (localStorage) wins, otherwise fall back to the
  // OS-level prefers-color-scheme, defaulting to dark if neither is set.
  (function () {
    var saved = localStorage.getItem('quran-theme');
    var theme = saved || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    document.documentElement.setAttribute('data-theme', theme);
  })();
</script>
<style>
  :root {
    --bg: #0c0e13;
    --surface: #171b24;
    --surface-2: #1d222d;
    --border: #2b3140;
    --text: #ece9e2;
    --text-muted: #838a9c;
    --accent: #e8bf3f;
    --accent-2: #d99a3d;
    --accent-soft: rgba(232, 191, 63, 0.16);
    --shadow: 0 10px 30px rgba(0,0,0,0.35);
    --bg-glow: rgba(232,191,63,0.06);
  }
  /* Light theme: same accent hue, flipped surfaces/text — applied via
     data-theme on <html> (see the theme-toggle script near the bottom),
     never via prefers-color-scheme alone, so the user's explicit choice
     (stored in localStorage) always wins over the OS setting. */
  :root[data-theme="light"] {
    --bg: #f7f4ec;
    --surface: #ffffff;
    --surface-2: #f1ede2;
    --border: #ded6c2;
    --text: #241f14;
    --text-muted: #7a7360;
    --accent: #b8862a;
    --accent-2: #9c6f22;
    --accent-soft: rgba(184, 134, 42, 0.14);
    --shadow: 0 10px 30px rgba(36,31,20,0.10);
    --bg-glow: rgba(184,134,42,0.08);
  }
  /* The real Uthmani Quranic script (QPC "Uthmanic Hafs"), NOT the QCF
     glyph-per-word mushaf font used in Mushaf mode — this is a normal
     Unicode font (one file, full cmap + contextual joining), so it's the
     right choice for Letter/Word modes where text still needs to be
     split into individual per-letter spans for highlighting. The QCF
     glyph fonts can't do that: each of their "characters" IS an entire
     precomposed word, with no individual letters to select. */
  @font-face {
    font-family: 'UthmanicHafs';
    src: url('https://verses.quran.foundation/fonts/quran/hafs/uthmanic_hafs/UthmanicHafs1Ver18.woff2') format('woff2');
    font-display: swap;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background:
      radial-gradient(ellipse 900px 500px at 50% -10%, var(--bg-glow), transparent),
      var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 28px 16px 140px;
    transition: background-color 0.2s, color 0.2s;
  }
  h1 {
    font-size: 17px;
    font-weight: 600;
    letter-spacing: 0.14em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin: 0 0 4px;
    background: linear-gradient(90deg, var(--text-muted), var(--accent), var(--text-muted));
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .subtitle { color: var(--text-muted); font-size: 13px; margin-bottom: 28px; text-align: center;}
  .subtitle a { color: var(--accent); text-decoration: none; }
  .verses {
    width: 100%;
    max-width: 760px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .verse {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 24px;
    box-shadow: var(--shadow);
    transition: border-color 0.2s, transform 0.15s;
    cursor: pointer;
    direction: rtl;
  }
  .verse:hover { transform: translateY(-1px); }
  .verse.active { border-color: var(--accent); }
  .verse-num {
    display: inline-block;
    font-size: 11px;
    color: var(--text-muted);
    font-family: monospace;
    margin-bottom: 10px;
    direction: ltr;
  }

  /* QUSX milestone-pin styling — matches usxv2/viewer/viewer.html's own
     visual convention (a rule + label marking where a boundary axis
     actually falls, and an inline circular pin for the ayah marker) rather
     than a flat text label bolted onto the verse number. juz/hizb/rub/page
     are boundary axes, not per-ayah facts, so they render as BREAKS between
     verses (only when the value actually changes), not repeated on every
     single verse. */
  .qusx-break {
    direction: ltr;
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 4px 4px 10px;
    width: 100%;
    max-width: 760px;
  }
  .qusx-break .ln { flex: 1; height: 1px; background: var(--border); }
  .qusx-break .lbl {
    font-family: monospace;
    font-size: 10px;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: var(--text-muted);
    white-space: nowrap;
  }
  .qusx-break.page .lbl { color: var(--accent); }
  .qusx-break.minor { margin: 2px 4px 6px; opacity: 0.55; }
  .qusx-break.minor .lbl { font-size: 9px; }
  .ayah-pin {
    display: inline-flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;
    min-width: 1.6em;
    height: 1.6em;
    margin: 0 0.3em;
    border: 1.3px solid var(--accent);
    border-radius: 50%;
    font-family: monospace;
    font-size: 0.4em;
    color: var(--accent);
    vertical-align: 0.18em;
  }
  .qusx-ruku {
    direction: ltr;
    width: 100%;
    max-width: 760px;
    text-align: center;
    margin: 2px 4px 8px;
    font-family: monospace;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    opacity: 0.7;
  }
  .bismillah {
    width: 100%;
    max-width: 760px;
    text-align: center;
    font-family: 'UthmanicHafs', "Traditional Arabic", "Scheherazade New", serif;
    font-size: 24px;
    color: var(--accent);
    margin: 4px 4px 16px;
  }
  .qusx-line-break { flex-basis: 100%; height: 0; }
  .sajda-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: monospace;
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid var(--accent);
    color: var(--accent);
    background: var(--accent-soft);
    margin-left: 8px;
    direction: ltr;
  }
  .verse-text {
    font-family: 'UthmanicHafs', "Traditional Arabic", "Scheherazade New", serif;
    font-size: 34px;
    line-height: 2.3;
    letter-spacing: 0.01em;
  }
  /* Mushaf mode: real KFGQPC V2 mushaf font (one precomposed glyph per
     word, per-page font file — loaded dynamically per page number), the
     same edition QUSX's own `layout` attribute references — rendered as
     ONE CONTINUOUS FLOWING PAGE, not per-verse cards: a real mushaf has no
     visual break between verses, so words from consecutive ayahs share
     the same line right up to QUSX's actual line-break positions.
     Full lines are edge-to-edge via flex space-between so the visual left
     of the page aligns like a printed mushaf. True kashida shaping still
     isn't available; this only redistributes inter-word space. Single-token
     lines keep natural width (`.is-short`). */
  .mushaf-pages {
    display: none;
    width: 100%;
    max-width: 760px;
    flex-direction: column;
    gap: 4px;
  }
  .mushaf-page {
    background: linear-gradient(180deg, var(--surface-2), var(--surface));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px 26px 28px;
    box-shadow: var(--shadow);
  }
  .mushaf-page-header {
    direction: ltr;
    text-align: center;
    font-family: monospace;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 14px;
  }
  .mushaf-text {
    direction: rtl;
    font-size: 30px;
    line-height: 2.2;
    letter-spacing: 0;
    text-align: start;
  }
  .mushaf-line {
    display: flex;
    flex-wrap: nowrap;
    align-items: baseline;
    justify-content: space-between;
    direction: rtl;
    width: 100%;
  }
  .mushaf-line.is-short {
    justify-content: flex-start;
    gap: 0.35em;
  }
  /* Letter/Word hybrid: same page/line shell as Mushaf, but real Uthmani
     letters so phoneme highlighting still works. */
  .mushaf-text.with-letters {
    font-family: 'UthmanicHafs', "Traditional Arabic", "Scheherazade New", serif;
  }
  .mushaf-line .word {
    display: inline-block;
    flex: 0 0 auto;
    white-space: nowrap;
    max-width: 100%;
  }
  .mushaf-line .word .letter { display: inline; }
  .letter.mark-only {
    display: inline-block;
    width: 0;
    height: 0;
    overflow: hidden;
    padding: 0;
    margin: 0;
    border: 0;
    font-size: 0;
    line-height: 0;
    vertical-align: baseline;
  }
  .mushaf-glyph {
    display: inline-block;
    flex: 0 0 auto;
    border-radius: 6px;
    padding: 2px 4px;
    margin: 0;
    transition: background 0.15s;
    cursor: pointer;
  }
  .mushaf-glyph.active-word { background: var(--accent-soft); }
  .mushaf-num-glyph {
    display: inline-block;
    flex: 0 0 auto;
    color: var(--accent);
    margin: 0;
  }
  .letter { transition: color 0.08s, text-shadow 0.08s; }
  .letter.lit { color: var(--accent); text-shadow: 0 0 14px var(--accent-soft); }
  .word {
    display: inline; /* NOT inline-flex/inline-block — those break Arabic cursive glyph shaping across sibling letter spans */
    border-radius: 8px;
    padding: 4px 2px;
    box-decoration-break: clone;
    -webkit-box-decoration-break: clone;
    transition: box-shadow 0.15s, background 0.15s;
  }
  .word:hover { box-shadow: 0 0 0 1px var(--border); }
  .word.active-word {
    background: var(--accent-soft);
    box-shadow: 0 0 0 3px var(--accent-soft);
  }
  .controls {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: rgba(15,17,21,0.92);
    backdrop-filter: blur(12px);
    border-top: 1px solid var(--border);
    padding: 10px 20px 14px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }
  .scrubber {
    display: flex;
    gap: 6px;
    width: 100%;
    max-width: 760px;
    overflow-x: auto;
    padding-bottom: 2px;
  }
  .scrubber::-webkit-scrollbar { height: 4px; }
  .scrub-btn {
    flex: 1;
    min-width: 34px;
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text-muted);
    border-radius: 8px;
    padding: 6px 4px;
    font-size: 11px;
    font-family: monospace;
    cursor: pointer;
    text-align: center;
    white-space: nowrap;
  }
  .scrub-btn.active { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }
  .controls-row { display: flex; align-items: center; gap: 14px; width: 100%; max-width: 760px; }
  .info-bar { display: flex; align-items: center; gap: 10px; min-width: 150px; }
  .info-avatar {
    width: 30px; height: 30px; border-radius: 50%;
    background: var(--accent-soft); color: var(--accent);
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; flex-shrink: 0;
  }
  .info-text { line-height: 1.25; }
  .info-name { font-size: 12px; font-weight: 600; }
  .info-meta { font-size: 10.5px; color: var(--text-muted); }
  button.play-btn {
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    color: #1a1508;
    border: none;
    border-radius: 50%;
    width: 46px; height: 46px;
    font-size: 18px;
    cursor: pointer;
    flex-shrink: 0;
    box-shadow: 0 4px 16px rgba(232,191,63,0.35);
    display: flex; align-items: center; justify-content: center;
    transition: transform 0.12s;
  }
  button.play-btn:hover { transform: scale(1.05); }
  button.play-btn:active { transform: scale(0.96); }
  input[type=range] { flex: 1; accent-color: var(--accent); }
  .time { font-family: monospace; font-size: 12px; color: var(--text-muted); min-width: 42px; text-align: center; }
  .mode-toggle { display: flex; gap: 6px; font-size: 12px; flex-shrink: 0; }
  .mode-toggle button {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text-muted);
    border-radius: 20px;
    padding: 5px 12px;
    cursor: pointer;
  }
  .mode-toggle button.on { color: var(--accent); border-color: var(--accent); background: var(--accent-soft); }
  .tajweed-btn.on { color: #4fd17a; border-color: #4fd17a; background: rgba(79,209,122,0.14); }
  .tajweed-btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .credit { color: var(--text-muted); font-size: 11px; margin-top: 22px; text-align: center; max-width: 600px; line-height: 1.6; }
  .credit a { color: var(--accent); }

  .browse-bar {
    display: none;
    align-items: center;
    justify-content: center;
    gap: 16px;
    width: 100%;
    max-width: 760px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 10px 16px;
  }
  .browse-bar.on { display: flex; }
  .browse-step {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 8px;
    width: 34px; height: 34px;
    font-size: 15px;
    cursor: pointer;
    flex-shrink: 0;
  }
  .browse-step:hover { border-color: var(--accent); color: var(--accent); }
  .browse-letter {
    font-family: 'UthmanicHafs', "Traditional Arabic", "Scheherazade New", serif;
    font-size: 40px;
    color: var(--accent);
    min-width: 60px;
    text-align: center;
  }
  .browse-meta { font-size: 11px; color: var(--text-muted); font-family: monospace; text-align: center; flex: 1; }

  .word.has-morph { cursor: help; }
  .morph-tip {
    position: fixed;
    z-index: 50;
    background: var(--surface);
    border: 1px solid var(--accent);
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    color: var(--text);
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.12s;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    max-width: 240px;
    direction: rtl;
  }
  .morph-tip.show { opacity: 1; }
  .morph-tip .mt-row { display: flex; justify-content: space-between; gap: 12px; margin-top: 4px; direction: ltr; }
  .morph-tip .mt-label { color: var(--text-muted); font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.04em; }
  .morph-tip .mt-arabic { font-family: 'UthmanicHafs', "Traditional Arabic", "Scheherazade New", serif; font-size: 18px; }

  /* Word inspector — a persistent panel (unlike the ephemeral hover tooltip
     above) that stays open until explicitly closed, so a learner can keep
     it visible while reading rather than re-hovering the same word. Docked
     bottom-right on wide screens; becomes a full-width bottom sheet under
     640px since there's no room for a floating corner panel there. */
  .word-inspector {
    position: fixed;
    z-index: 60;
    right: 20px;
    bottom: 150px;
    width: 280px;
    max-width: calc(100vw - 40px);
    background: var(--surface);
    border: 1px solid var(--accent);
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: var(--shadow);
    direction: rtl;
    transform: translateY(12px);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.15s, transform 0.15s;
  }
  .word-inspector.show { opacity: 1; transform: translateY(0); pointer-events: auto; }
  .word-inspector .wi-close {
    position: absolute;
    top: 8px; left: 8px;
    direction: ltr;
    background: transparent;
    border: none;
    color: var(--text-muted);
    font-size: 18px;
    line-height: 1;
    cursor: pointer;
    padding: 4px;
  }
  .word-inspector .wi-close:hover { color: var(--accent); }
  .word-inspector .wi-arabic {
    font-family: 'UthmanicHafs', "Traditional Arabic", "Scheherazade New", serif;
    font-size: 32px;
    text-align: center;
    margin-bottom: 4px;
  }
  .word-inspector .wi-ref {
    direction: ltr;
    text-align: center;
    font-family: monospace;
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 12px;
  }
  .word-inspector .wi-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 12px;
    padding: 6px 0;
    border-top: 1px solid var(--border);
    direction: ltr;
  }
  .word-inspector .wi-label {
    color: var(--text-muted);
    font-size: 10.5px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    flex-shrink: 0;
  }
  .word-inspector .wi-value {
    font-family: 'UthmanicHafs', "Traditional Arabic", "Scheherazade New", serif;
    font-size: 17px;
    direction: rtl;
    text-align: right;
  }
  .word-inspector .wi-value.mono { font-family: monospace; font-size: 12px; direction: ltr; }
  .word.inspected { box-shadow: 0 0 0 2px var(--accent) !important; }
  .wi-gloss {
    direction: ltr;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--border);
  }
  .wi-gloss-lang { display: flex; gap: 6px; margin-bottom: 8px; }
  .wi-lang-btn {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text-muted);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 11px;
    cursor: pointer;
  }
  .wi-lang-btn.on { color: var(--accent); border-color: var(--accent); background: var(--accent-soft); }
  .wi-gloss-body { font-size: 13px; color: var(--text-muted); min-height: 18px; }
  .wi-gloss-text { color: var(--text); font-size: 14px; margin-bottom: 4px; }
  .wi-gloss-spoken { font-size: 11px; font-style: italic; margin-bottom: 8px; }
  .wi-play-btn {
    background: var(--accent-soft);
    border: 1px solid var(--accent);
    color: var(--accent);
    border-radius: 8px;
    padding: 5px 12px;
    font-size: 12px;
    cursor: pointer;
  }
  .wi-play-btn:hover { background: var(--accent); color: var(--surface); }
  @media (max-width: 640px) {
    .word-inspector {
      left: 12px; right: 12px; bottom: 150px; width: auto;
    }
  }

  .surah-picker {
    display: flex; align-items: center; gap: 10px; margin-bottom: 6px;
  }
  .surah-picker select {
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 13px;
    max-width: 260px;
    cursor: pointer;
    transition: border-color 0.15s;
  }
  .surah-picker select:hover, .surah-picker select:focus { border-color: var(--accent); outline: none; }
  .theme-toggle {
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 10px;
    width: 36px;
    height: 36px;
    font-size: 15px;
    cursor: pointer;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: border-color 0.15s;
  }
  .theme-toggle:hover { border-color: var(--accent); }
  .load-status {
    color: var(--text-muted);
    font-size: 12px;
    min-height: 16px;
    margin-bottom: 4px;
  }
  .load-status.error { color: #e05858; }
  .tradition-info {
    font-family: monospace;
    font-size: 10.5px;
    color: var(--text-muted);
    opacity: 0.7;
    margin-bottom: 18px;
    max-width: 760px;
    text-align: center;
  }
  .tradition-info.diverges { color: var(--accent); opacity: 0.9; }
</style>
</head>
<body>

<h1>Qur'an &middot; Follow Along</h1>
<div class="surah-picker">
  <select id="surahSelect"></select>
  <select id="reciterSelect"></select>
  <select id="layoutSelect" title="Print layout — changes page/line breaks; only Madani V2 has real calligraphic glyphs"></select>
  <button class="theme-toggle" id="themeToggle" title="Toggle light/dark" aria-label="Toggle light/dark theme">&#9789;</button>
</div>
<div class="load-status" id="loadStatus">&nbsp;</div>
<div class="tradition-info" id="traditionInfo"></div>
<div class="subtitle">data from <a href="https://huggingface.co/datasets/hetchyy/quranic-universal-ayahs" target="_blank">Qur'anic Universal Audio</a> (36 reciters) &middot; text &amp; word morphology from <a href="https://github.com/dfordev1/usxv2" target="_blank">QUSX</a> &middot; Mushaf glyphs &amp; tajweed colors from <a href="https://qul.tarteel.ai" target="_blank">Tarteel QUL</a></div>

<div class="verses" id="verses"></div>
<div class="mushaf-pages" id="mushafPages"></div>
<div class="morph-tip" id="morphTip"></div>
<div class="word-inspector" id="wordInspector">
  <button class="wi-close" id="wiClose" aria-label="Close word inspector">&times;</button>
  <div class="wi-body" id="wiBody"></div>
</div>

<div class="controls">
  <div class="scrubber" id="scrubber"></div>
  <div class="browse-bar" id="browseBar">
    <button class="browse-step" id="browsePrev">&#8592;</button>
    <span class="browse-letter" id="browseLetter">&nbsp;</span>
    <span class="browse-meta" id="browseMeta">letter 1 / 1</span>
    <button class="browse-step" id="browseNext">&#8594;</button>
  </div>
  <div class="controls-row">
    <div class="info-bar">
      <div class="info-avatar" id="infoAvatar">AS</div>
      <div class="info-text">
        <div class="info-name" id="infoName">Abu Bakr Al-Shatri</div>
        <div class="info-meta" id="infoMeta">Al-Fatiha 1</div>
      </div>
    </div>
    <button class="play-btn" id="playBtn">&#9658;</button>
    <span class="time" id="curTime">0:00</span>
    <input type="range" id="seek" min="0" max="1000" value="0">
    <span class="time" id="totTime">0:00</span>
  </div>
  <div class="mode-toggle">
    <button id="modeLetter" class="on">Letter</button>
    <button id="modeWord">Word</button>
    <button id="modeMushaf">Mushaf</button>
    <button id="tajweedToggle" class="tajweed-btn" disabled title="Colored tajweed rules, Mushaf mode only">Tajweed</button>
    <button id="modeBrowse">Browse letters</button>
  </div>
</div>

<div class="credit">Built on the open-source <a href="https://github.com/Wider-Community/quranic-universal-audio" target="_blank">Qur'anic Universal Audio</a> dataset &mdash; phoneme-aligned timestamps, CC BY 4.0. Audio: audio-cdn.tarteel.ai. Text, morphology &amp; milestones (juz/hizb/rub/manzil/ruku/page/line/sajda) from <a href="https://github.com/dfordev1/usxv2" target="_blank">QUSX</a>, Hafs &#39;an &#39;Asim (hafs-kufi) tradition, NFC-normalized. Spoken word-by-word English/Hindi gloss from <a href="https://github.com/dfordev1/qusx-audio" target="_blank">QUSX-Audio</a>.</div>

<audio id="player" preload="auto"></audio>

<script>
const SURAH_INDEX = __SURAH_INDEX_JSON__; // 114 entries: {num, name, nameArabic, ayahCount}, from QUSX (github.com/dfordev1/usxv2)

// QPC V2 glyph data: surah -> ayah -> [glyph char per word position, plus a
// trailing ayah-number glyph]. From Tarteel's QUL ("QPC V2 Glyph - Word by
// Word" resource) — the real per-word glyph codes for the same "KFGQPC V2"
// mushaf edition QUSX's own `layout` attribute already references. Paired
// at render time with the actual per-page QCF V2 font files (loaded live,
// per page, from Quran Foundation's open font CDN — see ensurePageFont).
const GLYPH_V2 = __GLYPH_V2_JSON__;

// One @font-face-equivalent FontFace per mushaf page (604 total across the
// whole Qur'an), loaded lazily only for pages actually shown, from the
// same public, CORS-open CDN Quran.com's own Mushaf mode uses.
const loadedPageFonts = new Set();
async function ensurePageFont(page) {
  if (!page || loadedPageFonts.has(page)) return;
  loadedPageFonts.add(page);
  try {
    const font = new FontFace('QCFP' + page, 'url(https://verses.quran.foundation/fonts/quran/hafs/v2/woff2/p' + page + '.woff2)');
    await font.load();
    document.fonts.add(font);
  } catch (e) {
    // Font failed to load (offline, blocked, etc) — mushaf mode falls back
    // to the default serif and shows tofu for the glyph codepoints instead
    // of crashing; classic letter/word modes are unaffected either way.
  }
}

// Tajweed-colored mushaf font (QCF V4, COLRv1 color-font format): SAME
// per-word glyph codes as V2 (GLYPH_V2 / the "code_v2" field is shared
// across V2 and V4 per Quran Foundation's own docs) — only the font FILE
// differs, with each glyph's tajweed-rule coloring painted in by the
// original typesetters. Chrome/Edge/Safari render COLRv1 natively;
// Firefox falls back to plain glyph shapes (no crash, just no color).
const loadedTajweedFonts = new Set();
async function ensureTajweedFont(page) {
  if (!page || loadedTajweedFonts.has(page)) return;
  loadedTajweedFonts.add(page);
  try {
    const font = new FontFace('QCFT' + page, 'url(https://verses.quran.foundation/fonts/quran/hafs/v4/colrv1/woff2/p' + page + '.woff2)');
    await font.load();
    document.fonts.add(font);
  } catch (e) {
    // falls back to the plain V2 glyph shape for this page, no crash
  }
}

const RECITERS = __RECITERS_JSON__; // [config, displayName][] — all 36 reciters in the QUA dataset (hetchyy/quranic-universal-ayahs)
let RECITER_CONFIG = RECITERS[8][0]; // default: Abu Bakr Al-Shatri

// Per-surah ayah-count deltas across qira'at numbering traditions (Warsh,
// Qalun, Ad-Duri, Shu'bah vs Hafs/Kufi) — only the 55 surahs where they
// actually diverge; a surah absent from this map counts identically in
// every tradition. From QUSX's own data/diff-report.json.
const TRADITION_DIFFS = __TRADITION_DIFFS_JSON__;
const TRADITION_DIFFS_BY_SURAH = {};
for (const entry of TRADITION_DIFFS) TRADITION_DIFFS_BY_SURAH[entry.surah] = entry;

// cumulative row offset per surah, for jumping straight to any surah's rows
// in the HF datasets-server API without paging through the whole dataset
let cum = 0;
const SURAH_OFFSET = {};
for (const s of SURAH_INDEX) { SURAH_OFFSET[s.num] = cum; cum += s.ayahCount; }

let VERSES = [];        // current surah's verses, fetched live
let MORPHOLOGY = {};    // 'ayah:position' -> {root,stem,lemma,text}, fetched live from QUSX
let currentSurah = 1;

// QUSX ships the SAME word text/morphology across all 10 print layouts —
// only page/line placement differs per real print edition (see the layout
// table in usxv2's README). Real calligraphic QCF glyphs + tajweed COLRv1
// fonts are only bundled here for madani-v2 (qpc_v2_glyphs.json); every
// other layout still gets its OWN authentic page/line wraps (fetched live
// from that layout's own .qusx.xml), just rendered in plain Uthmani text
// instead of precomposed glyphs.
const LAYOUTS = [
  ['madani-v2', 'Madani V2 (KFGQPC, glyphs)'],
  ['madani-v1', 'Madani V1 (KFGQPC 1405H)'],
  ['madani-v4-tajweed', 'Madani V4 Tajweed'],
  ['qatar', 'Mushaf Qatar'],
  ['indopak-15', 'IndoPak 15-line'],
  ['indopak-9-gaba', 'IndoPak 9-line (Gaba)'],
  ['indopak-13-qudratullah', 'IndoPak 13-line (Qudratullah)'],
  ['indopak-13-taj', 'IndoPak 13-line (Taj Co.)'],
  ['indopak-16-taj', 'IndoPak 16-line (Taj Co.)'],
  ['nastaleeq', 'KFGQPC Nastaleeq 15-line'],
];
let currentLayout = 'madani-v2';

let mode = 'letter'; // 'letter' | 'word' | 'mushaf'
let tajweedOn = false; // Mushaf-mode-only: colored tajweed rules via QCF V4
let currentVerseIdx = 0;
let userSeeking = false;

const versesEl = document.getElementById('verses');
const audio = document.getElementById('player');
const playBtn = document.getElementById('playBtn');
const seek = document.getElementById('seek');
const curTimeEl = document.getElementById('curTime');
const totTimeEl = document.getElementById('totTime');
const surahSelect = document.getElementById('surahSelect');
const reciterSelect = document.getElementById('reciterSelect');
const loadStatusEl = document.getElementById('loadStatus');
const infoAvatar = document.getElementById('infoAvatar');
const infoName = document.getElementById('infoName');

SURAH_INDEX.forEach(s => {
  const opt = document.createElement('option');
  opt.value = s.num;
  opt.textContent = s.num + '. ' + s.name + ' (' + s.nameArabic + ')';
  surahSelect.appendChild(opt);
});
surahSelect.addEventListener('change', () => loadSurah(+surahSelect.value));

RECITERS.forEach(([config, name]) => {
  const opt = document.createElement('option');
  opt.value = config;
  opt.textContent = name;
  if (config === RECITER_CONFIG) opt.selected = true;
  reciterSelect.appendChild(opt);
});
function reciterInitials(name) {
  return name.split(/[\s(]/).filter(Boolean).slice(0, 2).map(w => w[0]).join('').toUpperCase();
}
function refreshReciterInfo() {
  const name = RECITERS.find(r => r[0] === RECITER_CONFIG)?.[1] || RECITER_CONFIG;
  infoName.textContent = name;
  infoAvatar.textContent = reciterInitials(name);
}
reciterSelect.addEventListener('change', () => {
  RECITER_CONFIG = reciterSelect.value;
  refreshReciterInfo();
  loadSurah(currentSurah); // same surah, new reciter's audio/timing
});
refreshReciterInfo();

const layoutSelect = document.getElementById('layoutSelect');
LAYOUTS.forEach(([key, name]) => {
  const opt = document.createElement('option');
  opt.value = key;
  opt.textContent = name;
  if (key === currentLayout) opt.selected = true;
  layoutSelect.appendChild(opt);
});
layoutSelect.addEventListener('change', () => {
  currentLayout = layoutSelect.value;
  loadedPageFonts.clear();     // glyph fonts are keyed by page number, which means something different per layout
  loadedTajweedFonts.clear();
  if (currentLayout !== 'madani-v2') {
    tajweedOn = false;
    tajweedBtn.classList.remove('on');
  }
  tajweedBtn.disabled = mode !== 'mushaf' || currentLayout !== 'madani-v2';
  loadSurah(currentSurah); // same surah, this layout's own page/line pins
});

// Theme toggle — the actual data-theme attribute was already set pre-paint
// by the inline script in <head>; this just wires up the button and
// persists explicit user choices, which always beat the OS preference.
const themeToggleBtn = document.getElementById('themeToggle');
function refreshThemeIcon() {
  const isLight = document.documentElement.getAttribute('data-theme') === 'light';
  themeToggleBtn.innerHTML = isLight ? '&#9788;' : '&#9789;'; // sun : moon
  themeToggleBtn.title = isLight ? 'Switch to dark mode' : 'Switch to light mode';
}
themeToggleBtn.addEventListener('click', () => {
  const next = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('quran-theme', next);
  refreshThemeIcon();
});
refreshThemeIcon();

function fmtTime(ms) {
  const s = Math.floor(ms / 1000);
  const m = Math.floor(s / 60);
  const r = s % 60;
  return m + ':' + String(r).padStart(2, '0');
}

// Split full-tashkeel Uthmani text into display "clusters": a base letter plus
// any trailing combining marks (harakat, shadda, sukun, tanwin, tatweel,
// superscript alef). Timing may still treat some marks as their own step —
// those are attached back onto the previous letter at render time so the
// browser never paints the dotted-circle placeholder (◌).
const COMBINING_RANGES = [
  [0x064B, 0x0652], // fathatan..sukun
  [0x0653, 0x065F], // maddah/hamza-above-below variants, small marks
  [0x0670, 0x0670], // superscript alef (madd) — combining for display
  [0x06D6, 0x06ED],  // quranic annotation signs
  [0x0610, 0x061A],  // honorific/quranic signs
  [0x0640, 0x0640],  // tatweel
];
function isCombining(cp) {
  for (const [a, b] of COMBINING_RANGES) if (cp >= a && cp <= b) return true;
  return false;
}
function isMarkOnly(text) {
  if (!text) return false;
  for (const ch of text) {
    if (!isCombining(ch.codePointAt(0))) return false;
  }
  return true;
}
function buildClusters(text) {
  const clusters = [];
  for (const ch of text) {
    if (ch === ' ') continue;
    const cp = ch.codePointAt(0);
    if (isCombining(cp) && clusters.length) {
      clusters[clusters.length - 1] += ch;
    } else {
      clusters.push(ch);
    }
  }
  return clusters;
}

let flatLetters = []; // built up across all verses while rendering, for letter-browse mode; reset per surah load

// Build one timed word span with per-letter children (Letter/Word hybrid).
// Shared by the mushaf-page letter layout so phoneme highlighting works
// inside a continuous page, not only inside classic verse cards.
function getVerseLetterRuns(v) {
  if (v._letterRuns) return v._letterRuns;
  const letters = v.letters;
  const n = letters.word_idx.length;
  const firstRunByWord = new Map();
  const extraWindowsByWord = new Map();
  let i = 0;
  while (i < n) {
    const wIdx = letters.word_idx[i];
    const start = i;
    while (i < n && letters.word_idx[i] === wIdx) i++;
    const run = { wIdx, start, end: i };
    if (!firstRunByWord.has(wIdx)) {
      firstRunByWord.set(wIdx, run);
    } else {
      const absStart = v.source_offset_ms + letters.start_ms[run.start];
      const absEnd = v.source_offset_ms + letters.end_ms[run.end - 1];
      if (!extraWindowsByWord.has(wIdx)) extraWindowsByWord.set(wIdx, []);
      extraWindowsByWord.get(wIdx).push([absStart, absEnd]);
    }
  }
  v._letterRuns = { firstRunByWord, extraWindowsByWord };
  return v._letterRuns;
}

function buildTimedWordSpan(v, wIdx, verseIdx) {
  const letters = v.letters;
  const { firstRunByWord, extraWindowsByWord } = getVerseLetterRuns(v);
  const run = firstRunByWord.get(wIdx);
  if (!run) return null;

  const qusxWords = v.qusxWords || [];
  const wordClusters = buildClusters(qusxWords[wIdx - 1] || '');
  const useClusters = wordClusters.length === (run.end - run.start);

  const wordSpan = document.createElement('span');
  wordSpan.className = 'word';
  wordSpan.dataset.word = wIdx;
  wordSpan.dataset.ayah = v.ayah;
  let wordStart = null;
  for (let j = run.start; j < run.end; j++) {
    const absStart = v.source_offset_ms + letters.start_ms[j];
    const absEnd = v.source_offset_ms + letters.end_ms[j];
    if (wordStart === null) wordStart = absStart;
    const text = useClusters ? wordClusters[j - run.start] : letters.char[j];

    // Timing often isolates a combining mark (۟ ٰ etc.) as its own step.
    // A mark alone paints as ◌ + mark — attach it to the previous letter
    // for display, and keep a zero-width timing span that lights that base.
    if (isMarkOnly(text) && wordSpan.lastElementChild) {
      const prev = wordSpan.lastElementChild;
      prev.textContent += text;
      if (absEnd > +prev.dataset.end) prev.dataset.end = String(absEnd);
      const ghost = document.createElement('span');
      ghost.className = 'letter mark-only';
      ghost.dataset.start = absStart;
      ghost.dataset.end = absEnd;
      ghost.dataset.word = wIdx;
      ghost.dataset.ayah = v.ayah;
      ghost.dataset.gidx = flatLetters.length;
      ghost.dataset.attachPrev = '1';
      ghost.textContent = '';
      flatLetters.push({ verseIdx, verse: v, startMs: absStart, endMs: absEnd, char: text });
      wordSpan.appendChild(ghost);
      continue;
    }

    const ch = document.createElement('span');
    ch.className = 'letter';
    ch.dataset.start = absStart;
    ch.dataset.end = absEnd;
    ch.dataset.word = wIdx;
    ch.dataset.ayah = v.ayah;
    ch.dataset.gidx = flatLetters.length;
    // Orphan mark with no base yet — use tatweel so shaping has a carrier
    // instead of inventing a dotted circle.
    ch.textContent = isMarkOnly(text) ? ('\u0640' + text) : text;
    flatLetters.push({ verseIdx, verse: v, startMs: absStart, endMs: absEnd, char: text });
    wordSpan.appendChild(ch);
  }
  const extraWindows = extraWindowsByWord.get(wIdx);
  if (extraWindows) {
    const json = JSON.stringify(extraWindows);
    wordSpan.dataset.extraWindows = json;
    wordSpan.querySelectorAll('.letter').forEach(el => { el.dataset.extraWindows = json; });
  }
  if (wordStart != null) {
    wordSpan.dataset.startMs = wordStart;
    wordSpan.addEventListener('click', (e) => {
      e.stopPropagation();
      audio.currentTime = wordStart / 1000;
      audio.play();
      jumpToVerse(verseIdx, false);
    });
  }
  const morph = MORPHOLOGY[v.ayah + ':' + wIdx];
  if (morph) {
    wordSpan.classList.add('has-morph');
    wordSpan.tabIndex = 0;
    wordSpan.addEventListener('mouseenter', () => showMorphTip(wordSpan, morph));
    wordSpan.addEventListener('mouseleave', hideMorphTip);
    wordSpan.addEventListener('focus', () => showMorphTip(wordSpan, morph));
    wordSpan.addEventListener('blur', hideMorphTip);
    wordSpan.addEventListener('click', () => showInspector(wordSpan, morph, v, wIdx));
  }
  return wordSpan;
}

function renderVerse(v, idx) {
  // Legacy per-ayah card renderer — kept for reference but unused: Letter/Word
  // now share the continuous mushaf page shell (see renderMushafPages).
  const div = document.createElement('div');
  div.className = 'verse';
  div.dataset.idx = idx;

  const numEl = document.createElement('div');
  numEl.className = 'verse-num';
  numEl.textContent = v.surah + ':' + v.ayah;
  if (v.sajda) {
    const badge = document.createElement('span');
    badge.className = 'sajda-badge';
    badge.textContent = '۩ sajda · ' + v.sajda;
    numEl.appendChild(badge);
  }
  div.appendChild(numEl);

  const textEl = document.createElement('div');
  textEl.className = 'verse-text classic-text';

  const wordLines = v.wordLines || [];
  let lastLine = wordLines.length ? wordLines[0] : null;
  const qusxWords = v.qusxWords || [];
  for (let wIdx = 1; wIdx <= qusxWords.length; wIdx++) {
    const thisLine = wordLines[wIdx - 1];
    if (thisLine != null && lastLine != null && thisLine !== lastLine) {
      textEl.appendChild(document.createElement('br'));
    }
    lastLine = thisLine != null ? thisLine : lastLine;
    const wordSpan = buildTimedWordSpan(v, wIdx, idx);
    if (wordSpan) {
      textEl.appendChild(wordSpan);
      textEl.appendChild(document.createTextNode(' '));
    }
  }

  const pin = document.createElement('span');
  pin.className = 'ayah-pin';
  pin.textContent = toArabicDigits(v.ayah);
  textEl.appendChild(pin);

  div.appendChild(textEl);
  div.addEventListener('click', () => jumpToVerse(idx));
  return div;
}

// --- Mushaf mode: a genuinely continuous page, not per-verse cards. Real
// mushaf pages have no visual break between verses at all — words just
// flow, wrapping to a new line only where QUSX's own <line> pins say a
// real mushaf line ends, which often falls MID-ayah. So this groups
// VERSES by page and lays out every word from every verse on that page
// into one shared flow of line-divs, carrying the current line number
// across ayah boundaries within the page (not resetting per verse).
const mushafPagesEl = document.getElementById('mushafPages');

function buildMushafGlyphSpan(v, wIdx, wordStart) {
  const glyphWords = (GLYPH_V2[v.surah] || {})[v.ayah] || [];
  const glyphChar = glyphWords[wIdx - 1];
  if (!glyphChar) return null;
  const gSpan = document.createElement('span');
  gSpan.className = 'word mushaf-glyph';
  gSpan.dataset.word = wIdx;
  gSpan.dataset.ayah = v.ayah;
  gSpan.textContent = glyphChar;
  if (wordStart != null) {
    gSpan.addEventListener('click', (e) => {
      e.stopPropagation();
      audio.currentTime = wordStart / 1000;
      audio.play();
      jumpToVerse(VERSES.indexOf(v), false);
    });
  }
  return gSpan;
}

// Fallback for the 9 non-madani-v2 layouts, which have no bundled QCF glyph
// font: plain Uthmani text per word instead of a precomposed glyph, but
// still laid out against THIS layout's own real page/line pins (fetched
// from that layout's own .qusx.xml) — so the wrap points are authentic to
// that print edition even though the letterforms aren't calligraphic.
// Kept on the same "mushaf-glyph" class so the existing active-word
// highlight selectors (by data-word/data-ayah) work unchanged.
function buildMushafPlainSpan(v, wIdx, wordText, wordStart) {
  if (!wordText) return null;
  const gSpan = document.createElement('span');
  gSpan.className = 'word mushaf-glyph';
  gSpan.dataset.word = wIdx;
  gSpan.dataset.ayah = v.ayah;
  gSpan.textContent = wordText;
  if (wordStart != null) {
    gSpan.addEventListener('click', (e) => {
      e.stopPropagation();
      audio.currentTime = wordStart / 1000;
      audio.play();
      jumpToVerse(VERSES.indexOf(v), false);
    });
  }
  return gSpan;
}

function renderMushafPages() {
  mushafPagesEl.innerHTML = '';
  if (!VERSES.length) return;
  // Letter/Word: same continuous page/line shell as Mushaf, but Uthmani
  // letter spans so phoneme highlighting still works. Mushaf: QCF glyphs.
  const withLetters = mode !== 'mushaf';
  if (withLetters) flatLetters = [];
  const sMeta = SURAH_INDEX.find(x => x.num === currentSurah);

  const pageGroups = [];
  for (const v of VERSES) {
    let g = pageGroups[pageGroups.length - 1];
    if (!g || g.page !== v.page) {
      g = { page: v.page, verses: [] };
      pageGroups.push(g);
    }
    g.verses.push(v);
  }

  pageGroups.forEach((g, gi) => {
    const pageDiv = document.createElement('div');
    pageDiv.className = 'mushaf-page';

    const header = document.createElement('div');
    header.className = 'mushaf-page-header';
    const juz = g.verses[0].juz;
    const hizb = g.verses[0].hizb;
    const manzil = g.verses[0].manzil;
    header.textContent = (g.page ? 'PAGE ' + g.page : '')
      + (juz ? '   ·   JUZ ' + juz : '')
      + (hizb ? '   ·   HIZB ' + hizb : '')
      + (manzil ? '   ·   MANZIL ' + manzil : '');
    pageDiv.appendChild(header);

    if (gi === 0 && sMeta && sMeta.bismillahPre && currentSurah !== 1) {
      const b = document.createElement('div');
      b.className = 'bismillah';
      b.textContent = 'بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ';
      pageDiv.appendChild(b);
    }

    const flow = document.createElement('div');
    flow.className = 'verse-text mushaf-text' + (withLetters ? ' with-letters' : '');
    const isV2 = currentLayout === 'madani-v2';
    if (!withLetters && isV2 && g.page) {
      const family = tajweedOn ? 'QCFT' + g.page : 'QCFP' + g.page;
      flow.style.fontFamily = family + ', "Traditional Arabic", serif';
    } else {
      flow.style.fontFamily = "'UthmanicHafs', 'Traditional Arabic', 'Scheherazade New', serif";
    }

    let curLineNum = null;
    let lineDiv = null;
    for (const v of g.verses) {
      const verseIdx = VERSES.indexOf(v);
      const wordLines = v.wordLines || [];
      const qusxWords = v.qusxWords || [];
      const wordTimeMs = new Map();
      for (const [wIdx, s] of (v.words || [])) wordTimeMs.set(wIdx, v.source_offset_ms + s);

      for (let wIdx = 1; wIdx <= qusxWords.length; wIdx++) {
        const thisLine = wordLines[wIdx - 1];
        if (!lineDiv || (thisLine != null && thisLine !== curLineNum)) {
          lineDiv = document.createElement('div');
          lineDiv.className = 'mushaf-line';
          flow.appendChild(lineDiv);
          curLineNum = thisLine;
        }
        if (withLetters) {
          const wordSpan = buildTimedWordSpan(v, wIdx, verseIdx);
          if (wordSpan) lineDiv.appendChild(wordSpan);
        } else {
          const wordStart = wordTimeMs.has(wIdx) ? wordTimeMs.get(wIdx) : null;
          const gSpan = isV2
            ? buildMushafGlyphSpan(v, wIdx, wordStart)
            : buildMushafPlainSpan(v, wIdx, qusxWords[wIdx - 1], wordStart);
          if (gSpan) lineDiv.appendChild(gSpan);
        }
      }
      if (!withLetters && isV2) {
        // The font's own trailing ayah-number glyph — the real mushaf's
        // ornamental end-of-verse marker, non-interactive (no audio of its
        // own), inline right after the verse's last word like the real page.
        const glyphWords = (GLYPH_V2[v.surah] || {})[v.ayah] || [];
        const numGlyph = glyphWords[glyphWords.length - 1];
        if (numGlyph && lineDiv) {
          const numSpan = document.createElement('span');
          numSpan.className = 'mushaf-num-glyph';
          numSpan.textContent = numGlyph;
          lineDiv.appendChild(numSpan);
        }
      } else if (lineDiv) {
        // Letter/Word hybrid + non-glyph layouts: circled ayah pin.
        const pin = document.createElement('span');
        pin.className = 'ayah-pin';
        pin.textContent = toArabicDigits(v.ayah);
        lineDiv.appendChild(pin);
      }
      if (v.sajda && lineDiv) {
        const badge = document.createElement('span');
        badge.className = 'sajda-badge';
        badge.textContent = '۩';
        lineDiv.appendChild(badge);
      }
    }
    pageDiv.appendChild(flow);
    mushafPagesEl.appendChild(pageDiv);
  });
  // Defer until fonts/glyphs have laid out so short-line detection is real.
  requestAnimationFrame(() => requestAnimationFrame(markShortMushafLines));
}

function markShortMushafLines() {
  // Only leave natural width for single-token lines (e.g. a lone ayah pin).
  // Every real mushaf line with 2+ glyphs is edge-to-edge; CSS space-between
  // is the closest we can get without kashida shaping.
  mushafPagesEl.querySelectorAll('.mushaf-line').forEach(line => {
    line.classList.toggle('is-short', line.children.length < 2);
  });
}

let mushafJustifyTimer = null;
window.addEventListener('resize', () => {
  clearTimeout(mushafJustifyTimer);
  mushafJustifyTimer = setTimeout(markShortMushafLines, 120);
});

const scrubberEl = document.getElementById('scrubber');

function toArabicDigits(n) {
  const map = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
  return String(n).split('').map(d => map[+d] ?? d).join('');
}

function makeBreak(label, isPage, isMinor) {
  const div = document.createElement('div');
  div.className = 'qusx-break' + (isPage ? ' page' : '') + (isMinor ? ' minor' : '');
  const ln1 = document.createElement('div');
  ln1.className = 'ln';
  const lbl = document.createElement('div');
  lbl.className = 'lbl';
  lbl.textContent = label;
  const ln2 = document.createElement('div');
  ln2.className = 'ln';
  div.appendChild(ln1);
  div.appendChild(lbl);
  div.appendChild(ln2);
  return div;
}

function makeRukuMark(n) {
  const div = document.createElement('div');
  div.className = 'qusx-ruku';
  div.textContent = '⁘ ruku ' + n;
  return div;
}

function renderAll() {
  versesEl.innerHTML = '';
  versesEl.style.display = 'none';
  scrubberEl.innerHTML = '';
  flatLetters = [];
  // Letter, Word, and Mushaf all share the continuous page shell.
  mushafPagesEl.style.display = 'flex';
  renderMushafPages();
  VERSES.forEach((v, idx) => {
    const b = document.createElement('button');
    b.className = 'scrub-btn';
    b.dataset.idx = idx;
    b.textContent = v.ayah;
    b.addEventListener('click', () => jumpToVerse(idx));
    scrubberEl.appendChild(b);
  });
}

function refreshScrubber(idx) {
  document.querySelectorAll('.scrub-btn').forEach((b, i) => b.classList.toggle('active', i === idx));
  const active = document.querySelector('.scrub-btn.active');
  if (active) active.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
}
const infoMeta = document.getElementById('infoMeta');
function refreshInfoBar(idx) {
  const s = SURAH_INDEX.find(x => x.num === currentSurah);
  const place = s && s.revelationPlace ? (s.revelationPlace === 'makkah' ? 'Makkan' : 'Madinan') : null;
  let text = (s ? s.name : currentSurah) + ' ' + VERSES[idx].ayah;
  if (place) text += ' · ' + place;
  infoMeta.textContent = text;
}

// The HF datasets-server /rows endpoint caps `length` at 100 — many surahs
// (Al-Baqarah has 286 ayahs) exceed that, so fetch in <=100-row pages and
// concatenate. Pages are independent (known offsets upfront), so fetch them
// concurrently rather than sequentially.
const ROWS_PAGE_SIZE = 100;
async function fetchAllRows(offset, length) {
  const pageOffsets = [];
  for (let o = offset; o < offset + length; o += ROWS_PAGE_SIZE) pageOffsets.push(o);
  const pages = await Promise.all(pageOffsets.map(async (o) => {
    const len = Math.min(ROWS_PAGE_SIZE, offset + length - o);
    const url = 'https://datasets-server.huggingface.co/rows?dataset=hetchyy%2Fquranic-universal-ayahs&config='
      + RECITER_CONFIG + '&split=train&offset=' + o + '&length=' + len;
    const res = await fetch(url);
    if (!res.ok) throw new Error('audio/timing fetch failed (' + res.status + ')');
    return (await res.json()).rows;
  }));
  return pages.flat();
}

// Fetch a surah's audio timing (QUA, per-reciter) + text/morphology (QUSX,
// canonical) live and merge them client-side by (ayah, word position) — the
// two datasets share that indexing convention, so no server-side join needed.
async function loadSurah(num) {
  currentSurah = num;
  const meta = SURAH_INDEX.find(s => s.num === num);
  loadStatusEl.textContent = 'Loading ' + meta.name + '…';
  loadStatusEl.classList.remove('error');
  audio.pause();
  hideInspector(); // the previously-inspected word's DOM node is about to be discarded by renderAll()

  try {
    const offset = SURAH_OFFSET[num];
    const length = meta.ayahCount;
    const xmlUrl = 'https://raw.githubusercontent.com/dfordev1/usxv2/main/output/' + currentLayout + '/'
      + String(num).padStart(3, '0') + '.qusx.xml';

    const [rows, xmlRes] = await Promise.all([fetchAllRows(offset, length), fetch(xmlUrl)]);
    if (!xmlRes.ok) throw new Error('QUSX text fetch failed (' + xmlRes.status + ')');
    const xmlText = await xmlRes.text();

    // Actually walk QUSX's milestone structure — this is a USX-style flat
    // word stream sliced by independent sid/eid boundary pins (juz, hizb,
    // rub, manzil, page, sajda, ayah), not just a bag of <word> attributes.
    // We track each axis's *currently open* pin as we walk in document
    // order, snapshot it onto each ayah, and reconstruct the ayah's own
    // canonical text from its word stream (not QUA's copy) — so QUSX is the
    // real text/structure source, and QUA is used only for audio + timing,
    // which is the division of labor this integration should have had from
    // the start.
    const doc = new DOMParser().parseFromString(xmlText, 'application/xml');
    if (doc.querySelector('parsererror')) throw new Error('QUSX XML parse error');
    const newMorph = {};
    const ayahMeta = {}; // ayah number -> {juz,hizb,rub,manzil,page,ruku,sajda,text,wordLines,fragments}
    let curAyah = null;
    let curJuz = null, curHizb = null, curRub = null, curManzil = null, curPage = null, curRuku = null, curLine = null;
    // fragment ("start"/"middle"/"end"/"whole") of whichever juz/hizb/rub/
    // manzil/ruku pin is CURRENTLY open — lets a consumer tell "this
    // milestone genuinely begins here" from "we're picking up mid-milestone
    // because the surah opened inside one carried over from before".
    let curJuzFrag = null, curHizbFrag = null, curRubFrag = null, curManzilFrag = null, curRukuFrag = null;
    let wordBuf = [];
    for (const el of doc.documentElement.children) {
      const tag = el.tagName;
      const num = el.getAttribute('number');
      if (tag === 'juz' && num) { curJuz = +num; curJuzFrag = el.getAttribute('fragment'); }
      else if (tag === 'hizb' && num) { curHizb = +num; curHizbFrag = el.getAttribute('fragment'); }
      else if (tag === 'rub' && num) { curRub = +num; curRubFrag = el.getAttribute('fragment'); }
      else if (tag === 'manzil' && num) { curManzil = +num; curManzilFrag = el.getAttribute('fragment'); }
      else if (tag === 'ruku' && num) { curRuku = +num; curRukuFrag = el.getAttribute('fragment'); }
      else if (tag === 'page' && num) curPage = +num;
      else if (tag === 'line' && num) curLine = +num;
      else if (tag === 'sajda') {
        if (curAyah) (ayahMeta[curAyah] || (ayahMeta[curAyah] = {})).sajda = el.getAttribute('type') || 'required';
      } else if (tag === 'ayah' && num) {
        curAyah = +num;
        wordBuf = [];
        ayahMeta[curAyah] = Object.assign({
          juz: curJuz, hizb: curHizb, rub: curRub, manzil: curManzil, page: curPage, ruku: curRuku,
          fragments: { juz: curJuzFrag, hizb: curHizbFrag, rub: curRubFrag, manzil: curManzilFrag, ruku: curRukuFrag },
          words: [], wordIds: [], wordLines: [],
        }, ayahMeta[curAyah] || {});
      } else if (tag === 'word' && curAyah) {
        if (el.getAttribute('type') !== 'number') {
          // Some QUSX words carry an embedded space in their OWN text (e.g.
          // "لَكُمْ ۗ" — the word plus its trailing pause mark, as one unit).
          // Keep each word's raw text in its own array slot, keyed by
          // position — never reconstruct per-word text by re-splitting the
          // joined ayah string on spaces later, since that embedded space
          // would silently shift every later word's index by one.
          wordBuf.push(el.textContent);
          ayahMeta[curAyah].words.push(el.textContent);
          ayahMeta[curAyah].wordIds.push(el.getAttribute('id'));
          ayahMeta[curAyah].wordLines.push(curLine);
          const pos = +el.getAttribute('position');
          newMorph[curAyah + ':' + pos] = {
            id: el.getAttribute('id'),
            root: el.getAttribute('root'),
            stem: el.getAttribute('stem'),
            lemma: el.getAttribute('lemma'),
            text: el.textContent,
          };
        }
        ayahMeta[curAyah].text = wordBuf.join(' ');
      }
    }

    VERSES = rows.map(row => {
      const r = row.row;
      const meta = ayahMeta[r.ayah] || {};
      return {
        surah: r.surah,
        ayah: r.ayah,
        // QUSX's own reconstructed word stream is the canonical text; QUA's
        // text_uthmani is kept only as a fallback if a row has no QUSX match
        text: meta.text || r.text_uthmani,
        qusxWords: meta.words || [], // QUSX's own per-word text, indexed by position — NOT re-derived from splitting `text`
        audio: 'https://' + r.source_url,
        duration_ms: r.duration_ms,
        source_offset_ms: r.source_offset_ms,
        words: r.word_timestamps,
        letters: r.letter_timestamps,
        juz: meta.juz, hizb: meta.hizb, rub: meta.rub, manzil: meta.manzil, page: meta.page, ruku: meta.ruku, sajda: meta.sajda,
        fragments: meta.fragments || {},
        wordLines: meta.wordLines || [],
      };
    });
    MORPHOLOGY = newMorph;

    // Load every distinct mushaf page's own font before rendering, so
    // Mushaf mode doesn't flash tofu-then-glyphs for the pages this surah
    // touches (usually 1-2, up to ~20 for very long surahs). Only madani-v2
    // has bundled QCF glyph/tajweed fonts — every other layout renders in
    // plain Uthmani text, so there's nothing page-specific to preload.
    if (currentLayout === 'madani-v2') {
      const pages = [...new Set(VERSES.map(v => v.page).filter(Boolean))];
      await Promise.all(pages.map(ensurePageFont));
      if (tajweedOn) await Promise.all(pages.map(ensureTajweedFont));
    }

    renderAll();
    audio.src = VERSES[0].audio;
    currentVerseIdx = 0;
    refreshScrubber(0);
    refreshInfoBar(0);
    scrollToPlayback(0);
    if (browsing) exitBrowse();
    loadStatusEl.textContent = meta.ayahCount + ' verses loaded — ' + meta.nameArabic;
    refreshTraditionInfo(num, meta.ayahCount);
  } catch (err) {
    loadStatusEl.textContent = 'Could not load ' + meta.name + ': ' + err.message;
    loadStatusEl.classList.add('error');
  }
}

// Numbering-only comparison against the pilot Warsh/Qalun/Ad-Duri/Shu'bah
// traditions — see TRADITION_DIFFS above. Not a full alternate-tradition
// read (no synced text/audio for those traditions), just surfacing the
// classical ʿadd al-āy (ayah-counting) divergence QUSX itself documents.
const TRADITION_LABELS = { qalon_kfqc: 'Qalun', qalon_libya: 'Qalun (Libya)', warsh_kfqc: 'Warsh', douri_kfqc: 'Ad-Duri', shubah_kfqc: "Shu'bah" };
const traditionInfoEl = document.getElementById('traditionInfo');
function refreshTraditionInfo(surahNum, hafsCount) {
  const diff = TRADITION_DIFFS_BY_SURAH[surahNum];
  if (!diff) {
    traditionInfoEl.textContent = 'Ayah count (' + hafsCount + ') is the same across every counted tradition';
    traditionInfoEl.classList.remove('diverges');
    return;
  }
  const parts = ['Hafs ' + diff.counts.hafs_kfqc];
  for (const [key, label] of Object.entries(TRADITION_LABELS)) {
    if (key in diff.counts) parts.push(label + ' ' + diff.counts[key]);
  }
  traditionInfoEl.textContent = 'Ayah count by tradition (numbering only): ' + parts.join(' · ');
  traditionInfoEl.classList.add('diverges');
}

function jumpToVerse(idx, autoplay) {
  if (autoplay === undefined) autoplay = true;
  currentVerseIdx = idx;
  if (autoplay) audio.currentTime = VERSES[idx].source_offset_ms / 1000;
  clearHighlights();
  refreshScrubber(idx);
  refreshInfoBar(idx);
  scrollToPlayback(idx);
  if (autoplay) audio.play();
}

function scrollToPlayback(idx) {
  const v = VERSES[idx];
  if (!v) return;
  const target =
    document.querySelector('.mushaf-pages .letter.lit') ||
    document.querySelector('.mushaf-pages .word.active-word[data-ayah="' + v.ayah + '"]') ||
    document.querySelector('.mushaf-pages .word[data-ayah="' + v.ayah + '"][data-word="1"]') ||
    document.querySelector('.mushaf-pages .mushaf-glyph[data-ayah="' + v.ayah + '"]');
  if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Word morphology tooltip (root/stem/lemma), from QUSX (github.com/dfordev1/usxv2)
const morphTipEl = document.getElementById('morphTip');
function showMorphTip(wordSpan, morph) {
  morphTipEl.innerHTML =
    '<div class="mt-arabic">' + morph.text + '</div>' +
    '<div class="mt-row"><span class="mt-label">root</span><span class="mt-arabic">' + morph.root + '</span></div>' +
    '<div class="mt-row"><span class="mt-label">lemma</span><span class="mt-arabic">' + morph.lemma + '</span></div>' +
    (morph.id ? '<div class="mt-row"><span class="mt-label">word id</span><span class="mt-arabic">' + morph.id + '</span></div>' : '');
  const r = wordSpan.getBoundingClientRect();
  morphTipEl.style.left = Math.max(8, r.left + r.width / 2 - 120) + 'px';
  morphTipEl.style.top = (r.top - 96) + 'px';
  morphTipEl.classList.add('show');
}
function hideMorphTip() {
  morphTipEl.classList.remove('show');
}

// Word inspector — click-to-pin panel (persistent, unlike the hover-only
// tooltip above). Only one word is ever "inspected" at a time; clicking a
// new word replaces the panel contents and moves the highlight ring.
const wordInspectorEl = document.getElementById('wordInspector');
const wiBodyEl = document.getElementById('wiBody');
const wiCloseBtn = document.getElementById('wiClose');
let inspectedWordEl = null;

// QUSX-Audio (github.com/dfordev1/qusx-audio) — spoken word-by-word gloss,
// addressed by the same QUSX global word id as morph.id, layout-agnostic
// (same ids across all 10 print editions). Fetched lazily per (lang, surah)
// only when the inspector actually needs it, not prefetched for every surah.
const GLOSS_BASE = {
  en: 'https://quran-wbw-audio.quran-wbw.workers.dev/en/v1/',
  hi: 'https://quran-wbw-audio.quran-wbw.workers.dev/hi/v1/',
};
let glossLang = localStorage.getItem('quran-gloss-lang') || 'en';
const glossIndexCache = {}; // `${lang}:${surah}` -> parsed index json, or null on fetch failure
const glossAudio = new Audio();
async function fetchGlossIndex(lang, surah) {
  const key = lang + ':' + surah;
  if (key in glossIndexCache) return glossIndexCache[key];
  try {
    const res = await fetch(GLOSS_BASE[lang] + 'index/' + String(surah).padStart(3, '0') + '.json');
    if (!res.ok) throw new Error('gloss fetch failed (' + res.status + ')');
    glossIndexCache[key] = await res.json();
  } catch (e) {
    glossIndexCache[key] = null;
  }
  return glossIndexCache[key];
}

let inspectorToken = 0; // guards against a slow fetch from a since-replaced inspection overwriting the panel
function showInspector(wordSpan, morph, v, wIdx) {
  if (inspectedWordEl) inspectedWordEl.classList.remove('inspected');
  inspectedWordEl = wordSpan;
  wordSpan.classList.add('inspected');
  const myToken = ++inspectorToken;
  wiBodyEl.innerHTML =
    '<div class="wi-arabic">' + morph.text + '</div>' +
    '<div class="wi-ref">' + v.surah + ':' + v.ayah + ' &middot; word ' + wIdx + '</div>' +
    '<div class="wi-row"><span class="wi-label">root</span><span class="wi-value">' + (morph.root || '&mdash;') + '</span></div>' +
    '<div class="wi-row"><span class="wi-label">stem</span><span class="wi-value">' + (morph.stem || '&mdash;') + '</span></div>' +
    '<div class="wi-row"><span class="wi-label">lemma</span><span class="wi-value">' + (morph.lemma || '&mdash;') + '</span></div>' +
    (morph.id ? '<div class="wi-row"><span class="wi-label">word id</span><span class="wi-value mono">' + morph.id + '</span></div>' : '') +
    '<div class="wi-gloss">' +
      '<div class="wi-gloss-lang">' +
        '<button class="wi-lang-btn' + (glossLang === 'en' ? ' on' : '') + '" data-lang="en">EN</button>' +
        '<button class="wi-lang-btn' + (glossLang === 'hi' ? ' on' : '') + '" data-lang="hi">HI</button>' +
      '</div>' +
      '<div class="wi-gloss-body">Loading gloss&hellip;</div>' +
    '</div>';
  wordInspectorEl.classList.add('show');
  wiBodyEl.querySelectorAll('.wi-lang-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      glossLang = btn.dataset.lang;
      localStorage.setItem('quran-gloss-lang', glossLang);
      loadGlossFor(v, morph, myToken);
    });
  });
  loadGlossFor(v, morph, myToken);
}
async function loadGlossFor(v, morph, token) {
  const bodyEl = wiBodyEl.querySelector('.wi-gloss-body');
  if (!bodyEl) return; // panel already replaced by a newer inspection
  wiBodyEl.querySelectorAll('.wi-lang-btn').forEach(b => b.classList.toggle('on', b.dataset.lang === glossLang));
  if (!morph.id) { bodyEl.textContent = 'No gloss (ayah-number token, not a word)'; return; }
  bodyEl.textContent = 'Loading gloss…';
  const idx = await fetchGlossIndex(glossLang, v.surah);
  if (token !== inspectorToken) return; // superseded by a newer word click while the fetch was in flight
  if (!idx) { bodyEl.textContent = 'Gloss unavailable (fetch failed)'; return; }
  const clipId = idx.words[String(morph.id)];
  if (!clipId) { bodyEl.textContent = 'No gloss for this word'; return; }
  const printed = idx.text[clipId];
  const spoken = idx.spoken && idx.spoken[clipId];
  bodyEl.innerHTML =
    '<div class="wi-gloss-text">' + printed + '</div>' +
    (spoken ? '<div class="wi-gloss-spoken">spoken: &ldquo;' + spoken + '&rdquo;</div>' : '') +
    '<button class="wi-play-btn" id="wiPlayBtn">&#9658; Play</button>';
  bodyEl.querySelector('#wiPlayBtn').addEventListener('click', () => {
    audio.pause(); // avoid overlapping the main recitation
    glossAudio.src = idx.base + 'audio/' + clipId + '.opus';
    glossAudio.play();
  });
}
function hideInspector() {
  wordInspectorEl.classList.remove('show');
  if (inspectedWordEl) inspectedWordEl.classList.remove('inspected');
  inspectedWordEl = null;
}
wiCloseBtn.addEventListener('click', hideInspector);

function clearHighlights() {
  document.querySelectorAll('.letter.lit').forEach(el => el.classList.remove('lit'));
  document.querySelectorAll('.word.active-word').forEach(el => el.classList.remove('active-word'));
}

function verseAtMs(ms) {
  for (let i = 0; i < VERSES.length; i++) {
    const v = VERSES[i];
    if (ms >= v.source_offset_ms && ms < v.source_offset_ms + v.duration_ms) return i;
  }
  // fallback: last verse whose offset has passed
  for (let i = VERSES.length - 1; i >= 0; i--) {
    if (ms >= VERSES[i].source_offset_ms) return i;
  }
  return 0;
}

function updateHighlight() {
  const ms = audio.currentTime * 1000;
  const idx = verseAtMs(ms);
  if (idx !== currentVerseIdx) {
    currentVerseIdx = idx;
    clearHighlights();
    refreshScrubber(idx);
    refreshInfoBar(idx);
    scrollToPlayback(idx);
  }

  const v = VERSES[currentVerseIdx];
  if (!v) return;

  // Letter-level lighting for Letter + Word hybrid page layout.
  if (mode === 'letter' || mode === 'word') {
    document.querySelectorAll('.mushaf-pages .word[data-ayah="' + v.ayah + '"] .letter').forEach(el => {
      const s = +el.dataset.start, e = +el.dataset.end;
      let active = ms >= s && ms < e;
      if (!active && el.dataset.extraWindows) {
        active = JSON.parse(el.dataset.extraWindows).some(([a, b]) => ms >= a && ms < b);
      }
      el.classList.toggle('lit', active);
      // Mark-only ghosts inherit glow onto the base letter they attach to.
      if (el.dataset.attachPrev && el.previousElementSibling) {
        if (active) el.previousElementSibling.classList.add('lit');
      }
    });
  }

  if (mode === 'letter') {
    document.querySelectorAll('.mushaf-pages .word.active-word').forEach(el => el.classList.remove('active-word'));
    return;
  }

  // Word + Mushaf: highlight the active word glyph/span on the page.
  let activeWord = null;
  for (const [wIdx, s, e] of v.words) {
    if (ms - v.source_offset_ms >= s && ms - v.source_offset_ms < e) { activeWord = wIdx; break; }
  }
  document.querySelectorAll('.mushaf-pages .word[data-ayah="' + v.ayah + '"]').forEach(el => {
    el.classList.toggle('active-word', activeWord !== null && +el.dataset.word === activeWord);
  });
  document.querySelectorAll('.mushaf-pages .word.active-word').forEach(el => {
    if (el.dataset.ayah !== String(v.ayah)) el.classList.remove('active-word');
  });
}

audio.addEventListener('timeupdate', () => {
  updateHighlight();
  if (audio.duration && !userSeeking) {
    seek.value = (audio.currentTime / audio.duration) * 1000;
  }
  curTimeEl.textContent = fmtTime(audio.currentTime * 1000);
  totTimeEl.textContent = fmtTime((audio.duration || 0) * 1000);
});

audio.addEventListener('play', () => playBtn.innerHTML = '&#10074;&#10074;');
audio.addEventListener('pause', () => playBtn.innerHTML = '&#9658;');
audio.addEventListener('ended', () => playBtn.innerHTML = '&#9658;');

playBtn.addEventListener('click', () => {
  if (audio.paused) audio.play(); else audio.pause();
});

seek.addEventListener('mousedown', () => userSeeking = true);
seek.addEventListener('touchstart', () => userSeeking = true);
seek.addEventListener('change', () => {
  if (audio.duration) audio.currentTime = (seek.value / 1000) * audio.duration;
  userSeeking = false;
});

document.getElementById('modeLetter').addEventListener('click', () => setMode('letter'));
document.getElementById('modeWord').addEventListener('click', () => setMode('word'));
document.getElementById('modeMushaf').addEventListener('click', () => setMode('mushaf'));
const tajweedBtn = document.getElementById('tajweedToggle');
tajweedBtn.addEventListener('click', async () => {
  if (mode !== 'mushaf' || currentLayout !== 'madani-v2') return; // COLRv1 tajweed font only exists for madani-v2
  tajweedOn = !tajweedOn;
  tajweedBtn.classList.toggle('on', tajweedOn);
  if (tajweedOn) {
    const pages = [...new Set(VERSES.map(v => v.page).filter(Boolean))];
    await Promise.all(pages.map(ensureTajweedFont));
  }
  renderMushafPages();
});
function setMode(m) {
  const prev = mode;
  mode = m;
  document.getElementById('modeLetter').classList.toggle('on', m === 'letter');
  document.getElementById('modeWord').classList.toggle('on', m === 'word');
  document.getElementById('modeMushaf').classList.toggle('on', m === 'mushaf');
  // All three modes use the continuous mushaf page shell. Letter/Word render
  // Uthmani letter spans; Mushaf renders QCF glyphs. Rebuild when crossing
  // that boundary (letter content vs glyph content).
  versesEl.style.display = 'none';
  mushafPagesEl.style.display = 'flex';
  tajweedBtn.disabled = m !== 'mushaf' || currentLayout !== 'madani-v2';
  if ((prev === 'mushaf') !== (m === 'mushaf') && VERSES.length) {
    renderMushafPages();
  }
  clearHighlights();
}

// --- Letter-browse mode: step through every letter in the mushaf one at a
// time (like paging through the dataset's letter tier directly) instead of
// continuous playback. Pauses on each letter and plays just its own clip.
let browsing = false;
let browseIdx = 0;
const browseBar = document.getElementById('browseBar');
const browseLetterEl = document.getElementById('browseLetter');
const browseMetaEl = document.getElementById('browseMeta');
const modeBrowseBtn = document.getElementById('modeBrowse');

function enterBrowse() {
  browsing = true;
  audio.pause();
  browseBar.classList.add('on');
  modeBrowseBtn.classList.add('on');
  showBrowseLetter(browseIdx);
}
function exitBrowse() {
  browsing = false;
  browseBar.classList.remove('on');
  modeBrowseBtn.classList.remove('on');
}
function showBrowseLetter(gidx) {
  browseIdx = Math.max(0, Math.min(flatLetters.length - 1, gidx));
  const L = flatLetters[browseIdx];
  browseLetterEl.textContent = L.char;
  browseMetaEl.textContent = L.verse.surah + ':' + L.verse.ayah + ' — letter ' + (browseIdx + 1) + ' / ' + flatLetters.length;

  jumpToVerse(L.verseIdx, /*autoplay*/ false);
  clearHighlights();
  const cell = document.querySelector('.letter[data-gidx="' + browseIdx + '"]');
  if (cell) {
    cell.classList.add('lit');
    cell.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  audio.currentTime = L.startMs / 1000;
  audio.play();
  const stopAt = L.endMs;
  const onTick = () => {
    if (audio.currentTime * 1000 >= stopAt) {
      audio.pause();
      audio.removeEventListener('timeupdate', onTick);
    }
  };
  audio.addEventListener('timeupdate', onTick);
}
document.getElementById('browsePrev').addEventListener('click', () => showBrowseLetter(browseIdx - 1));
document.getElementById('browseNext').addEventListener('click', () => showBrowseLetter(browseIdx + 1));
modeBrowseBtn.addEventListener('click', () => { if (browsing) exitBrowse(); else enterBrowse(); });
document.addEventListener('keydown', (e) => {
  if (!browsing) return;
  if (e.key === 'ArrowLeft') showBrowseLetter(browseIdx + 1);   // RTL: left = next
  if (e.key === 'ArrowRight') showBrowseLetter(browseIdx - 1);  // RTL: right = prev
  if (e.key === 'Escape') exitBrowse();
});
[playBtn, seek].forEach(el => el.addEventListener('click', () => { if (browsing) exitBrowse(); }));

// init
loadSurah(1);
</script>
</body>
</html>
"""

html = html.replace('__SURAH_INDEX_JSON__', surah_index_json)
html = html.replace('__GLYPH_V2_JSON__', glyph_v2_json)
html = html.replace('__RECITERS_JSON__', reciters_json)
html = html.replace('__TRADITION_DIFFS_JSON__', tradition_diffs_json)
with open(os.path.join(_DIR, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(html)
print('written', len(html), 'bytes')
