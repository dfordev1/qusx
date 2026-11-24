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
# QPC V1 glyph codes (same shape as V2) — harvested from Quran.com API
# word_fields=code_v1; pairs with per-page QCF V1 fonts.
glyph_v1_json = open(os.path.join(_DIR, 'qpc_v1_glyphs.json'), encoding='utf-8').read()

# All 36 reciter configs available in the QUA dataset (hetchyy/quranic-
# universal-ayahs), with a readable display name for each — the raw HF
# config slugs are source-tagged machine names (e.g. "..._mp3quran",
# "..._tarteel", "..._qdc"), not meant for display.
reciters = json.load(open(os.path.join(_DIR, 'reciters.json'), encoding='utf-8'))
# Local Al-Hadr juz pack (canonical word alignments + offline opus) — tested
# against the OnX release; appears first in the picker.
reciters = [["local_alhadr", "Al-Hadr (local alignments)"]] + reciters
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
<title>القرآن الكريم — Follow Along</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Amiri+Quran&family=Harmattan:wght@400;500;600;700&family=Lateef:wght@400;500;600;700&family=Mirza:wght@400;500;600;700&family=Noto+Naskh+Arabic:wght@400;500;600&family=Noto+Nastaliq+Urdu:wght@400;500;600&family=Scheherazade+New:wght@400;700&display=swap" rel="stylesheet">
<script>
  // Applied before first paint: explicit localStorage choice wins; otherwise
  // default to light (Madani parchment). Dark is available via the toggle.
  (function () {
    var saved = localStorage.getItem('quran-theme');
    var theme = saved || 'light';
    document.documentElement.setAttribute('data-theme', theme);
  })();
</script>
<style>
  /* Madani mushaf system. Light = cream parchment; dark = dim parchment +
     light ink (not just a green room with the same cream page). */
  :root {
    --reader-size: 32px;
    --reader-leading: 1.42;
    --bg: #090b0d;
    --bg-mid: #101318;
    --surface: #15191e;
    --surface-2: #1b2026;
    --chrome: rgba(13, 16, 20, 0.94);
    --border: #2b323a;
    --text: #f0ede5;
    --text-muted: #9fa6ad;
    --accent: #d8b861;
    --accent-2: #b99338;
    --accent-soft: rgba(216, 184, 97, 0.16);
    --frame: #bfa253;
    --frame-inner: #657a70;
    --page: #111418;
    --page-edge: #1b2025;
    --ink: #f3f0e8;
    --ink-muted: #8f969d;
    --shadow: 0 18px 54px rgba(0,0,0,0.48);
    --bg-glow: rgba(216, 184, 97, 0.045);
    --page-grain: rgba(255,255,255,0.012);
    --page-sheen: rgba(255,255,255,0.022);
  }
  :root[data-theme="light"] {
    --bg: #d9c9a8;
    --bg-mid: #e2d4b6;
    --surface: #f4ecd8;
    --surface-2: #efe4cc;
    --chrome: rgba(244, 236, 216, 0.94);
    --border: #c9b88a;
    --text: #1c1810;
    --text-muted: #6a6254;
    --accent: #9a7a28;
    --accent-2: #7a5f1e;
    --accent-soft: rgba(154, 122, 40, 0.16);
    --frame: #a8872e;
    --frame-inner: #2f5d45;
    --page: #f4ecd8;
    --page-edge: #e5d7b8;
    --ink: #1c1810;
    --ink-muted: #6a6254;
    --shadow: 0 12px 36px rgba(40, 30, 12, 0.18);
    --bg-glow: rgba(154, 122, 40, 0.12);
    --page-grain: rgba(80, 60, 20, 0.015);
    --page-sheen: rgba(255,255,255,0.18);
  }
  /* UthmanicHafs (QPC) is kept for bismillah / morph tips, but Letter/Word
     mode prefers Scheherazade New: UthmanicHafs Ver18 paints U+06DF/U+06E0
     (small high rounded zero on silent alif, etc.) as a wide spacing
     dotted-circle tofu instead of a combining sifr above the base letter.
     Scheherazade shapes those marks correctly. QCF mushaf glyph fonts stay
     Mushaf-mode only — each "character" is a whole precomposed word. */
  @font-face {
    font-family: 'UthmanicHafs';
    src: url('https://verses.quran.foundation/fonts/quran/hafs/uthmanic_hafs/UthmanicHafs1Ver18.woff2') format('woff2');
    font-display: swap;
  }
  /* IndoPak / Nastaleeq print faces (Unicode — no per-page PUA glyph map). */
  @font-face {
    font-family: 'IndoPakNastaleeq';
    src: url('https://static-cdn.tarteel.ai/qul/fonts/nastaleeq/Hanafi/normal-v4.2.2/with-waqf-lazmi/font.woff2') format('woff2');
    font-display: swap;
  }
  @font-face {
    font-family: 'KFGQPCNastaleeq';
    src: url('https://static-cdn.tarteel.ai/qul/fonts/nastaleeq/KFGQPCNastaleeq-Regular.woff2') format('woff2');
    font-display: swap;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background:
      radial-gradient(ellipse 1000px 560px at 50% -8%, var(--bg-glow), transparent),
      linear-gradient(180deg, var(--bg-mid) 0%, var(--bg) 55%, var(--bg) 100%);
    color: var(--text);
    font-family: "Segoe UI", "Traditional Arabic", Tahoma, sans-serif;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px 12px 108px;
    transition: background-color 0.25s, color 0.25s;
  }
  .brand {
    text-align: center;
    margin: 2px 0 12px;
  }
  .brand-ar {
    display: block;
    font-family: 'UthmanicHafs', "Traditional Arabic", "Scheherazade New", serif;
    font-size: 30px;
    color: var(--accent);
    line-height: 1.35;
    margin: 0;
    text-shadow: 0 1px 0 color-mix(in srgb, var(--frame) 25%, transparent);
  }
  .brand-en {
    display: block;
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-top: 3px;
    opacity: 0.9;
  }
  .about-wrap {
    margin: 2px 0 10px;
    text-align: center;
    max-width: 520px;
  }
  .about-wrap summary {
    cursor: pointer;
    list-style: none;
    font-size: 11px;
    color: var(--text-muted);
    letter-spacing: 0.06em;
  }
  .about-wrap summary::-webkit-details-marker { display: none; }
  .about-wrap summary:hover { color: var(--accent); }
  .about-wrap[open] summary { margin-bottom: 6px; color: var(--accent); }
  .subtitle {
    color: var(--text-muted);
    font-size: 12px;
    margin: 0;
    text-align: center;
    line-height: 1.55;
  }
  .subtitle a { color: var(--accent); text-decoration: none; }
  .verses {
    width: 100%;
    max-width: 820px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .verse {
    background: var(--page);
    color: var(--ink);
    border: 1px solid var(--page-edge);
    border-radius: 8px;
    padding: 22px 24px;
    box-shadow: var(--shadow);
    transition: border-color 0.2s;
    cursor: pointer;
    direction: rtl;
  }
  .verse:hover { border-color: var(--frame); }
  .verse.active { border-color: var(--frame); box-shadow: 0 0 0 1px var(--frame), var(--shadow); }
  .verse-num {
    display: inline-block;
    font-size: 11px;
    color: var(--ink-muted);
    font-family: "Scheherazade New", serif;
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
    max-width: 820px;
  }
  .qusx-break .ln { flex: 1; height: 1px; background: var(--frame); opacity: 0.45; }
  .qusx-break .lbl {
    font-family: "Scheherazade New", serif;
    font-size: 11px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--frame);
    white-space: nowrap;
  }
  .qusx-break.page .lbl { color: var(--accent); }
  .qusx-break.minor { margin: 2px 4px 6px; opacity: 0.55; }
  .qusx-break.minor .lbl { font-size: 10px; }
  .ayah-pin {
    display: inline-flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;
    min-width: 1.55em;
    height: 1.55em;
    margin: 0 0.28em;
    border: 1.5px solid var(--frame);
    border-radius: 50%;
    font-family: "Scheherazade New", "Traditional Arabic", serif;
    font-size: 0.42em;
    color: var(--ink);
    -webkit-text-fill-color: var(--ink);
    background:
      radial-gradient(circle at 50% 45%, transparent 55%, var(--accent-soft) 56%),
      var(--page);
    vertical-align: 0.18em;
    box-shadow: inset 0 0 0 1px rgba(184, 149, 58, 0.35);
  }
  .mushaf-num-glyph {
    display: inline-block;
    flex: 0 0 auto;
    color: var(--frame);
    -webkit-text-fill-color: var(--frame);
    margin: 0;
  }
  .qusx-ruku {
    direction: ltr;
    width: 100%;
    max-width: 820px;
    text-align: center;
    margin: 2px 4px 8px;
    font-family: "Scheherazade New", serif;
    font-size: 11px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--frame-inner);
    opacity: 0.85;
  }
  .bismillah {
    width: 100%;
    text-align: center;
    font-family: 'UthmanicHafs', "Traditional Arabic", "Scheherazade New", serif;
    font-size: calc(var(--reader-size) * .88);
    line-height: 1.55;
    color: var(--frame);
    margin: 8px 4px 20px;
    padding: 10px 8px 14px;
    overflow: visible;
    border-bottom: 1px solid rgba(184, 149, 58, 0.28);
  }
  .bismillah .bismillah-word {
    display: inline;
    cursor: pointer;
    border-radius: 4px;
    padding: 2px 3px;
    transition: color 0.15s, background 0.15s, box-shadow 0.15s;
  }
  .qusx-line-break { flex-basis: 100%; height: 0; }
  .sajda-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: "Scheherazade New", serif;
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 999px;
    border: 1px solid var(--frame);
    color: var(--frame);
    background: var(--accent-soft);
    margin-left: 8px;
    direction: ltr;
  }
  .verse-text {
    font-family: 'Scheherazade New', "Traditional Arabic", 'UthmanicHafs', serif;
    font-size: var(--reader-size);
    line-height: var(--reader-leading);
    letter-spacing: 0;
    word-spacing: 0;
    font-kerning: normal;
    font-variant-ligatures: common-ligatures contextual;
    font-feature-settings: "kern" 1, "liga" 1, "calt" 1, "rlig" 1;
    color: var(--ink);
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
    max-width: 820px;
    flex-direction: column;
    gap: 18px;
  }
  .mushaf-pages.page-mode {
    gap: 0;
  }
  .mushaf-pages.page-mode .mushaf-page {
    display: none;
  }
  .mushaf-pages.page-mode .mushaf-page.is-visible {
    display: block;
    animation: pageIn 0.28s ease;
  }
  @keyframes pageIn {
    from { opacity: 0.55; transform: translateY(6px); }
    to { opacity: 1; transform: none; }
  }
  .page-nav {
    display: none;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin: 6px 0 10px;
    padding: 6px 12px;
    font-family: "Scheherazade New", "Traditional Arabic", serif;
    color: var(--frame);
    background: color-mix(in srgb, var(--chrome) 88%, transparent);
    border: 1px solid color-mix(in srgb, var(--frame) 28%, transparent);
    border-radius: 999px;
  }
  .page-nav.visible { display: flex; }
  .page-nav button {
    background: transparent;
    border: 1px solid color-mix(in srgb, var(--frame) 40%, transparent);
    color: var(--frame);
    border-radius: 50%;
    width: 30px;
    height: 30px;
    padding: 0;
    font-size: 18px;
    cursor: pointer;
    line-height: 1;
    transition: background 0.15s, border-color 0.15s, transform 0.12s;
  }
  .page-nav button:hover:not(:disabled) {
    background: color-mix(in srgb, var(--frame) 14%, transparent);
    transform: scale(1.04);
  }
  .page-nav button:disabled { opacity: 0.32; cursor: default; }
  .page-nav .page-label {
    font-size: 12px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    min-width: 8em;
    text-align: center;
    color: var(--ink-muted);
  }
  .mushaf-page {
    --page-ink: var(--ink);
    position: relative;
    /* visible: QCF / Uthmani glyphs (meem, nuun, etc.) overhang the em box */
    overflow: visible;
    background:
      linear-gradient(180deg, var(--page-sheen), transparent 40%),
      repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        var(--page-grain) 2px,
        var(--page-grain) 3px
      ),
      linear-gradient(165deg, var(--page) 0%, var(--page-edge) 100%);
    color: var(--ink);
    border: 2px solid var(--frame);
    border-radius: 6px;
    padding: 22px 22px 28px;
    box-shadow:
      inset 0 0 0 1px var(--frame-inner),
      inset 0 0 0 4px var(--page),
      inset 0 0 0 5px color-mix(in srgb, var(--frame) 55%, transparent),
      var(--shadow);
  }
  .mushaf-page-header {
    direction: ltr;
    text-align: center;
    font-family: "Scheherazade New", "Traditional Arabic", serif;
    font-size: 12px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--frame);
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid color-mix(in srgb, var(--frame) 32%, transparent);
  }
  .mushaf-text {
    direction: rtl;
    font-size: var(--reader-size);
    line-height: var(--reader-leading);
    letter-spacing: 0;
    text-align: start;
    color: var(--ink);
    max-width: 100%;
    overflow: visible;
    padding-inline: 2px;
  }
  .mushaf-line {
    display: flex;
    flex-wrap: nowrap;
    align-items: baseline;
    justify-content: space-between;
    direction: rtl;
    width: 100%;
    max-width: 100%;
    overflow: visible;
    box-sizing: border-box;
    padding-block: 0.18em;
  }
  .mushaf-line.is-short {
    justify-content: flex-start;
    gap: 0.35em;
  }
  /* Letter/Word hybrid: same page/line shell as Mushaf, but real Unicode
     letters (Scheherazade) so phoneme highlighting + Quranic marks work. */
  .mushaf-text.with-letters {
    font-family: 'Scheherazade New', "Traditional Arabic", 'UthmanicHafs', serif;
  }
  .mushaf-text.is-nastaleeq {
    font-size: var(--reader-size);
    line-height: var(--reader-leading);
  }
  .mushaf-line .word {
    display: inline-block;
    flex: 0 1 auto;
    white-space: nowrap;
    /* Do not clip glyph overhang (meem bowls, nuun tails, dots). */
    overflow: visible;
    min-width: 0;
  }
  /* All reading modes inherit the selected QUSX layout's authentic
     line composition: exact word membership, full-line justification and
     short-line treatment. Do not centre or force-align Unicode text. */
  .mushaf-line .word .letter {
    display: inline;
    margin: 0;
    padding: 0;
    letter-spacing: 0;
    word-spacing: 0;
    font-kerning: normal;
    font-variant-ligatures: common-ligatures contextual;
    font-feature-settings: "kern" 1, "liga" 1, "calt" 1, "rlig" 1;
  }
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
    border-radius: .18em;
    padding: 0;
    margin: 0;
    overflow: visible;
    transition: color 0.15s, text-shadow 0.15s, background 0.15s, box-shadow 0.15s;
    cursor: pointer;
  }
  .letter {
    margin: 0;
    padding: 0;
    letter-spacing: 0;
    word-spacing: 0;
    transition: color 0.08s, text-shadow 0.1s;
  }
  /* Active phoneme (Letter mode): soft tint + light glow. */
  .letter.lit {
    color: var(--accent);
    background: transparent;
    border-radius: 0;
    text-shadow: 0 0 5px color-mix(in srgb, var(--accent) 50%, transparent);
    filter: none;
  }
  .word {
    display: inline; /* preserve Arabic shaping and immutable line metrics */
    border-radius: .18em;
    padding: 0;
    box-decoration-break: clone;
    -webkit-box-decoration-break: clone;
    transition: box-shadow 0.15s, text-shadow 0.15s, color 0.15s, background 0.15s;
  }
  .word:hover { box-shadow: 0 0 0 1px rgba(184, 149, 58, 0.35); }
  /* Defaults overridden per follow-mode-* on body. */
  .word.active-word,
  .mushaf-glyph.active-word,
  .bismillah .bismillah-word.active-word {
    filter: none;
    transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease, text-shadow 0.12s ease;
  }
  /* Word mode: light boxed highlight in the accent color. */
  body.follow-mode-word .word.active-word,
  body.follow-mode-word .mushaf-glyph.active-word,
  body.follow-mode-word .bismillah .bismillah-word.active-word {
    background: var(--accent-soft);
    color: var(--accent);
    text-shadow: none;
    box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--accent) 30%, transparent);
  }
  /* Letter mode: very light word wash; current letter keeps its glow. */
  body.follow-mode-letter .word.active-word,
  body.follow-mode-letter .bismillah .bismillah-word.active-word {
    background: color-mix(in srgb, var(--accent) 11%, transparent);
    color: inherit;
    text-shadow: none;
    box-shadow: none;
  }
  /* Mushaf: same light box as word mode for the active glyph. */
  body.follow-mode-mushaf .mushaf-glyph.active-word,
  body.follow-mode-mushaf .bismillah .bismillah-word.active-word {
    background: var(--accent-soft);
    color: var(--accent);
    text-shadow: none;
    box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--accent) 30%, transparent);
  }
  .controls {
    position: fixed;
    bottom: 12px;
    left: 50%;
    width: min(840px, calc(100% - 24px));
    transform: translateX(-50%);
    background: color-mix(in srgb, var(--chrome) 94%, transparent);
    backdrop-filter: blur(22px) saturate(1.15);
    border: 1px solid color-mix(in srgb, var(--border) 86%, transparent);
    border-radius: 18px;
    padding: 7px 10px 9px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    z-index: 40;
    box-shadow: 0 14px 44px rgba(0,0,0,.22);
    transition: transform .32s cubic-bezier(.2,.8,.2,1), opacity .24s ease;
  }
  .controls.is-concealed {
    transform: translate(-50%, calc(100% + 28px));
    opacity: 0;
    pointer-events: none;
  }
  .controls-reveal {
    position: fixed;
    z-index: 39;
    bottom: 9px;
    left: 50%;
    transform: translateX(-50%) translateY(18px);
    width: 44px;
    height: 28px;
    border: 1px solid color-mix(in srgb, var(--border) 75%, transparent);
    border-radius: 999px;
    background: color-mix(in srgb, var(--chrome) 94%, transparent);
    color: var(--text-muted);
    opacity: 0;
    pointer-events: none;
    transition: opacity .2s, transform .25s;
    cursor: pointer;
  }
  .controls-reveal.show {
    opacity: .86;
    pointer-events: auto;
    transform: translateX(-50%) translateY(0);
  }
  .transport-btn {
    width: 30px;
    height: 30px;
    flex: 0 0 auto;
    border: 0;
    border-radius: 50%;
    background: transparent;
    color: var(--text-muted);
    font-size: 22px;
    line-height: 1;
    cursor: pointer;
  }
  .transport-btn:hover { color: var(--accent); background: var(--accent-soft); }
  .scrubber {
    display: flex;
    gap: 3px;
    width: 100%;
    max-width: 820px;
    overflow-x: auto;
    max-height: 28px;
    padding-bottom: 0;
  }
  .scrubber::-webkit-scrollbar { height: 2px; }
  .scrub-btn {
    flex: 1;
    min-width: 26px;
    background: color-mix(in srgb, var(--surface) 55%, transparent);
    border: 1px solid color-mix(in srgb, var(--border) 55%, transparent);
    color: var(--text);
    -webkit-text-fill-color: var(--text);
    border-radius: 3px;
    padding: 2px 2px;
    font-size: 11px;
    font-family: "Scheherazade New", serif;
    cursor: pointer;
    text-align: center;
    white-space: nowrap;
    line-height: 1.2;
    opacity: 0.92;
  }
  .scrub-btn:hover {
    border-color: var(--frame);
    color: var(--accent);
    -webkit-text-fill-color: var(--accent);
    opacity: 1;
  }
  .scrub-btn.active {
    border-color: var(--frame);
    color: var(--accent);
    -webkit-text-fill-color: var(--accent);
    background: var(--accent-soft);
    opacity: 1;
    font-weight: 600;
  }
  .controls-row { display: flex; align-items: center; gap: 8px; width: 100%; max-width: 820px; }
  .info-bar { display: flex; align-items: center; gap: 8px; min-width: 0; max-width: 140px; }
  .info-avatar {
    width: 24px; height: 24px; border-radius: 50%;
    background: var(--accent-soft); color: var(--accent);
    border: 1px solid var(--frame);
    display: flex; align-items: center; justify-content: center;
    font-size: 9px; font-weight: 700; flex-shrink: 0;
  }
  .info-text { line-height: 1.15; min-width: 0; overflow: hidden; }
  .info-name { font-size: 11px; font-weight: 600; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .info-meta { font-size: 9.5px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  button.play-btn {
    background: linear-gradient(145deg, var(--accent), var(--accent-2));
    color: #1a1508;
    border: 1px solid var(--frame);
    border-radius: 50%;
    width: 34px; height: 34px;
    font-size: 13px;
    cursor: pointer;
    flex-shrink: 0;
    box-shadow: 0 2px 8px color-mix(in srgb, var(--accent) 35%, transparent);
    display: flex; align-items: center; justify-content: center;
    transition: transform 0.12s;
  }
  button.play-btn:hover { transform: scale(1.05); }
  button.play-btn:active { transform: scale(0.96); }
  .speed-select {
    flex-shrink: 0;
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 4px 6px;
    font-size: 11px;
    font-family: "Scheherazade New", serif;
    cursor: pointer;
    max-width: 4.2rem;
  }
  .speed-select:hover, .speed-select:focus {
    border-color: var(--frame);
    outline: none;
  }
  input[type=range] { flex: 1; accent-color: var(--accent); height: 18px; }
  .time {
    font-family: "Scheherazade New", serif;
    font-size: 12px;
    color: var(--text);
    -webkit-text-fill-color: var(--text);
    min-width: 34px;
    text-align: center;
    opacity: 0.9;
  }
  .mode-toggle {
    display: flex;
    gap: 3px;
    font-size: 11px;
    flex-shrink: 0;
    border-bottom: none;
    flex-wrap: wrap;
    justify-content: center;
    padding: 2px;
    background: color-mix(in srgb, var(--surface) 70%, transparent);
    border-radius: 12px;
    border: 1px solid color-mix(in srgb, var(--border) 72%, transparent);
  }
  .mode-label {
    align-self: center;
    padding: 0 7px;
    color: var(--text-muted);
    font-size: 8px;
    font-weight: 700;
    letter-spacing: .14em;
    opacity: .72;
  }
  .mode-toggle button {
    background: transparent;
    border: none;
    border-bottom: none;
    margin-bottom: 0;
    color: var(--text-muted);
    border-radius: 9px;
    padding: 5px 11px 6px;
    cursor: pointer;
    transition: color 0.15s, background 0.15s;
  }
  .mode-toggle button:hover { color: var(--text); }
  .experience-toggle { width: min(330px, 100%); }
  .experience-toggle button { flex: 1; min-width: 0; }
  .legacy-mode-controls { display: none !important; }
  .settings-hidden { display: none !important; }
  .mode-toggle button.on {
    color: var(--accent);
    background: var(--accent-soft);
  }
  .tajweed-btn.on {
    color: #2f5d45;
    background: color-mix(in srgb, #2f5d45 14%, transparent);
  }
  :root:not([data-theme="light"]) .tajweed-btn.on {
    color: #7dba95;
    background: color-mix(in srgb, #7dba95 16%, transparent);
  }
  .tajweed-btn:disabled { opacity: 0.34; cursor: not-allowed; }
  .settings-action {
    width: 100%;
    margin-top: 3px;
    padding: 8px 10px;
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-muted);
    background: transparent;
    cursor: pointer;
  }
  .settings-action:hover { color: var(--accent); border-color: var(--frame); }
  .script-row select { font-weight: 600; }
  .typography-panel {
    margin-top: 2px;
    padding: 11px 12px 12px;
    border: 1px solid color-mix(in srgb, var(--border) 82%, transparent);
    border-radius: 12px;
    background: color-mix(in srgb, var(--surface-2) 72%, transparent);
    direction: ltr;
  }
  .type-panel-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 9px;
    color: var(--text);
    font-size: 11px;
    font-weight: 650;
  }
  .type-panel-head button {
    border: 0;
    padding: 3px 6px;
    background: transparent;
    color: var(--text-muted);
    font-size: 10px;
    cursor: pointer;
  }
  .type-panel-head button:hover { color: var(--accent); }
  .type-control {
    display: grid;
    grid-template-columns: 48px minmax(100px, 1fr) 58px;
    align-items: center;
    gap: 9px;
    min-height: 34px;
    color: var(--text-muted);
    font-size: 10px;
  }
  .type-control > input[type=range] { width: 100%; margin: 0; }
  .type-control > strong { text-align: right; color: var(--accent); font-size: 10px; }
  .number-unit {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 2px;
    color: var(--accent);
  }
  .number-unit input {
    width: 39px;
    padding: 3px 4px;
    border: 0;
    border-bottom: 1px solid var(--border);
    border-radius: 0;
    background: transparent;
    color: var(--accent);
    text-align: right;
    font: inherit;
    outline: none;
  }
  .number-unit input:focus { border-color: var(--accent); }
  .number-unit small { font-size: 9px; }
  .about-wrap, .credit { display: none; }
  .credit {
    color: var(--text-muted);
    font-size: 11px;
    margin-top: 18px;
    text-align: center;
    max-width: 560px;
    line-height: 1.55;
    opacity: 0.75;
  }
  .credit a { color: var(--accent); text-decoration: none; }

  .browse-bar {
    display: none;
    align-items: center;
    justify-content: center;
    gap: 16px;
    width: 100%;
    max-width: 820px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px 16px;
  }
  .browse-bar.on { display: flex; }
  .browse-step {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 4px;
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
  .browse-meta { font-size: 11px; color: var(--text-muted); font-family: "Scheherazade New", serif; text-align: center; flex: 1; }

  .word.has-morph { cursor: help; }
  .morph-tip {
    position: fixed;
    z-index: 50;
    background: var(--page);
    color: var(--ink);
    border: 1px solid var(--frame);
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 13px;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.12s;
    box-shadow: var(--shadow);
    max-width: 240px;
    direction: rtl;
  }
  .morph-tip.show { opacity: 1; }
  .morph-tip .mt-row { display: flex; justify-content: space-between; gap: 12px; margin-top: 4px; direction: ltr; }
  .morph-tip .mt-label { color: var(--ink-muted); font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.04em; }
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
    bottom: 100px;
    width: 280px;
    max-width: calc(100vw - 40px);
    background: var(--page);
    color: var(--ink);
    border: 1px solid var(--frame);
    border-radius: 8px;
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
    color: var(--ink-muted);
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
    font-family: "Scheherazade New", serif;
    font-size: 11px;
    color: var(--ink-muted);
    margin-bottom: 12px;
  }
  .word-inspector .wi-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 12px;
    padding: 6px 0;
    border-top: 1px solid var(--page-edge);
    direction: ltr;
  }
  .word-inspector .wi-label {
    color: var(--ink-muted);
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
  .word.inspected { box-shadow: 0 0 0 2px var(--frame) !important; }
  .wi-gloss {
    direction: ltr;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--page-edge);
  }
  .wi-gloss-lang { display: flex; gap: 6px; margin-bottom: 8px; }
  .wi-lang-btn {
    background: transparent;
    border: 1px solid var(--page-edge);
    color: var(--ink-muted);
    border-radius: 4px;
    padding: 3px 10px;
    font-size: 11px;
    cursor: pointer;
  }
  .wi-lang-btn.on { color: var(--accent); border-color: var(--frame); background: var(--accent-soft); }
  .wi-gloss-body { font-size: 13px; color: var(--ink-muted); min-height: 18px; }
  .wi-gloss-text { color: var(--ink); font-size: 14px; margin-bottom: 4px; }
  .wi-gloss-spoken { font-size: 11px; font-style: italic; margin-bottom: 8px; }
  .wi-play-btn {
    background: var(--accent-soft);
    border: 1px solid var(--frame);
    color: var(--accent);
    border-radius: 4px;
    padding: 5px 12px;
    font-size: 12px;
    cursor: pointer;
  }
  .wi-play-btn:hover { background: var(--accent); color: var(--page); }
  @media (max-width: 640px) {
    .word-inspector {
      left: 10px; right: 10px; bottom: 96px; width: auto;
    }
    .mushaf-page {
      padding: 14px 10px 18px;
      border-width: 1.5px;
      box-shadow:
        inset 0 0 0 1px var(--frame-inner),
        inset 0 0 0 3px var(--page),
        inset 0 0 0 4px color-mix(in srgb, var(--frame) 50%, transparent),
        var(--shadow);
    }
    .mushaf-text,
    .mushaf-text.is-nastaleeq {
      font-size: var(--reader-size);
      line-height: var(--reader-leading);
    }
    .bismillah { font-size: 20px; margin: 4px 0 12px; line-height: 2.3; }
    .brand-ar { font-size: 22px; }
    .info-avatar { display: none; }
    .info-bar { max-width: 96px; }
    .surah-picker { max-width: 100%; }
    .chrome-primary { padding: 5px 6px; gap: 4px; }
    .chrome-primary select { padding: 5px 6px; font-size: 12px; }
    .chrome-primary #browseModeSelect { max-width: 4.6rem; font-size: 11px; }
    .chrome-icon-btn { width: 30px; height: 30px; }
    .controls { padding: 4px 8px 6px; gap: 3px; }
    .mode-toggle button { padding: 2px 6px 3px; font-size: 10px; }
    body { padding: 10px 8px 100px; }
  }

  @media (max-width: 420px) {
    .scrubber { display: none; }
    .info-bar { display: none; }
  }

  .surah-picker {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 0;
    margin-bottom: 6px;
    max-width: 520px;
    width: 100%;
    padding: 0;
    background: transparent;
    border: none;
    border-radius: 0;
    backdrop-filter: none;
  }
  .chrome-primary {
    display: flex;
    flex-wrap: nowrap;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 6px 8px;
    background: var(--chrome);
    border: 1px solid var(--border);
    border-radius: 10px;
    backdrop-filter: blur(10px);
  }
  .chrome-primary select {
    background: transparent;
    color: var(--text);
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 8px;
    font-size: 13px;
    font-family: "Scheherazade New", "Traditional Arabic", serif;
    max-width: none;
    min-width: 0;
    cursor: pointer;
    transition: border-color 0.15s, background 0.15s;
  }
  .chrome-primary #browseModeSelect {
    flex: 0 0 auto;
    max-width: 5.5rem;
    font-size: 12px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--text-muted);
  }
  .chrome-primary #surahSelect,
  .chrome-primary #juzSelect {
    flex: 1 1 auto;
    font-size: 14px;
    text-align: center;
  }
  .chrome-primary select:hover:not(:disabled),
  .chrome-primary select:focus:not(:disabled) {
    border-color: color-mix(in srgb, var(--frame) 45%, transparent);
    background: var(--surface);
    outline: none;
  }
  .chrome-primary select:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }
  .chrome-icon-btn {
    background: transparent;
    border: 1px solid transparent;
    color: var(--text-muted);
    border-radius: 6px;
    width: 32px;
    height: 32px;
    font-size: 14px;
    cursor: pointer;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: border-color 0.15s, color 0.15s, background 0.15s;
  }
  .chrome-icon-btn:hover {
    color: var(--text);
    border-color: color-mix(in srgb, var(--frame) 40%, transparent);
    background: var(--surface);
  }
  .chrome-more-btn[aria-expanded="true"] {
    color: var(--accent);
    border-color: color-mix(in srgb, var(--frame) 45%, transparent);
    background: var(--accent-soft);
  }
  .chrome-more {
    display: none;
    flex-direction: column;
    gap: 8px;
    margin-top: 6px;
    padding: 10px 12px 12px;
    background: var(--chrome);
    border: 1px solid var(--border);
    border-radius: 10px;
    backdrop-filter: blur(10px);
  }
  .chrome-more.open { display: flex; }
  .chrome-more-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px 10px;
  }
  .chrome-more-row label {
    flex: 0 0 4.5rem;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
  }
  .chrome-more-row select {
    flex: 1 1 10rem;
    min-width: 0;
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    cursor: pointer;
  }
  .chrome-more-row select:hover:not(:disabled),
  .chrome-more-row select:focus:not(:disabled) {
    border-color: var(--frame);
    outline: none;
  }
  .chrome-more-row select:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }
  .chrome-toggle-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px 16px;
    padding-top: 2px;
  }
  .chrome-toggle-row label {
    flex: 0 1 auto;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    letter-spacing: 0;
    text-transform: none;
    color: var(--text);
    cursor: pointer;
    user-select: none;
  }
  .chrome-toggle-row input {
    accent-color: var(--accent);
    width: 14px;
    height: 14px;
    margin: 0;
  }
  body:not(.grammar-hover-on) .word.has-morph { cursor: inherit; }
  body.grammar-click-on .word.has-morph { cursor: pointer; }
  .theme-toggle { /* class kept for existing JS / theme button */ }
  .load-status {
    color: var(--text-muted);
    font-size: 11px;
    min-height: 0;
    margin: 4px 0 0;
    text-align: center;
    opacity: 0.85;
    max-width: 520px;
    line-height: 1.35;
  }
  .load-status:empty { display: none; }
  .load-status.error { color: #c45a4a; opacity: 1; }
  .boot-hint {
    color: var(--accent);
    font-family: "Scheherazade New", "Traditional Arabic", serif;
    font-size: 15px;
    margin: 24px 0;
    text-align: center;
    letter-spacing: 0.04em;
  }
  .boot-hint.done { display: none; }
  .tradition-info {
    font-family: "Scheherazade New", serif;
    font-size: 10px;
    color: var(--text-muted);
    opacity: 0.65;
    margin: 4px 0 0;
    max-width: 520px;
    text-align: center;
    line-height: 1.4;
  }
  .tradition-info:empty { display: none; }
  .tradition-info.diverges { color: var(--accent); opacity: 0.9; }

  /* Quran.com-inspired reader chrome, independent implementation.
     Leave the page/word layout, glyph fonts and timing renderer intact. */
  :root { --reader-header: 64px; --reader-nav: 280px; }
  :root[data-theme="light"] {
    --bg:#fff; --bg-mid:#fff; --surface:#fff; --surface-2:#f5f7f8;
    --chrome:rgba(255,255,255,.98); --border:#e2e6e9;
    --text:#20282d; --text-muted:#657179; --accent:#237c72;
    --accent-2:#17645b; --accent-soft:#237c7218; --frame:#237c72;
    --frame-inner:#58746c; --shadow:0 2px 12px #0000000a; --bg-glow:transparent;
  }
  :root:not([data-theme="light"]) {
    --bg:#171d21; --bg-mid:#171d21; --surface:#20282d; --surface-2:#29343a;
    --chrome:rgba(32,40,45,.98); --border:#39434a; --text:#f1f4f5;
    --text-muted:#aab7be; --accent:#83d3c6; --accent-2:#65b9ad;
    --accent-soft:#83d3c620; --bg-glow:transparent;
  }
  body { background:var(--bg); padding:calc(var(--reader-header) + 20px) 24px 150px; }
  #readerHeader { position:fixed; top:0; left:0; right:0; height:var(--reader-header);
    z-index:60; display:flex; align-items:center; justify-content:space-between;
    gap:14px; padding:0 20px; background:var(--surface); border-bottom:1px solid var(--border); direction:ltr; }
  #readerHeader .brand { display:flex; flex-direction:column; align-items:flex-start; margin:0; flex-shrink:0; }
  #readerHeader .brand-ar { font-size:23px; line-height:1.15; text-shadow:none; }
  #readerHeader .brand-en { font-family:system-ui,sans-serif; font-size:10px; letter-spacing:.12em; }
  #readerHeader .surah-picker { width:min(560px,65%); max-width:none; margin:0; position:relative; direction:ltr; }
  #readerHeader .chrome-primary { background:none; border:none; padding:0; }
  #readerHeader .chrome-primary select { font-family:system-ui,sans-serif; font-size:13px; }
  #readerHeader .chrome-more { position:absolute; right:0; top:calc(100% + 12px);
    width:min(420px,calc(100vw - 28px)); max-height:calc(100dvh - 100px);
    overflow:auto; background:var(--surface); box-shadow:0 10px 40px #0003; }
  #readerHeader .chrome-more-row label { flex-basis:6rem; }
  .reader-nav-toggle, .reader-action, .reader-nav-tabs button {
    background:var(--surface); border:1px solid var(--border); border-radius:8px;
    color:var(--text); font:500 13px/1.3 system-ui,sans-serif; cursor:pointer; padding:9px 12px; }
  .reader-nav-toggle { min-width:40px; font-size:20px; padding:5px 10px; }
  .reader-nav-toggle:hover,.reader-action:hover,.reader-nav-tabs button:hover { border-color:var(--accent); color:var(--accent); }
  #readerSidebar { position:fixed; top:var(--reader-header); left:0; bottom:0; width:var(--reader-nav);
    background:var(--surface); border-right:1px solid var(--border); z-index:50;
    padding:18px 14px 150px; overflow:auto; direction:ltr; font:14px/1.5 system-ui,sans-serif; }
  #readerSidebar[hidden],#readerShade[hidden] { display:none; }
  #readerSidebar h2 { font-size:16px; margin:0 0 14px; }
  .reader-nav-tabs { display:flex; gap:5px; margin-bottom:12px; }
  .reader-nav-tabs button { flex:1; padding:8px 5px; }
  .reader-nav-tabs button[aria-pressed="true"] { color:var(--accent); background:var(--accent-soft); border-color:var(--accent); }
  #readerSearch { display:block; width:100%; padding:10px; border:1px solid var(--border);
    border-radius:8px; background:var(--surface-2); color:var(--text); font:inherit; margin-bottom:8px; }
  #readerNavList { display:flex; flex-direction:column; gap:2px; }
  #readerNavList button { display:flex; align-items:center; gap:10px; width:100%; border:none;
    border-radius:7px; padding:9px; background:transparent; color:var(--text); text-align:left; cursor:pointer; font:inherit; }
  #readerNavList button:hover,#readerNavList button[aria-current="true"] { background:var(--accent-soft); color:var(--accent); }
  #readerNavList button:disabled { opacity:.45; cursor:not-allowed; }
  .reader-nav-num { flex:0 0 28px; font-size:12px; color:var(--text-muted); }
  .reader-nav-ar { margin-left:auto; font:19px "Noto Naskh Arabic",serif; direction:rtl; }
  .reader-nav-help { color:var(--text-muted); font-size:12px; padding:8px; }
  #readerHeading { width:100%; max-width:820px; text-align:center; direction:ltr; padding:18px 0 20px; margin:0 0 8px; border-bottom:1px solid var(--border); }
  #readerHeading h1 { margin:4px 0; font:650 27px/1.3 system-ui,sans-serif; }
  #readerHeading .reader-ar-title { font:32px/1.6 "Noto Naskh Arabic",serif; color:var(--text); }
  #readerHeading p { margin:5px 0 16px; color:var(--text-muted); font:13px system-ui,sans-serif; }
  .reader-actions { display:flex; align-items:center; justify-content:center; flex-wrap:wrap; gap:8px; }
  .reader-actions a { text-decoration:none; }
  .reader-jump { display:flex; align-items:center; gap:5px; }
  #readerAyah { width:66px; padding:8px 5px; font:inherit; background:var(--surface-2); color:var(--text); border:1px solid var(--border); border-radius:7px; }
  #readerNotice { min-height:1.2em; color:var(--text-muted); font:12px system-ui,sans-serif; margin-top:8px; }
  .controls { left:50%; bottom:0; width:100%; max-width:none; border-radius:0; border-width:1px 0 0;
    background:var(--surface); padding:8px 18px 12px; box-shadow:0 -2px 12px #0000000d; }
  .controls .scrubber,.controls .controls-row { max-width:920px; }
  .controls-reveal { display:none!important; }
  :focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
  @media(min-width:900px) {
    body.reader-nav-open { padding-left:calc(var(--reader-nav) + 24px); }
  }
  @media(max-width:899px) {
    #readerHeader { padding:0 10px; gap:7px; }
    #readerHeader .brand-ar { font-size:18px; }
    #readerHeader .brand-en { display:none; }
    #readerHeader .surah-picker { width:auto; flex:1; min-width:0; }
    #readerHeader .chrome-primary { gap:3px; }
    #readerHeader .chrome-primary #browseModeSelect { display:none; }
    #readerHeader .chrome-primary #surahSelect,#readerHeader .chrome-primary #juzSelect { min-width:0; width:100%; font-size:12px; padding:5px 2px; }
    #readerSidebar { width:min(320px,88vw); bottom:0; box-shadow:10px 0 30px #0002; }
    #readerShade { position:fixed; inset:var(--reader-header) 0 0; background:#0005; z-index:45; }
    body { padding:calc(var(--reader-header) + 10px) 10px 150px; }
    #readerHeading { padding:12px 0; }
    #readerHeading h1 { font-size:22px; }
    .controls { padding:6px 8px 10px; }
  }
  @media(max-width:400px) { #readerHeader .brand { display:none; } }


  /* Reader v2: a distinct verse/translation view, not a reskinned printed page. */
  :root{--reader-header:56px;--reader-nav:245px}
  :root[data-theme="light"]{--bg:#fff;--surface:#fff;--surface-2:#f5f6f7;--border:#e6e8eb;--text:#1f2125;--text-muted:#666c75;--accent:#2ca4ab;--accent-soft:#2ca4ab12;--frame:#2ca4ab;--ink:#1f2125}
  :root:not([data-theme="light"]){--bg:#1b1b1d;--surface:#222225;--surface-2:#2b2b2e;--border:#39393e;--text:#f2f2f3;--text-muted:#a8a8af;--accent:#69cbd0;--accent-soft:#69cbd019}
  body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;padding-top:var(--reader-header);padding-bottom:116px}
  #readerHeader{height:var(--reader-header);justify-content:flex-start;gap:12px;padding:0 16px}
  #readerHeader .brand{margin-right:auto;align-items:flex-start}
  #readerHeader .brand-ar{font:650 19px/1.2 system-ui,sans-serif;color:var(--text)}
  #readerHeader .brand-en{font-size:9px;letter-spacing:.08em}
  .reader-nav-toggle{border:0;min-width:32px;padding:5px 7px}
  #readerHeader .surah-picker{width:min(450px,56%);flex-shrink:1}
  #readerHeader .chrome-primary{justify-content:flex-end}
  #readerHeader .chrome-primary #surahSelect,#readerHeader .chrome-primary #juzSelect{flex:0 1 240px;text-align:left}
  #readerHeader .chrome-more{position:fixed;top:var(--reader-header);right:0;bottom:0;width:min(380px,100vw);max-height:none;margin:0;border-radius:0;padding:18px;z-index:70;box-shadow:-8px 0 24px #0002}
  .reader-settings-heading{font:650 19px system-ui,sans-serif;margin:0 0 8px;color:var(--text)}
  #readerSidebar{padding:16px 12px 120px;font-size:13px;overscroll-behavior:contain}
  #readerSidebar h2{font-size:14px;margin:0 4px 12px}
  .reader-nav-tabs{gap:4px}
  .reader-nav-tabs button{font-size:12px;padding:7px 4px}
  #readerSearch{padding:9px;font-size:13px}
  #readerNavList{gap:1px}
  #readerNavList button{padding:7px 6px;min-height:41px;gap:7px}
  .reader-nav-num{flex-basis:23px;font-size:11px}
  .reader-nav-ar{font-size:17px}
  #readerModeBar{position:sticky;top:var(--reader-header);z-index:29;direction:ltr;display:flex;justify-content:space-between;align-items:center;gap:8px;width:100%;max-width:1000px;padding:10px 4px;background:var(--bg);border-bottom:1px solid var(--border)}
  .reader-mode-switch{display:flex;background:var(--surface-2);border-radius:7px;padding:3px;gap:2px;flex-shrink:0}
  .reader-mode-switch button{border:0;border-radius:5px;background:transparent;color:var(--text-muted);padding:7px 13px;font:550 13px system-ui,sans-serif;cursor:pointer}
  .reader-mode-switch button[aria-pressed="true"]{background:var(--surface);color:var(--text);box-shadow:0 1px 4px #0001}
  .reader-mode-tools{display:flex;align-items:center;gap:6px}
  .reader-mode-tools button,.reader-mode-tools select{border:1px solid var(--border);border-radius:7px;background:var(--surface);color:var(--text);font:12px system-ui,sans-serif;padding:7px 9px;cursor:pointer}
  .reader-mode-tools button[aria-pressed="true"]{color:var(--accent);background:var(--accent-soft)}
  #readerHeading{max-width:1000px;padding:26px 0 12px;margin-bottom:0;border:0}
  #readerHeading h1{font-size:24px;font-weight:650;letter-spacing:-.4px}
  #readerHeading .reader-ar-title{font-size:30px;line-height:1.5}
  #readerHeading p{margin:4px 0 14px}
  #readerHeading .reader-actions{gap:6px}
  #readerHeading .reader-action{font-size:12px;padding:7px 10px}
  #readerMeanings{display:none}
  #readerNotice:empty{display:none}
  body.reader-translation .mushaf-pages{max-width:1000px;gap:0;display:flex}
  body.reader-translation .page-nav{display:none!important}
  body.reader-translation .mushaf-pages .bismillah{color:var(--text);font-size:32px;margin:8px 0 10px;border:0;padding:12px 0}
  .qv{width:100%;display:grid;grid-template-columns:66px minmax(0,1fr);gap:24px;border-top:1px solid var(--border);padding:32px 8px;direction:ltr;scroll-margin-top:120px}
  .qv-actions{display:flex;flex-direction:column;align-items:center;gap:9px;color:var(--text-muted)}
  .qv-ref{font:600 13px system-ui,sans-serif;color:var(--text);padding:4px 0 9px}
  .qv-action{border:0;background:transparent;color:var(--text-muted);width:34px;height:34px;border-radius:7px;display:grid;place-items:center;font:18px system-ui,sans-serif;cursor:pointer}
  .qv-action:hover,.qv-action[aria-pressed="true"]{color:var(--accent);background:var(--accent-soft)}
  .qv-content{min-width:0}
  .qv-arabic{font-family:'Scheherazade New','Traditional Arabic',serif;font-size:var(--reader-size);line-height:1.95;color:var(--text);direction:rtl;text-align:right;font-weight:400;margin:0 0 20px;overflow-wrap:anywhere}
  .qv-arabic .word{display:inline-block;color:inherit;max-width:100%;vertical-align:baseline}
  .qv-arabic .word.active-word{color:var(--accent);background:var(--accent-soft)}
  .qv-arabic .ayah-pin{color:var(--accent);background:transparent;box-shadow:none;border-color:var(--accent)}
  .qv-translation{font:17px/1.75 system-ui,sans-serif;color:var(--text);text-align:left;margin:0 0 8px;white-space:pre-wrap}
  .qv-credit{font:12px/1.5 system-ui,sans-serif;color:var(--text-muted);display:block}
  .qv-retry{border:0;background:none;color:var(--accent);font:13px system-ui,sans-serif;cursor:pointer;text-decoration:underline;padding:0}
  .qv-gloss{display:inline-flex;flex-direction:column;align-items:center;vertical-align:top;max-width:100%;margin:0 3px 10px}
  .qv-gloss button{font:12px/1.5 system-ui,sans-serif;color:var(--text-muted);background:none;border:0;max-width:160px;padding:4px 6px;white-space:normal;direction:ltr;cursor:pointer}
  .qv-gloss button:hover,.qv-gloss button[aria-pressed="true"]{color:var(--accent);background:var(--accent-soft);border-radius:5px}
  .qv-gloss button:disabled{cursor:default}
  body:not(.reader-translation) .mushaf-page{background:var(--surface);color:var(--text);--page-ink:var(--text);border:0;border-radius:0;box-shadow:none;padding:22px 10px}
  body:not(.reader-translation) .mushaf-page-header{color:var(--text-muted);border-color:var(--border)}
  body:not(.reader-translation) .mushaf-page .bismillah{border-color:var(--border)}
  .controls{direction:ltr;padding:7px 18px 9px;min-height:65px}
  .controls-row{max-width:1100px!important;gap:12px}
  .controls .scrubber{display:none}
  .controls .info-bar{min-width:0;flex:0 1 190px;direction:ltr}
  .controls .info-text{text-align:left;min-width:0}
  .controls .info-name,.controls .info-meta{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .controls #seek{flex:1;min-width:60px;accent-color:var(--accent)}
  .controls .play-btn{background:var(--accent);color:white;box-shadow:none}
  .reader-mode-tools .experience-toggle{display:flex;gap:3px;direction:ltr;margin:0}
  .reader-mode-tools .experience-toggle button{font-size:12px;white-space:nowrap}
  .reader-mode-tools .experience-toggle button.on{background:var(--accent-soft);color:var(--accent)}
  body.reader-translation .reader-reading-only{display:none}
  @media(min-width:900px){body.reader-nav-open{padding-left:calc(var(--reader-nav) + 26px);padding-right:26px}}
  @media(max-width:899px){
    #readerHeader .surah-picker{width:auto;flex:1;min-width:0}
    #readerHeader .brand-ar{font-size:17px}
    #readerModeBar{padding:7px 0}
    .reader-mode-switch button{padding:7px 9px;font-size:12px}
    .reader-mode-tools{gap:3px}
    .reader-mode-tools button,.reader-mode-tools select{padding:6px;font-size:11px}
    .reader-mode-tools .experience-toggle{display:none}
    .qv{grid-template-columns:1fr;gap:8px;padding:19px 3px}
    .qv-actions{flex-direction:row;justify-content:flex-start}
    .qv-ref{margin-right:auto;padding:0}
    .qv-arabic{margin-bottom:15px;font-size:var(--reader-size)}
    .qv-translation{font-size:16px}
    .controls{padding:6px 9px}
    .controls-row{gap:6px}
  }
  @media(max-width:420px){#readerHeader .brand{display:none}.controls .info-bar{display:none}.reader-mode-tools select{max-width:80px}}


  /* Mobile overlap: never squeeze a word's layout box below its ink width. */
  :root { --reader-top-inset: 116px; --reader-bottom-inset: 100px; }
  html { scroll-padding-top:calc(var(--reader-top-inset) + 12px); scroll-padding-bottom:calc(var(--reader-bottom-inset) + 16px); }
  body { padding-bottom:calc(var(--reader-bottom-inset) + 24px); }
  .mushaf-pages,.mushaf-page,.mushaf-text,.qv,.qv-content { min-width:0; max-width:100%; }
  .mushaf-text { line-height:max(var(--reader-leading),1.65); }
  .mushaf-text.with-letters,.mushaf-text.is-nastaleeq { line-height:max(var(--reader-leading),1.85); }
  .mushaf-text.is-nastaleeq { line-height:max(var(--reader-leading),2.1); }
  .mushaf-line { gap:.12em; padding-block:.24em; }
  .mushaf-line.is-short { gap:.35em; }
  .mushaf-line > .word,.mushaf-line > .mushaf-num-glyph,.mushaf-line > .ayah-pin,.mushaf-line > .sajda-badge {
    flex:0 0 auto; min-width:max-content; white-space:nowrap;
  }
  .mushaf-line > .bismillah { flex:1 1 100%; min-width:0; }
  .qv-arabic { line-height:max(var(--reader-leading),2.05); overflow-wrap:normal; word-break:normal; padding:.22em .12em .35em; }
  .qv-arabic .word { white-space:nowrap; max-width:none; overflow:visible; padding-inline:.025em; }
  .qv-gloss { min-width:0; max-width:none; margin-inline:.08em; }
  .qv-gloss button { max-width:min(145px,40vw); overflow-wrap:break-word; }
  .qv-arabic .ayah-pin { white-space:nowrap; vertical-align:baseline; }
  #readerModeBar [hidden] { display:none!important; }
  .reader-mode-tools { min-width:0; }
  @media(max-width:899px) {
    :root { --reader-top-inset:56px; }
    #readerHeader { max-width:100vw; }
    #readerModeBar { position:static; flex-wrap:wrap; justify-content:space-between; gap:8px; padding:8px 0; }
    .reader-mode-tools { flex-wrap:wrap; justify-content:flex-end; gap:4px; }
    .reader-mode-tools .experience-toggle { display:flex; width:auto; }
    .reader-mode-tools .experience-toggle button { padding:5px 7px; }
    .reader-mode-switch { flex:0 0 auto; }
    .reader-mode-tools button { white-space:nowrap; }
    body { padding-left:12px; padding-right:12px; }
    body:not(.reader-translation) .mushaf-page { padding:10px 4px 18px; }
    .qv { padding:18px 0; }
    .qv-arabic { font-size:min(var(--reader-size),max(20px,8.5vw)); line-height:max(var(--reader-leading),2.15); overflow-x:auto; overflow-y:visible; }
    .qv-gloss { margin-bottom:12px; }
    .controls { padding:8px 10px calc(8px + env(safe-area-inset-bottom,0px)); }
    .controls-row { min-width:0; }
    .controls #seek { min-width:0; width:100%; margin:0; }
    .word-inspector { bottom:calc(var(--reader-bottom-inset) + 10px); max-height:calc(100dvh - var(--reader-top-inset) - var(--reader-bottom-inset) - 24px); overflow:auto; }
  }
  @media(max-width:480px) {
    .reader-mode-tools { flex:1 1 100%; justify-content:flex-start; }
    .reader-mode-tools .experience-toggle { margin-left:auto; }
    .controls .controls-row { display:grid; grid-template-columns: minmax(0,1fr) 30px 36px 30px minmax(0,1fr); grid-template-areas:"speed prev play next spare" "start seek seek seek end"; gap:5px 8px; }
    .controls .info-bar { display:none; }
    #prevAyahBtn{grid-area:prev} #playBtn{grid-area:play;justify-self:center} #nextAyahBtn{grid-area:next}
    #speedSelect{grid-area:speed;justify-self:start;max-width:100%}
    #curTime{grid-area:start;min-width:0} #seek{grid-area:seek} #totTime{grid-area:end;min-width:0}
    #readerHeading .reader-actions { flex-wrap:wrap; }
    .reader-mode-tools select { max-width:100px; }
  }


  /* Translation: keep each Quranic word as a single native shaping run.
     Timing ranges are painted independently of the actual text nodes. */
  .qv-arabic {
    direction:rtl; text-align:right; text-align-last:right;
    word-break:normal; overflow-wrap:normal; word-spacing:normal;
    letter-spacing:normal; font-kerning:normal;
    font-variant-ligatures:normal;
    font-feature-settings:normal;
    font-family:'Scheherazade New','Noto Naskh Arabic','Traditional Arabic',serif;
  }
  .qv-arabic .word {
    display:inline; white-space:nowrap; padding:0; margin:0;
    font:inherit; letter-spacing:normal; word-spacing:normal;
    font-feature-settings:normal; font-variant-ligatures:normal;
    unicode-bidi:normal;
  }
  .qv-gloss .word { display:block; text-align:center; }
  ::highlight(qusx-timed-letter) { color:var(--accent); }
  @media(max-width:899px){
    .qv-arabic { padding-block:.35em .45em; line-height:max(var(--reader-leading),2.05); }
  }


  /* Reading and Translation share native Unicode word shaping.
     Preserve exact printed line membership, but avoid artificial gaps
     between Unicode words when the line has spare space. */
  .mushaf-text.native-words .mushaf-line {
    justify-content:flex-start; gap:.24em;
    font-kerning:normal; font-variant-ligatures:normal;
    font-feature-settings:normal; letter-spacing:normal;
    word-spacing:normal;
  }
  .mushaf-text.native-words .mushaf-line > .word {
    display:inline-block; flex:0 0 auto; min-width:max-content;
    font:inherit; direction:rtl; unicode-bidi:normal;
    letter-spacing:normal; word-spacing:normal;
    font-feature-settings:normal; font-variant-ligatures:normal;
    white-space:nowrap; padding:0; margin:0;
  }
  .mushaf-text .mushaf-line.is-short { justify-content:flex-start; gap:.24em; }
  .mushaf-text .unicode-fallback {
    font-family:'Scheherazade New','UthmanicHafs','Noto Naskh Arabic','Traditional Arabic',serif;
    font-feature-settings:normal; font-variant-ligatures:normal;
    letter-spacing:normal; word-spacing:normal;
  }
  @media(max-width:899px){
    .mushaf-text.native-words .mushaf-line { gap:.22em; }
  }

  .word.active-ayah { background:var(--accent-soft); }
</style>
</head>
<body>

<div id="readerHeader"><button type="button" class="reader-nav-toggle" id="readerNavToggle" aria-label="Toggle navigation" aria-controls="readerSidebar" aria-expanded="false">☰</button>
<div class="brand">
  <span class="brand-ar" lang="en">QUSX</span>
  <span class="brand-en">Quran Reader</span>
</div>
<div class="surah-picker">
  <div class="chrome-primary">
    <select id="browseModeSelect" title="Browse by surah or by juz" aria-label="Browse mode">
      <option value="surah">Surah</option>
      <option value="juz">Juz</option>
    </select>
    <select id="surahSelect" aria-label="Surah"></select>
    <select id="juzSelect" style="display:none" title="Juz" aria-label="Juz"></select>
    <button type="button" class="chrome-icon-btn chrome-more-btn" id="chromeMoreBtn" title="Reader settings" aria-label="Reader settings" aria-expanded="false" aria-controls="chromeMore">&#8943;</button>
    <button type="button" class="chrome-icon-btn theme-toggle" id="themeToggle" title="Toggle light/dark" aria-label="Toggle light/dark theme">&#9789;</button>
  </div>
  <div class="chrome-more" id="chromeMore" hidden><h2 class="reader-settings-heading">Reading settings</h2>
    <div class="chrome-more-row">
      <label for="reciterSelect">Reciter</label>
      <select id="reciterSelect"></select>
    </div>
    <div class="chrome-more-row">
      <label for="layoutSelect">Edition</label>
      <select id="layoutSelect" title="Print edition — authentic page and line composition"></select>
    </div>
    <div class="chrome-more-row">
      <label for="readingStyleSelect">Reading</label>
      <select id="readingStyleSelect">
        <option value="authentic">Authentic Mushaf</option>
        <option value="reflow">Reflow Reader</option>
      </select>
    </div>
    <div class="chrome-more-row">
      <label for="followModeSelect">Following</label>
      <select id="followModeSelect">
        <option value="word">Highlight words</option>
        <option value="letter">Highlight letters</option>
      </select>
    </div>
    <div class="chrome-more-row" id="fontRow">
      <label for="fontSelect">Font</label>
      <select id="fontSelect" title="Unicode text font for Letter/Word modes"></select>
    </div>
    <div class="chrome-more-row script-row">
      <label for="scriptSelect">Arabic text</label>
      <select id="scriptSelect" title="Fully vocalized Uthmani or Quran Foundation Uthmani Simple">
        <option value="uthmani">Uthmani · with a‘rāb</option>
        <option value="uthmani-simple">Uthmani Simple · no a‘rāb</option>
      </select>
    </div>
    <div class="typography-panel" id="typographyPanel">
      <div class="type-panel-head">
        <span>Typography</span>
        <button type="button" id="typeReset">Reset</button>
      </div>
      <label class="type-control" for="textSizeRange">
        <span>Size</span>
        <input id="textSizeRange" type="range" min="18" max="72" step="1" value="32" aria-label="Quran text size">
        <span class="number-unit"><input id="textSizeNumber" type="number" min="12" max="120" step="1" value="32" inputmode="numeric" aria-label="Exact Quran text size"><small>px</small></span>
      </label>
      <label class="type-control" for="lineHeightRange">
        <span>Spacing</span>
        <input id="lineHeightRange" type="range" min="1.1" max="2.1" step="0.02" value="1.42" aria-label="Quran line spacing">
        <strong id="lineHeightValue">1.42</strong>
      </label>
    </div>
    <div class="chrome-more-row">
      <label for="pageViewSelect">Pages</label>
      <select id="pageViewSelect" title="Browse one mushaf page at a time, or scroll the whole reading">
        <option value="page">Browse page by page</option>
        <option value="scroll">Scroll all pages</option>
      </select>
    </div>
    <div class="chrome-more-row">
      <label for="followScrollSelect">Follow</label>
      <select id="followScrollSelect" title="How the view tracks the recited word">
        <option value="keep-up">Keep word up (above player)</option>
        <option value="nearest">Only if off-screen</option>
        <option value="off">Don't auto-scroll</option>
      </select>
    </div>
    <div class="chrome-toggle-row">
      <label title="Show root/lemma tip on hover"><input type="checkbox" id="grammarHoverToggle"> Hover grammar</label>
      <label title="Open grammar panel on word click (click still seeks audio)"><input type="checkbox" id="grammarClickToggle"> Click grammar</label>
    </div>
    <button type="button" id="modeBrowse" class="settings-action">Browse timed letters</button>
  </div>
</div>
</div>
<div id="readerShade" hidden></div>
<aside id="readerSidebar" aria-label="Quran navigation" hidden>
  <h2>Navigate the Quran</h2>
  <div class="reader-nav-tabs"><button type="button" id="readerSurahs" aria-pressed="true">Surah</button><button type="button" id="readerJuz" aria-pressed="false">Juz</button><button type="button" id="readerSaved" aria-pressed="false">Saved</button></div>
  <input type="search" id="readerSearch" placeholder="Search surah" aria-label="Search navigation">
  <nav id="readerNavList" aria-label="Reader locations"></nav>
</aside>
<div id="readerModeBar"><div class="reader-mode-switch" role="group" aria-label="Reading view"><button type="button" id="readerTranslationMode" aria-pressed="true">Translation</button><button type="button" id="readerReadingMode" aria-pressed="false">Reading</button></div><div class="reader-mode-tools"><button type="button" id="readerGlossToggle" aria-pressed="false">Word meanings</button><select id="readerGlossLanguage" aria-label="Spoken meaning language" hidden><option value="en">English</option><option value="hi">Hindi</option></select><button type="button" id="readerQuickSettings" aria-label="Reader settings">⚙</button><div class="mode-toggle experience-toggle" aria-label="Reading experience">
    <button id="experienceRead" class="on" title="Uninterrupted Quran reading">Read</button>
    <button id="experienceFollow" title="Follow the recitation">Follow</button>
    <button id="experienceExplore" title="Tap and study individual words">Explore</button>
  </div></div></div>
<section id="readerHeading" aria-label="Current reading">
  <div class="reader-ar-title" id="readerArabicName" lang="ar" dir="rtl"></div>
  <h1 id="readerChapterName">The Quran</h1><p id="readerChapterMeta">Read, listen and explore</p>
  <div class="reader-actions">
    <label class="reader-jump">Ayah <input type="number" id="readerAyah" min="1" value="1" aria-label="Verse number"></label>
    <button type="button" class="reader-action" id="readerGo">Go</button>
    <button type="button" class="reader-action" id="readerBookmark" aria-pressed="false">☆ Save verse</button>
    <button type="button" class="reader-action" id="readerShare">Copy link</button>
    <a class="reader-action" id="readerMeanings" href="https://dfordev1.github.io/qusx-audio/" target="_blank" rel="noopener">Spoken meanings ↗</a>
  </div>
  <div id="readerNotice" role="status"></div>
</section>
<div class="load-status" id="loadStatus"></div>
<div class="tradition-info" id="traditionInfo"></div>
<details class="about-wrap">
  <summary>About sources</summary>
  <div class="subtitle">data from <a href="https://huggingface.co/datasets/hetchyy/quranic-universal-ayahs" target="_blank">Qur'anic Universal Audio</a> (36 reciters) &middot; text &amp; word morphology from <a href="https://github.com/dfordev1/usxv2" target="_blank">QUSX</a> &middot; Mushaf glyphs &amp; tajweed colors from <a href="https://qul.tarteel.ai" target="_blank">Tarteel QUL</a></div>
</details>

<div class="verses" id="verses"></div>
<div class="page-nav" id="pageNav">
  <button type="button" id="pagePrev" aria-label="Previous page">&#8249;</button>
  <span class="page-label" id="pageLabel">Page 1</span>
  <button type="button" id="pageNext" aria-label="Next page">&#8250;</button>
</div>
<div class="mushaf-pages" id="mushafPages"></div>
<div class="boot-hint" id="bootHint">Loading mushaf…</div>
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
    <button class="transport-btn" id="prevAyahBtn" title="Previous ayah" aria-label="Previous ayah">&#8249;</button>
    <button class="play-btn" id="playBtn" aria-label="Play">&#9658;</button>
    <button class="transport-btn" id="nextAyahBtn" title="Next ayah" aria-label="Next ayah">&#8250;</button>
    <select id="speedSelect" class="speed-select" title="Playback speed" aria-label="Playback speed">
      <option value="0.75">0.75×</option>
      <option value="1" selected>1×</option>
      <option value="1.25">1.25×</option>
    </select>
    <span class="time" id="curTime">0:00</span>
    <input type="range" id="seek" min="0" max="1000" value="0">
    <span class="time" id="totTime">0:00</span>
  </div>
  
  <div class="legacy-mode-controls" aria-hidden="true">
    <button id="modeLetter">Letters</button>
    <button id="modeWord">Words</button>
    <button id="modeMushaf">Mushaf</button>
    <button id="tapWordToggle">Tap words</button>
    <button id="tajweedToggle" class="tajweed-btn" disabled>Tajweed</button>
  </div>
</div>
<button type="button" id="controlsReveal" class="controls-reveal" aria-label="Show playback controls">&#9650;</button>

<div class="credit">Open timings &amp; audio · <a href="https://github.com/Wider-Community/quranic-universal-audio" target="_blank">QUA</a> · <a href="https://github.com/dfordev1/usxv2" target="_blank">QUSX</a> · Hafs &#39;an &#39;Asim</div>

<audio id="player" preload="auto"></audio>

<script>
const SURAH_INDEX = __SURAH_INDEX_JSON__; // 114 entries: {num, name, nameArabic, ayahCount}, from QUSX (github.com/dfordev1/usxv2)

// QPC glyph data: surah -> ayah -> string of PUA glyph chars (one per word
// position + trailing ayah-number glyph). V2 from Tarteel QUL; V1 from
// Quran.com API code_v1. Paired at render time with the matching per-page
// QCF font files from Quran Foundation's CDN.
const GLYPH_V2 = __GLYPH_V2_JSON__;
const GLYPH_V1 = __GLYPH_V1_JSON__;

// Per-page QCF fonts: key = "v1:50" / "v2:50" / "v4:50".
const loadedPageFonts = new Set();
const loadingPageFonts = new Map();
const QCF_FONT_URL = {
  v1: (p) => 'https://verses.quran.foundation/fonts/quran/hafs/v1/woff2/p' + p + '.woff2',
  v2: (p) => 'https://verses.quran.foundation/fonts/quran/hafs/v2/woff2/p' + p + '.woff2',
  v4: (p) => 'https://verses.quran.foundation/fonts/quran/hafs/v4/colrv1/woff2/p' + p + '.woff2',
};
const QCF_FAMILY_PREFIX = { v1: 'QCF1P', v2: 'QCFP', v4: 'QCFT' };
async function ensurePageFont(edition,page){
  if(!page||!QCF_FONT_URL[edition])return false;
  const key=edition+':'+page;
  if(loadedPageFonts.has(key))return true;
  if(loadingPageFonts.has(key))return loadingPageFonts.get(key);
  const job=(async()=>{
    try{
      const font=new FontFace(QCF_FAMILY_PREFIX[edition]+page,'url('+QCF_FONT_URL[edition](page)+')');
      await font.load();document.fonts.add(font);loadedPageFonts.add(key);
      requestAnimationFrame(markShortMushafLines);
      return true;
    }catch(_){return false;}
  })();
  loadingPageFonts.set(key,job);
  try{return await job;}finally{loadingPageFonts.delete(key);}
}

async function ensureTajweedFont(page) {
  return ensurePageFont('v4', page);
}

const RECITERS = __RECITERS_JSON__; // first entry may be local_alhadr; rest are QUA HF configs
let RECITER_CONFIG = RECITERS[0][0]; // may fall back after probing local_alhadr/
const LOCAL_RECITER_ID = 'local_alhadr';
let LOCAL_MANIFEST = null; // loaded on demand from ./local_alhadr/manifest.json
let LOCAL_ALHADR_AVAILABLE = null; // null = unknown, true/false after probe
let currentAudioKey = null; // actual audio file identity, not just a timestamp
let audioSeekToken=0, pendingAudioSeek=null, readerLoadToken=0, readerLoading=false;
function readerAudioUrl(url){
  try{return new URL(url,document.baseURI).href;}catch(_){return String(url||'');}
}
function readerAudioMatches(url){
  return !!url && readerAudioUrl(audio.currentSrc||audio.src)===readerAudioUrl(url);
}
function cancelPendingAudioSeek(){
  audioSeekToken++;
  if(pendingAudioSeek?.cleanup)pendingAudioSeek.cleanup();
  pendingAudioSeek=null;
}

function isLocalReciter() { return RECITER_CONFIG === LOCAL_RECITER_ID; }

function firstOnlineReciter() {
  const hit = RECITERS.find(r => r[0] !== LOCAL_RECITER_ID);
  return hit ? hit[0] : RECITERS[0][0];
}

async function ensureLocalManifest() {
  if (LOCAL_MANIFEST) return LOCAL_MANIFEST;
  const res = await fetch('local_alhadr/manifest.json');
  if (!res.ok) {
    LOCAL_ALHADR_AVAILABLE = false;
    throw new Error('local Al-Hadr pack not found (' + res.status + '). Use an online reciter, or serve this folder over HTTP with local_alhadr/ present.');
  }
  LOCAL_MANIFEST = normalizeLocalManifest(await res.json());
  LOCAL_ALHADR_AVAILABLE = true;
  return LOCAL_MANIFEST;
}

/** Soft probe — never throws. Used at boot so GitHub Pages can skip Al-Hadr. */
async function probeLocalAlhadr() {
  if (LOCAL_ALHADR_AVAILABLE === true && LOCAL_MANIFEST) return true;
  if (LOCAL_ALHADR_AVAILABLE === false) return false;
  try {
    const res = await fetch('local_alhadr/manifest.json', { method: 'GET' });
    if (!res.ok) {
      LOCAL_ALHADR_AVAILABLE = false;
      return false;
    }
    LOCAL_MANIFEST = normalizeLocalManifest(await res.json());
    LOCAL_ALHADR_AVAILABLE = true;
    return true;
  } catch (_) {
    LOCAL_ALHADR_AVAILABLE = false;
    return false;
  }
}

function applyLocalAlhadrAvailability() {
  const localOpt = reciterSelect && reciterSelect.querySelector('option[value="' + LOCAL_RECITER_ID + '"]');
  if (localOpt) {
    localOpt.disabled = !LOCAL_ALHADR_AVAILABLE;
    localOpt.hidden = false;
    localOpt.textContent = LOCAL_ALHADR_AVAILABLE
      ? 'Al-Hadr (alignments)'
      : 'Al-Hadr (pack missing — local only)';
  }
  if (!LOCAL_ALHADR_AVAILABLE && isLocalReciter()) {
    RECITER_CONFIG = firstOnlineReciter();
    if (reciterSelect) reciterSelect.value = RECITER_CONFIG;
    refreshReciterInfo();
    browseMode = 'surah';
    if (browseModeSelect) browseModeSelect.value = 'surah';
    if (surahSelect) surahSelect.style.display = '';
    if (juzSelect) juzSelect.style.display = 'none';
  }
  if (browseModeSelect) {
    const juzOpt = browseModeSelect.querySelector('option[value="juz"]');
    if (juzOpt) juzOpt.disabled = !isLocalReciter();
  }
}

// Optional manifest.audioBase (Internet Archive) rewrites relative juz paths
// to absolute URLs so GitHub Pages can run Al-Hadr without shipping audio.
// Set preferLocalAudio: true in the manifest to keep relative paths for offline.
// Juz 1–3 MP3 files were independently downloaded and probed in audit run
// 45358930585. Their durations match the manifest within 0.0005 seconds.
// Prefer those browser-compatible recordings; leave unaudited tracks unchanged.
function readerAuditedAudioUrl(url,base){
  const auditedBase='https://archive.org/download/quran-al-hadr-recitation/juz';
  if(base!==auditedBase||typeof url!=='string'||!url.startsWith(auditedBase+'/'))return url;
  return url.replace(/\/juz-(0[123])\.(ogg|opus)$/i,'/juz-$1.mp3');
}
function normalizeLocalManifest(m) {
  const base = (m.audioBase || '').replace(/\/$/, '');
  m._remoteAudioBase = base || '';
  const preferLocal = m.preferLocalAudio === true;
  if (!base || preferLocal) return m;
  const fix = (p) => {
    if (!p) return p;
    const url=/^https?:\/\//i.test(p)?p:base+'/'+p.split('/').pop();
    return readerAuditedAudioUrl(url,base);
  };
  for (const t of (m.tracks || [])) t.audio = fix(t.audio);
  for (const sn of Object.keys(m.surahs || {})) {
    for (const a of (m.surahs[sn].ayahs || [])) a.audio = fix(a.audio);
  }
  return m;
}

// Archive.org ships ogg for juz 1–21 and 23, but juz 22 and 25–30 are opus-only.
const AUDIO_EXT_FALLBACKS = ['.mp3', '.ogg', '.opus'];

function audioBasename(path) {
  if (!path) return null;
  const name = path.split('/').pop();
  return name || null;
}

function audioUrlWithExt(path, ext) {
  const name = audioBasename(path);
  if (!name) return null;
  const stem = name.replace(/\.(ogg|opus|mp3)$/i, '');
  const newName = stem + ext;
  if (/^https?:\/\//i.test(path)) {
    const parts = path.split('/');
    parts[parts.length - 1] = newName;
    return parts.join('/');
  }
  const base = LOCAL_MANIFEST && LOCAL_MANIFEST._remoteAudioBase;
  if (base) return base + '/' + newName;
  const parts = path.split('/');
  parts[parts.length - 1] = newName;
  return parts.join('/');
}

function nextAudioFallback(failedUrl, triedSet) {
  const name = audioBasename(failedUrl);
  if (!name) return null;
  const currentExt = (name.match(/\.(ogg|opus|mp3)$/i) || [])[0] || '.ogg';
  if (!/^https?:\/\//i.test(failedUrl)) {
    const base = LOCAL_MANIFEST && LOCAL_MANIFEST._remoteAudioBase;
    if (base) {
      const remote = base + '/' + name;
      if (!triedSet.has(remote)) return remote;
    }
  }
  for (const ext of AUDIO_EXT_FALLBACKS) {
    if (ext === currentExt.toLowerCase()) continue;
    const alt = audioUrlWithExt(failedUrl, ext);
    if (alt && !triedSet.has(alt)) return alt;
  }
  return null;
}

function readerLocalDurationIssue(expected,actual,requiredEnd=0){
  if(!Number.isFinite(expected)||expected<=0)return 'Missing expected recording duration';
  if(!Number.isFinite(actual)||actual<=0)return 'Recording duration unavailable';
  if(Number.isFinite(requiredEnd)&&requiredEnd>actual+.075)return 'Recording ends before the requested ayah (required '+requiredEnd.toFixed(2)+'s, received '+actual.toFixed(2)+'s)';
  if(Math.abs(expected-actual)>Math.max(2,expected*.005))return 'Al-Hadr duration mismatch (expected '+expected.toFixed(2)+'s, received '+actual.toFixed(2)+'s)';
  return null;
}
function readerRetryLocalAudio(v,idx,ms,autoplay,reason){
  if(!isLocalReciter()||!LOCAL_MANIFEST||VERSES[idx]!==v||!v.audio)return false;
  const from=v.audio;
  const tried=new Set((audio.dataset.audioTriedUrls||'').split('|').filter(Boolean));
  tried.add(from);
  const next=nextAudioFallback(from,tried);
  if(!next){audio.dataset.audioTriedUrls=[...tried].join('|');return false;}
  cancelPendingAudioSeek();
  audio.dataset.audioTriedUrls=[...tried,next].join('|');
  VERSES.forEach(x=>{if(x.audio===from)x.audio=next;});
  currentAudioKey=next;
  loadStatusEl.classList.remove('error');
  loadStatusEl.textContent=reason+' — trying '+audioBasename(next)+'…';
  seekToWordMs(ms,idx,autoplay);
  return true;
}
function audioIsReadyFor(url) {
  if (!url || !audio.src) return false;
  if (currentAudioKey !== url) return false;
  // HAVE_METADATA or better — safe to seek/play.
  return audio.readyState >= 1 && readerAudioMatches(url);
}

function refreshSurahAvailability() {
  const localNums = isLocalReciter() && LOCAL_MANIFEST
    ? new Set(LOCAL_MANIFEST.surahNumbers)
    : null;
  for (const opt of surahSelect.options) {
    const n = +opt.value;
    if (!localNums) {
      opt.disabled = false;
      opt.textContent = opt.textContent.replace(/ — no local timing$/, '');
      continue;
    }
    const base = SURAH_INDEX.find(s => s.num === n);
    const label = n + '. ' + base.name + ' (' + base.nameArabic + ')';
    if (localNums.has(n)) {
      opt.disabled = false;
      opt.textContent = label;
    } else {
      opt.disabled = true;
      opt.textContent = label + ' — no local timing';
    }
  }
}

function seekVerseStart(idx, autoplay) {
  const v = VERSES[idx];
  if (!v) return;
  seekToWordMs(v.source_offset_ms, idx, autoplay);
}

// Seek to an absolute ms position in the current (or target) verse's audio file.
function handleWordTap(v, wIdx, verseIdx, absStart) {
  if(readerLoading)return;
  cancelTapWordStop();
  if (!tapWordMode) {
    seekToWordMs(absStart, verseIdx, true);
    return;
  }

  // Standalone playback must use the measured word end. getWordWindows()
  // deliberately fills pauses up to the next word for continuous highlighting,
  // so using it here leaks audible audio from the following word.
  const rows = [...(v.words || [])].sort((a, b) => a[1] - b[1] || a[0] - b[0]);
  const rowIndex = rows.findIndex(row => row[0] === wIdx);
  const row = rowIndex >= 0 ? rows[rowIndex] : null;
  if(!row||v.alignmentVerified===false||!readerContainsTime(v,absStart)){seekVerseStart(verseIdx,true);return;}
  const startRel = row ? row[1] : Math.max(0, absStart - v.source_offset_ms);
  const nextStart = rowIndex >= 0 && rows[rowIndex + 1] ? rows[rowIndex + 1][1] : null;
  let endRel = row && row[2] > startRel ? row[2] : (nextStart != null ? nextStart : startRel + 450);
  if (nextStart != null) endRel = Math.min(endRel, nextStart);
  const absEnd = v.source_offset_ms + Math.max(startRel + 45, endRel);
  // Stop a few milliseconds inside the boundary to absorb output-buffer latency.
  const stopAt = Math.max(absStart + 35, absEnd - 20);
  const token = tapPlaybackToken;

  seekToWordMs(absStart, verseIdx, true);
  const watchFrame = () => {
    if (token !== tapPlaybackToken) return;
    if(pendingAudioSeek){tapFrameId=requestAnimationFrame(watchFrame);return;}
    if(readerLoading||VERSES[verseIdx]!==v||currentVerseIdx!==verseIdx||!readerAudioMatches(v.audio)||loadStatusEl.classList.contains('error')){cancelTapWordStop();return;}
    const now = audio.currentTime * 1000;
    if (now >= stopAt) {
      audio.pause();
      tapFrameId = 0;
      return;
    }
    tapFrameId = requestAnimationFrame(watchFrame);
  };
  tapFrameId = requestAnimationFrame(watchFrame);
}

function seekToWordMs(absMs,verseIdx,autoplay){
  const v=VERSES[verseIdx];if(!v)return;
  cancelPendingAudioSeek();
  if(!v.audio||!readerValidSpan(v.source_offset_ms,v.duration_ms)){audio.pause();currentAudioKey=null;currentVerseIdx=verseIdx;clearHighlights();refreshScrubber(verseIdx);refreshInfoBar(verseIdx);scrollToPlayback(verseIdx,true);loadStatusEl.textContent='No aligned audio for '+v.surah+':'+v.ayah+' in this reciter.';loadStatusEl.classList.add('error');return;}
  if(!readerContainsTime(v,absMs))absMs=Number(v.source_offset_ms);
  const token=audioSeekToken,request={token,verse:v,idx:verseIdx,ms:absMs,autoplay:!!autoplay};
  pendingAudioSeek=request;
  currentVerseIdx=verseIdx;lastScrollKey='';clearHighlights();
  refreshScrubber(verseIdx);refreshInfoBar(verseIdx);syncPageToVerse(verseIdx);
  const ready=audioIsReadyFor(v.audio);
  audio.pause();
  const current=()=>pendingAudioSeek===request&&audioSeekToken===token&&VERSES[verseIdx]===v;
  const cleanup=()=>{
    clearTimeout(timer);audio.removeEventListener('loadedmetadata',apply);
    audio.removeEventListener('durationchange',apply);audio.removeEventListener('canplay',apply);
    audio.removeEventListener('seeked',verify);audio.removeEventListener('canplay',verify);audio.removeEventListener('durationchange',verify);
  };
  request.cleanup=cleanup;
  const fail=message=>{
    if(!current())return;
    cleanup();pendingAudioSeek=null;cancelTapWordStop();audio.pause();clearHighlights();
    loadStatusEl.textContent=message;loadStatusEl.classList.add('error');
  };
  const verify=()=>{
    if(!current()||!request.seekIssued||audio.seeking||!readerAudioMatches(v.audio))return;
    if(!v.clipRelative&&isLocalReciter()){
      const track=LOCAL_MANIFEST?.tracks?.find(t=>Number(t.juz)===Number(v.localJuz));
      const issue=readerLocalDurationIssue(Number(track?.durationSeconds),audio.duration,(Number(v.source_offset_ms)+Number(v.duration_ms))/1000);
      if(issue){if(audio.readyState<3)return;if(readerRetryLocalAudio(v,verseIdx,absMs,request.autoplay,issue))return;fail(issue+'. No matching format available. Recitation stopped.');return;}
    }
    if(Math.abs(audio.currentTime-absMs/1000)>.075||!readerContainsTime(v,audio.currentTime*1000))return;
    cleanup();pendingAudioSeek=null;currentVerseIdx=verseIdx;
    loadStatusEl.classList.remove('error');
    refreshScrubber(verseIdx);refreshInfoBar(verseIdx);syncPageToVerse(verseIdx);
    scrollToPlayback(verseIdx,true);updateHighlight();
    if(request.autoplay)audio.play().catch(()=>{if(audioSeekToken!==token)return;cancelTapWordStop();loadStatusEl.textContent='Tap Play to continue recitation.';});
    saveResumeState();
  };
  const apply=()=>{
    if(!current()||request.seekIssued||!readerAudioMatches(v.audio)||audio.readyState<1)return;
    const duration=audio.duration;
    if(!v.clipRelative&&isLocalReciter()){
      const track=LOCAL_MANIFEST?.tracks?.find(t=>Number(t.juz)===Number(v.localJuz));
      const expected=Number(track?.durationSeconds);
      const issue=readerLocalDurationIssue(expected,duration,(Number(v.source_offset_ms)+Number(v.duration_ms))/1000);
      if(issue){
        // Streaming metadata can be provisional until the browser has buffered media.
        if(audio.readyState<3)return;
        if(readerRetryLocalAudio(v,verseIdx,absMs,request.autoplay,issue))return;
        fail(issue+'. No matching format available. Recitation stopped.');return;
      }
    }
    if(Number.isFinite(duration)){
      if(absMs/1000>duration+.15){fail('Audio does not contain the requested ayah. Recitation stopped.');return;}
      if(v.clipRelative&&Math.abs(duration-v.duration_ms/1000)>Math.max(.75,v.duration_ms/1000*.03)){fail('Audio clip duration differs from its timing data. Recitation stopped.');return;}
    }
    request.seekIssued=true;
    try{audio.currentTime=absMs/1000;}catch(e){fail('Could not seek recitation: '+e.message);return;}
    verify();
  };
  const timer=setTimeout(()=>{
    if(!current())return;
    const track=LOCAL_MANIFEST?.tracks?.find(t=>Number(t.juz)===Number(v.localJuz));
    const issue=!v.clipRelative&&isLocalReciter()?readerLocalDurationIssue(Number(track?.durationSeconds),audio.duration,(Number(v.source_offset_ms)+Number(v.duration_ms))/1000):null;
    if(!v.clipRelative&&isLocalReciter()&&readerRetryLocalAudio(v,verseIdx,absMs,request.autoplay,issue||'Could not confirm audio position'))return;
    fail(issue?issue+'. No matching format available. Recitation stopped.':'Could not confirm the audio position. Tap Play to retry.');
  },15000);
  audio.addEventListener('loadedmetadata',apply);
  audio.addEventListener('durationchange',apply);
  audio.addEventListener('canplay',apply);
  audio.addEventListener('seeked',verify);
  audio.addEventListener('canplay',verify);audio.addEventListener('durationchange',verify);
  if(!ready){
    if(currentAudioKey!==v.audio)audio.dataset.audioTriedUrls='';
    currentAudioKey=v.audio;
    audio.src=v.audio;audio.load();
  }else apply();
}

// Extend each word's end to the next word's start so gaps between ASR words
// still keep the previous word highlighted (e.g. pause after ٱللَّهِ).
// Also repair zero-duration ASR stamps (start===end) which otherwise never
// satisfy `ms < end` and appear as missing mid-ayah highlights.
function getWordWindows(v) {
  if (v._wordWindows) return v._wordWindows;
  const rows = [...(v.words || [])].sort((a, b) => a[1] - b[1] || a[0] - b[0]);
  v._wordWindows = rows.map(([wIdx, s, e], i) => {
    let end;
    if (i + 1 < rows.length) {
      end = rows[i + 1][1];
    } else {
      end = Math.max(e + 80, (v.duration_ms || e + 80));
    }
    // Zero-length or inverted window (common when ASR collapses a word).
    if (!(end > s)) end = s + 80;
    // Prefer the measured end when it sits inside the gap-to-next window.
    if (e > s && e < end) {
      // keep gap-fill to next word — stronger continuous highlight
    }
    return [wIdx, s, end];
  });
  return v._wordWindows;
}

function activeWordAtMs(v, ms) {
  if(v.alignmentVerified===false||!readerContainsTime(v,ms))return null;
  const rel = ms - Number(v.source_offset_ms);
  const wins = getWordWindows(v);
  for (const [wIdx, s, end] of wins) {
    if (rel >= s && rel < end) return wIdx;
  }
  // Soft fallback: nearest prior word if we're inside the ayah span but
  // between repaired windows (floating-point / trim edge).
  if (rel >= 0 && rel <= (v.duration_ms || 0) + 50) {
    let best = null;
    for (const [wIdx, s, end] of wins) {
      if (s <= rel) best = wIdx;
    }
    return best;
  }
  return null;
}

function ensureAudioForVerse(idx, autoplay) {
  const v=VERSES[idx];if(!v)return;
  if(!v.audio){seekVerseStart(idx,autoplay);return;}
  if(pendingAudioSeek?.verse===v){pendingAudioSeek.autoplay=!!autoplay;return;}
  if(audioIsReadyFor(v.audio)&&currentVerseIdx===idx&&!audio.seeking&&readerContainsTime(v,audio.currentTime*1000)&&!loadStatusEl.classList.contains('error')){
    if(autoplay&&audio.paused)audio.play().catch(()=>{loadStatusEl.textContent='Tap Play to continue recitation.';});
    return;
  }
  seekVerseStart(idx,autoplay);
}

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

// QUSX ships the SAME word text/morphology across all print layouts —
// only page/line placement differs. Script faces:
//   madani-v1/v2/v4 → per-page QCF PUA glyph fonts (+ glyph maps)
//   qatar           → UthmanicHafs Unicode
//   indopak-*       → IndoPak Nastaleeq Unicode
//   nastaleeq       → KFGQPC Nastaleeq Unicode
const LAYOUTS = [
  ['madani-v2', 'Madani V2 (KFGQPC glyphs)'],
  ['madani-v1', 'Madani V1 (KFGQPC glyphs)'],
  ['madani-v4-tajweed', 'Madani V4 Tajweed (glyphs)'],
  ['qatar', 'Mushaf Qatar (Uthmani)'],
  ['indopak-15', 'IndoPak 15-line (Nastaleeq)'],
  ['indopak-9-gaba', 'IndoPak 9-line (Gaba)'],
  ['indopak-13-qudratullah', 'IndoPak 13-line (Qudratullah)'],
  ['indopak-13-taj', 'IndoPak 13-line (Taj Co.)'],
  ['indopak-16-taj', 'IndoPak 16-line (Taj Co.)'],
  ['nastaleeq', 'KFGQPC Nastaleeq 15-line'],
];
let currentLayout = 'madani-v2';

function layoutProfile() {
  switch (currentLayout) {
    case 'madani-v1':
      return { kind: 'glyph', glyph: 'v1', pageFont: 'v1', tajweedCapable: false, unicodeFamily: null };
    case 'madani-v4-tajweed':
      return { kind: 'glyph', glyph: 'v2', pageFont: 'v4', tajweedCapable: true, tajweedForced: true, unicodeFamily: null };
    case 'madani-v2':
      return { kind: 'glyph', glyph: 'v2', pageFont: 'v2', tajweedCapable: true, unicodeFamily: null };
    case 'qatar':
      return { kind: 'unicode', glyph: null, pageFont: null, tajweedCapable: false, unicodeFamily: 'UthmanicHafs' };
    case 'nastaleeq':
      return { kind: 'unicode', glyph: null, pageFont: null, tajweedCapable: false, unicodeFamily: 'KFGQPCNastaleeq' };
    default:
      // All IndoPak line-count variants share the IndoPak Nastaleeq face;
      // QUSX still supplies each edition's own page/line pins.
      return { kind: 'unicode', glyph: null, pageFont: null, tajweedCapable: false, unicodeFamily: 'IndoPakNastaleeq' };
  }
}
function activeGlyphMap() {
  const g = layoutProfile().glyph;
  if (g === 'v1') return GLYPH_V1;
  if (g === 'v2') return GLYPH_V2;
  return null;
}
function mushafSupportsTajweed() {
  return layoutProfile().tajweedCapable === true;
}

// Unicode faces for Letter/Word modes. Mushaf Madani layouts still use QCF
// per-page glyph fonts; this picker only affects letter/word highlighting.
const TEXT_FONTS = [
  ['auto', 'Automatic · match the reading mode'],
  ['uthmanic', 'Uthmanic Hafs · Madani'],
  ['scheherazade', 'Scheherazade New · classical'],
  ['amiri-quran', 'Amiri Quran · literary'],
  ['noto-naskh', 'Noto Naskh Arabic · clean'],
  ['lateef', 'Lateef · open and elegant'],
  ['harmattan', 'Harmattan · compact Naskh'],
  ['mirza', 'Mirza · calligraphic'],
  ['indopak', 'IndoPak Nastaleeq'],
  ['kfgqpc-nastaleeq', 'KFGQPC Nastaleeq'],
  ['noto-nastaliq', 'Noto Nastaliq Urdu'],
];
const TEXT_FONT_CSS = {
  scheherazade: "'Scheherazade New', 'UthmanicHafs', 'Traditional Arabic', serif",
  uthmanic: "'UthmanicHafs', 'Scheherazade New', 'Traditional Arabic', serif",
  'amiri-quran': "'Amiri Quran', 'UthmanicHafs', 'Scheherazade New', serif",
  'noto-naskh': "'Noto Naskh Arabic', 'Scheherazade New', serif",
  lateef: "'Lateef', 'Scheherazade New', serif",
  harmattan: "'Harmattan', 'Scheherazade New', serif",
  mirza: "'Mirza', 'Scheherazade New', serif",
  'noto-nastaliq': "'Noto Nastaliq Urdu', 'KFGQPCNastaleeq', serif",
  indopak: "'IndoPakNastaleeq', 'KFGQPCNastaleeq', 'Traditional Arabic', serif",
  'kfgqpc-nastaleeq': "'KFGQPCNastaleeq', 'IndoPakNastaleeq', 'Traditional Arabic', serif",
};
let currentTextFont = localStorage.getItem('quran-text-font') || 'auto';
if (!TEXT_FONTS.some(([k]) => k === currentTextFont)) currentTextFont = 'auto';

function resolveTextFontKey() {
  if (currentTextFont !== 'auto') return currentTextFont;
  // Letter mode needs safe combining marks; Word can take the mushaf-like face.
  if (mode === 'letter') return 'scheherazade';
  const family = layoutProfile().unicodeFamily;
  if (family === 'UthmanicHafs') return 'uthmanic';
  if (family === 'IndoPakNastaleeq') return 'indopak';
  if (family === 'KFGQPCNastaleeq') return 'kfgqpc-nastaleeq';
  // Madani glyph layouts have no Unicode family — use QPC Uthmani for Word.
  if (layoutProfile().kind === 'glyph') return 'uthmanic';
  return 'scheherazade';
}
function textFontCss() {
  return TEXT_FONT_CSS[resolveTextFontKey()] || TEXT_FONT_CSS.scheherazade;
}
function textFontIsNastaleeq() {
  const k = resolveTextFontKey();
  return k === 'indopak' || k === 'kfgqpc-nastaleeq' || k === 'noto-nastaliq';
}

let mode = 'letter'; // internal renderer: 'letter' | 'word' | 'mushaf'
let readerPresentation=localStorage.getItem('qusx-presentation-v2')==='reading'?'reading':'translation';
let readerGlossEnabled=false, readerGlossLanguage='en';
const readerLetterRanges=new WeakMap();
let experience = localStorage.getItem('quran-experience') || 'read';
if (!['read', 'follow', 'explore'].includes(experience)) experience = 'read';
let readingStyle = localStorage.getItem('quran-reading-style') || 'authentic';
if (!['authentic', 'reflow'].includes(readingStyle)) readingStyle = 'authentic';
let followPreference = localStorage.getItem('quran-follow-mode') || 'word';
if (!['word', 'letter'].includes(followPreference)) followPreference = 'word';
document.body.classList.add('follow-mode-' + mode);
let textScript = localStorage.getItem('quran-text-script') || 'uthmani';
if (!['uthmani', 'uthmani-simple'].includes(textScript)) textScript = 'uthmani';
let tapWordMode = localStorage.getItem('quran-tap-word-audio') === '1';
let tapFrameId = 0;
let tapPlaybackToken = 0;
function cancelTapWordStop() {
  tapPlaybackToken++;
  if (tapFrameId) cancelAnimationFrame(tapFrameId);
  tapFrameId = 0;
}
let tajweedOn = false; // Mushaf-mode-only: colored tajweed rules via QCF V4
let currentVerseIdx = 0;
let userSeeking = false;

const versesEl = document.getElementById('verses');
const mushafPagesEl = document.getElementById('mushafPages');
const audio = document.getElementById('player');
const playBtn = document.getElementById('playBtn');
const prevAyahBtn = document.getElementById('prevAyahBtn');
const nextAyahBtn = document.getElementById('nextAyahBtn');
const controlsEl = document.querySelector('.controls');
const controlsRevealBtn = document.getElementById('controlsReveal');
const seek = document.getElementById('seek');
const curTimeEl = document.getElementById('curTime');
const totTimeEl = document.getElementById('totTime');
const surahSelect = document.getElementById('surahSelect');
const juzSelect = document.getElementById('juzSelect');
const browseModeSelect = document.getElementById('browseModeSelect');
const reciterSelect = document.getElementById('reciterSelect');
const scriptSelect = document.getElementById('scriptSelect');
if (scriptSelect) scriptSelect.value = textScript;
const readingStyleSelect = document.getElementById('readingStyleSelect');
const followModeSelect = document.getElementById('followModeSelect');
const typographyPanel = document.getElementById('typographyPanel');
const fontRow = document.getElementById('fontRow');
if (readingStyleSelect) readingStyleSelect.value = readingStyle;
if (followModeSelect) followModeSelect.value = followPreference;
const textSizeRange = document.getElementById('textSizeRange');
const textSizeNumber = document.getElementById('textSizeNumber');
const lineHeightRange = document.getElementById('lineHeightRange');
const lineHeightValue = document.getElementById('lineHeightValue');
const typeReset = document.getElementById('typeReset');
const TYPOGRAPHY_VERSION = '3';
if (localStorage.getItem('quran-typography-version') !== TYPOGRAPHY_VERSION) {
  localStorage.setItem('quran-text-size-px', '32');
  localStorage.setItem('quran-line-height', '1.42');
  localStorage.setItem('quran-typography-version', TYPOGRAPHY_VERSION);
}
let textSize = Number(localStorage.getItem('quran-text-size-px')) || 32;
let lineHeight = Number(localStorage.getItem('quran-line-height')) || 1.42;
function clampTypography() {
  textSize = Math.max(12, Math.min(120, Math.round(textSize)));
  lineHeight = Math.max(1.1, Math.min(2.1, Math.round(lineHeight * 100) / 100));
}
function applyTypography() {
  clampTypography();
  document.documentElement.style.setProperty('--reader-size', textSize + 'px');
  document.documentElement.style.setProperty('--reader-leading', String(lineHeight));
  if (textSizeRange) textSizeRange.value = String(Math.max(18, Math.min(72, textSize)));
  if (textSizeNumber) textSizeNumber.value = String(textSize);
  if (lineHeightRange) lineHeightRange.value = String(lineHeight);
  if (lineHeightValue) lineHeightValue.textContent = lineHeight.toFixed(2);
  requestAnimationFrame(markShortMushafLines);
}
function saveTypography() {
  localStorage.setItem('quran-text-size-px', String(textSize));
  localStorage.setItem('quran-line-height', String(lineHeight));
}
applyTypography();
textSizeRange.addEventListener('input', () => { textSize = Number(textSizeRange.value); saveTypography(); applyTypography(); });
textSizeNumber.addEventListener('input', () => { textSize = Number(textSizeNumber.value) || 32; saveTypography(); applyTypography(); });
lineHeightRange.addEventListener('input', () => { lineHeight = Number(lineHeightRange.value); saveTypography(); applyTypography(); });
typeReset.addEventListener('click', () => { textSize = 32; lineHeight = 1.42; saveTypography(); applyTypography(); });
const loadStatusEl = document.getElementById('loadStatus');
const infoAvatar = document.getElementById('infoAvatar');
const infoName = document.getElementById('infoName');

// Local juz 404 → Archive.org; ogg 404 → opus/mp3 (juz 22+ on IA are opus-only).
audio.addEventListener('error', () => {
  cancelTapWordStop();
  if(readerLoading&&!pendingAudioSeek)return;
  if(!isLocalReciter()||!LOCAL_MANIFEST){cancelPendingAudioSeek();clearHighlights();loadStatusEl.textContent='Recitation audio unavailable. Select another reciter or retry Play.';loadStatusEl.classList.add('error');return;}
  const v = VERSES[currentVerseIdx] || VERSES[0];
  if (!v) return;
  const from = currentAudioKey || v.audio;
  if (!from) return;
  const triedSet = new Set((audio.dataset.audioTriedUrls || '').split('|').filter(Boolean));
  triedSet.add(from);
  const next = nextAudioFallback(from, triedSet);
  if (!next) {
    if (loadStatusEl) {
      cancelPendingAudioSeek();clearHighlights();
      loadStatusEl.textContent = 'Audio failed to load for this juz';
      loadStatusEl.classList.add('error');
    }
    return;
  }
  audio.dataset.audioTriedUrls = [...triedSet, next].join('|');
  VERSES.forEach(x => { if (x.audio === from) x.audio = next; });
  currentAudioKey = next;
  if (loadStatusEl) {
    const msg = /^https?:\/\//i.test(from)
      ? 'Trying alternate audio format…'
      : 'Local audio missing — trying Archive.org…';
    loadStatusEl.textContent = msg;
    loadStatusEl.classList.remove('error');
  }
  const idx = currentVerseIdx || 0;
  const resumePlay=pendingAudioSeek?pendingAudioSeek.autoplay:!audio.paused;
  const resumeMs=pendingAudioSeek?.ms??(audio.currentTime*1000);
  cancelPendingAudioSeek();
  const target=VERSES[idx];
  const start=Number(target.source_offset_ms),end=start+Number(target.duration_ms);
  seekToWordMs(resumeMs>=start&&resumeMs<end?resumeMs:start,idx,resumePlay);
});

let browseMode = 'surah'; // 'surah' | 'juz'
let currentJuz = null;
let pageViewMode = localStorage.getItem('quran-page-view') || 'page'; // 'page' | 'scroll'
let followScrollMode = localStorage.getItem('quran-follow-scroll') || 'keep-up'; // 'keep-up' | 'nearest' | 'off'
let grammarHoverOn = localStorage.getItem('quran-grammar-hover') === '1';
let grammarClickOn = localStorage.getItem('quran-grammar-click') === '1';
let currentPageIdx = 0;
let mushafPageCount = 0;

const pageViewSelect = document.getElementById('pageViewSelect');
const followScrollSelect = document.getElementById('followScrollSelect');
const grammarHoverToggle = document.getElementById('grammarHoverToggle');
const grammarClickToggle = document.getElementById('grammarClickToggle');
const pageNavEl = document.getElementById('pageNav');
const pagePrevBtn = document.getElementById('pagePrev');
const pageNextBtn = document.getElementById('pageNext');
const pageLabelEl = document.getElementById('pageLabel');
if (pageViewSelect) pageViewSelect.value = pageViewMode;
if (followScrollSelect) followScrollSelect.value = followScrollMode;
if (grammarHoverToggle) grammarHoverToggle.checked = grammarHoverOn;
if (grammarClickToggle) grammarClickToggle.checked = grammarClickOn;

function applyGrammarSettings(hidePanels) {
  document.body.classList.toggle('grammar-hover-on', grammarHoverOn);
  document.body.classList.toggle('grammar-click-on', grammarClickOn);
  if (hidePanels) {
    if (!grammarHoverOn) hideMorphTip();
    if (!grammarClickOn) hideInspector();
  }
}
applyGrammarSettings(false);

function bindGrammarHandlers(wordSpan, morph, v, wIdx) {
  if (!morph) return;
  wordSpan.classList.add('has-morph');
  wordSpan.tabIndex = 0;
  wordSpan.addEventListener('mouseenter', () => {
    if (grammarHoverOn) showMorphTip(wordSpan, morph);
  });
  wordSpan.addEventListener('mouseleave', hideMorphTip);
  wordSpan.addEventListener('focus', () => {
    if (grammarHoverOn) showMorphTip(wordSpan, morph);
  });
  wordSpan.addEventListener('blur', hideMorphTip);
  wordSpan.addEventListener('click', () => {
    if (grammarClickOn || experience === 'explore') showInspector(wordSpan, morph, v, wIdx);
  });
}

function verseDomScope(v) {
  return '[data-surah="' + v.surah + '"][data-ayah="' + v.ayah + '"]';
}

function applyPageViewMode() {
  if(readerPresentation==='translation'){mushafPagesEl.classList.remove('page-mode');pageNavEl?.classList.remove('visible');return;}
  if (!mushafPagesEl) return;
  mushafPagesEl.classList.toggle('page-mode', pageViewMode === 'page');
  if (pageNavEl) pageNavEl.classList.toggle('visible', pageViewMode === 'page' && mushafPageCount > 0);
  if (pageViewMode === 'page') showMushafPage(currentPageIdx);
  else {
    mushafPagesEl.querySelectorAll('.mushaf-page').forEach(p => p.classList.add('is-visible'));
  }
}

function showMushafPage(i) {
  const pages = mushafPagesEl.querySelectorAll('.mushaf-page');
  mushafPageCount = pages.length;
  if (!mushafPageCount) {
    if (pageNavEl) pageNavEl.classList.remove('visible');
    return;
  }
  currentPageIdx = Math.max(0, Math.min(i, mushafPageCount - 1));
  pages.forEach((p, pi) => p.classList.toggle('is-visible', pageViewMode !== 'page' || pi === currentPageIdx));
  const visible = pages[currentPageIdx];
  requestAnimationFrame(markShortMushafLines);
  const pageNum = visible && visible.dataset.pageNum ? visible.dataset.pageNum : (currentPageIdx + 1);
  if (pageLabelEl) {
    pageLabelEl.textContent = mushafPageCount > 1
      ? ('Page ' + pageNum + ' · ' + (currentPageIdx + 1) + '/' + mushafPageCount)
      : ('Page ' + pageNum);
  }
  refreshPageNavButtons();
  if (pageNavEl) pageNavEl.classList.toggle('visible', pageViewMode === 'page' && mushafPageCount > 0);
}

function canGoPrevMushafPage() {
  if (currentPageIdx > 0) return true;
  if (browseMode === 'juz') return prevLocalJuz(currentJuz || 0) != null;
  if (isLocalReciter()) return prevLocalSurah(currentSurah) != null;
  return currentSurah > 1;
}
function canGoNextMushafPage() {
  if (currentPageIdx < mushafPageCount - 1) return true;
  if (browseMode === 'juz') return nextLocalJuz(currentJuz || 0) != null;
  if (isLocalReciter()) return nextLocalSurah(currentSurah) != null;
  return currentSurah < 114;
}
function refreshPageNavButtons() {
  if (pagePrevBtn) pagePrevBtn.disabled = !canGoPrevMushafPage();
  if (pageNextBtn) pageNextBtn.disabled = !canGoNextMushafPage();
}

function seekToFirstVerseOnVisiblePage(autoplay) {
  const page = mushafPagesEl.querySelectorAll('.mushaf-page')[currentPageIdx];
  const first = page && page.querySelector('.word[data-surah][data-ayah]');
  if (!first) return;
  const s = +first.dataset.surah, a = +first.dataset.ayah;
  const vi = VERSES.findIndex(v => v.surah === s && v.ayah === a);
  if(vi>=0){
    const v=VERSES[vi],wi=Number(first.dataset.word);
    const row=(v.words||[]).find(r=>r[0]===wi);
    seekToWordMs(Number(v.source_offset_ms)+(row?Number(row[1]):0),vi,!!autoplay);
  }
}

let pageNavBusy = false;
async function goMushafPage(delta) {
  if (pageNavBusy || pageViewMode !== 'page') return;
  const target = currentPageIdx + delta;
  if (target >= 0 && target < mushafPageCount) {
    showMushafPage(target);
    seekToFirstVerseOnVisiblePage(false);
    saveResumeState();
    return;
  }
  // Cross surah / juz boundary (Madani page 1 → 2 often means Fatiha → Baqarah).
  pageNavBusy = true;
  try {
    if (delta > 0) {
      if (browseMode === 'juz') {
        const next = nextLocalJuz(currentJuz || 0);
        if (next == null) return;
        await loadJuz(next, { openPage: 'first' });
      } else {
        const next = isLocalReciter()
          ? nextLocalSurah(currentSurah)
          : (currentSurah < 114 ? currentSurah + 1 : null);
        if (next == null) return;
        await loadSurah(next, { openPage: 'first' });
      }
    } else {
      if (browseMode === 'juz') {
        const prev = prevLocalJuz(currentJuz || 0);
        if (prev == null) return;
        await loadJuz(prev, { openPage: 'last' });
      } else {
        const prev = isLocalReciter()
          ? prevLocalSurah(currentSurah)
          : (currentSurah > 1 ? currentSurah - 1 : null);
        if (prev == null) return;
        await loadSurah(prev, { openPage: 'last' });
      }
    }
  } finally {
    pageNavBusy = false;
  }
}

function pageIndexForVerse(idx,wordIdx){
  const v=VERSES[idx];if(!v)return 0;
  const pages=mushafPagesEl.querySelectorAll('.mushaf-page');
  const scope=verseDomScope(v);
  if(wordIdx!=null){
    for(let i=0;i<pages.length;i++)if(pages[i].querySelector('.word'+scope+'[data-word="'+wordIdx+'"]'))return i;
  }
  // Keep a visible page if the current ayah crosses a page boundary and
  // there is no timed word yet. Otherwise use the first page of the ayah.
  if(pages[currentPageIdx]?.querySelector('.word'+scope))return currentPageIdx;
  for(let i=0;i<pages.length;i++)if(pages[i].querySelector('.word'+scope))return i;
  if(v.page!=null)for(let i=0;i<pages.length;i++)if(String(pages[i].dataset.pageNum)===String(v.page))return i;
  return currentPageIdx;
}
function readerActiveWordForVerse(v){
  if(pendingAudioSeek?.verse===v)return activeWordAtMs(v,pendingAudioSeek.ms)??1;
  if(v.audio!==currentAudioKey||!readerAudioMatches(v.audio))return null;
  return activeWordAtMs(v,audio.currentTime*1000);
}
function syncPageToVerse(idx){
  if(readerPresentation==='translation'||pageViewMode!=='page')return;
  const v=VERSES[idx];if(!v)return;
  const pi=pageIndexForVerse(idx,readerActiveWordForVerse(v));
  const pages=mushafPagesEl.querySelectorAll('.mushaf-page');
  if(pi!==currentPageIdx||!pages[pi]?.classList.contains('is-visible')){showMushafPage(pi);lastScrollKey='';}
}

if (pageViewSelect) {
  pageViewSelect.addEventListener('change', () => {
    pageViewMode = pageViewSelect.value;
    localStorage.setItem('quran-page-view', pageViewMode);
    applyPageViewMode();
    if (VERSES[currentVerseIdx]) scrollToPlayback(currentVerseIdx, true);
  });
}
if (followScrollSelect) {
  followScrollSelect.addEventListener('change', () => {
    followScrollMode = followScrollSelect.value;
    localStorage.setItem('quran-follow-scroll', followScrollMode);
    if (followScrollMode !== 'off' && VERSES[currentVerseIdx]) {
      scrollToPlayback(currentVerseIdx, true);
    }
  });
}
if (grammarHoverToggle) {
  grammarHoverToggle.addEventListener('change', () => {
    grammarHoverOn = grammarHoverToggle.checked;
    localStorage.setItem('quran-grammar-hover', grammarHoverOn ? '1' : '0');
    applyGrammarSettings(true);
  });
}
if (grammarClickToggle) {
  grammarClickToggle.addEventListener('change', () => {
    grammarClickOn = grammarClickToggle.checked;
    localStorage.setItem('quran-grammar-click', grammarClickOn ? '1' : '0');
    applyGrammarSettings(true);
  });
}
if (pagePrevBtn) pagePrevBtn.addEventListener('click', () => goMushafPage(-1));
if (pageNextBtn) pageNextBtn.addEventListener('click', () => goMushafPage(1));

SURAH_INDEX.forEach(s => {
  const opt = document.createElement('option');
  opt.value = s.num;
  opt.textContent = s.num + '. ' + s.name + ' (' + s.nameArabic + ')';
  surahSelect.appendChild(opt);
});
surahSelect.addEventListener('change', () => {
  browseMode = 'surah';
  currentJuz = null;
  loadSurah(+surahSelect.value);
});

function refreshJuzSelect() {
  juzSelect.innerHTML = '';
  if (!LOCAL_MANIFEST || !LOCAL_MANIFEST.tracks) return;
  const juzes = [...new Set(LOCAL_MANIFEST.tracks.map(t => t.juz))].sort((a, b) => a - b);
  juzes.forEach(j => {
    const opt = document.createElement('option');
    opt.value = j;
    const tr = LOCAL_MANIFEST.tracks.find(t => t.juz === j);
    const obs = tr && tr.observed
      ? (tr.observed.start[0] + ':' + tr.observed.start[1] + '–' + tr.observed.end[0] + ':' + tr.observed.end[1])
      : '';
    opt.textContent = 'Juz ' + j + (obs ? ' (' + obs + ')' : '');
    if (currentJuz === j) opt.selected = true;
    juzSelect.appendChild(opt);
  });
}

browseModeSelect.addEventListener('change', async () => {
  browseMode = browseModeSelect.value;
  if (browseMode === 'juz') {
    if (!isLocalReciter()) {
      loadStatusEl.textContent = 'Juz mode needs the Al-Hadr (local alignments) reciter';
      loadStatusEl.classList.add('error');
      browseModeSelect.value = 'surah';
      browseMode = 'surah';
      return;
    }
    await ensureLocalManifest();
    refreshJuzSelect();
    surahSelect.style.display = 'none';
    juzSelect.style.display = '';
    const j = currentJuz || +juzSelect.value || (LOCAL_MANIFEST.tracks[0] && LOCAL_MANIFEST.tracks[0].juz) || 1;
    juzSelect.value = String(j);
    await loadJuz(j);
  } else {
    surahSelect.style.display = '';
    juzSelect.style.display = 'none';
    currentJuz = null;
    await loadSurah(currentSurah || 1);
  }
});
juzSelect.addEventListener('change', () => loadJuz(+juzSelect.value));

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
reciterSelect.addEventListener('change', async () => {
  RECITER_CONFIG = reciterSelect.value;
  refreshReciterInfo();
  if (!isLocalReciter() && browseMode === 'juz') {
    browseMode = 'surah';
    browseModeSelect.value = 'surah';
    surahSelect.style.display = '';
    juzSelect.style.display = 'none';
  }
  browseModeSelect.querySelector('option[value="juz"]').disabled = !isLocalReciter();
  if (isLocalReciter()) {
    try {
      await ensureLocalManifest();
      refreshSurahAvailability();
      refreshJuzSelect();
      // Prefer Fatiha (always in juz 1 pack); else first available local surah.
      const want = LOCAL_MANIFEST.surahNumbers.includes(currentSurah) ? currentSurah : LOCAL_MANIFEST.surahNumbers[0];
      surahSelect.value = String(want);
      if (browseMode === 'juz') await loadJuz(currentJuz || LOCAL_MANIFEST.tracks[0].juz);
      else await loadSurah(want);
    } catch (err) {
      LOCAL_ALHADR_AVAILABLE = false;
      applyLocalAlhadrAvailability();
      loadStatusEl.textContent = err.message + ' — switched to an online reciter.';
      loadStatusEl.classList.add('error');
      refreshSurahAvailability();
      await loadSurah(currentSurah || 1);
    }
  } else {
    refreshSurahAvailability();
    loadSurah(currentSurah);
  }
});
refreshReciterInfo();
browseModeSelect.querySelector('option[value="juz"]').disabled = !isLocalReciter();

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
  loadedPageFonts.clear();
  const profile = layoutProfile();
  if (profile.tajweedForced) {
    tajweedOn = true;
    tajweedBtn.classList.add('on');
  } else if (!profile.tajweedCapable) {
    tajweedOn = false;
    tajweedBtn.classList.remove('on');
  }
  tajweedBtn.disabled = mode !== 'mushaf' || !mushafSupportsTajweed() || !!profile.tajweedForced;
  // Reloads QUSX pins for this layout — keep audio position/play state.
  const resume = {
    continuePlayback: true,
    keepPlaying: !audio.paused,
    resumeAt: audio.currentTime,
    resumeVerseIdx: currentVerseIdx,
  };
  if (browseMode === 'juz' && currentJuz != null) loadJuz(currentJuz, resume);
  else loadSurah(currentSurah, resume);
});

const fontSelect = document.getElementById('fontSelect');
TEXT_FONTS.forEach(([key, name]) => {
  const opt = document.createElement('option');
  opt.value = key;
  opt.textContent = name;
  if (key === currentTextFont) opt.selected = true;
  fontSelect.appendChild(opt);
});
fontSelect.disabled = mode === 'mushaf';
fontSelect.addEventListener('change', () => {
  currentTextFont = fontSelect.value;
  localStorage.setItem('quran-text-font', currentTextFont);
  if (!VERSES.length) return;
  // Re-paint only — never pause or seek the recitation.
  const playing = !audio.paused;
  const t = audio.currentTime;
  const idx = currentVerseIdx;
  renderMushafPages();
  lastScrollKey = '';
  currentVerseIdx = idx;
  refreshScrubber(idx);
  refreshInfoBar(idx);
  updateHighlight();
  scrollToPlayback(idx, true);
  if (Math.abs(audio.currentTime - t) > 0.05) {
    try { audio.currentTime = t; } catch (_) {}
  }
  if (playing && audio.paused) audio.play().catch(() => {});
});

// Theme toggle — the actual data-theme attribute was already set pre-paint
// by the inline script in <head>; this just wires up the button and
// persists explicit user choices, which always beat the OS preference.
const themeToggleBtn = document.getElementById('themeToggle');
const chromeMoreBtn = document.getElementById('chromeMoreBtn');
const chromeMoreEl = document.getElementById('chromeMore');
if (chromeMoreBtn && chromeMoreEl) {
  chromeMoreBtn.addEventListener('click', () => {
    const open = chromeMoreEl.classList.toggle('open');
    chromeMoreEl.hidden = !open;
    chromeMoreBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
}
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
// Silent-letter zeros (U+06DF/U+06E0) and empty-centre stop (U+06EB): in
// Letter/Word spans these read as "unknown circle" glyphs even when the
// font shapes them. Mushaf/QCF word glyphs still show the orthographic mark.
const HIDDEN_ORTHO_MARKS_RE = /[\u06DF\u06E0\u06EB]/g;
const ARABIC_RECITATION_MARKS_RE = /[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]/g;
function stripArabicRecitationMarks(text) {
  return String(text || '').replace(ARABIC_RECITATION_MARKS_RE, '').replace(/\u0640/g, '');
}
function displayLetterText(text) {
  const clean = String(text || '').replace(HIDDEN_ORTHO_MARKS_RE, '');
  return textScript === 'uthmani-simple' ? stripArabicRecitationMarks(clean) : clean;
}

// Quran Foundation word-level Uthmani Simple sidecar. QUSX stays authoritative
// for identity, page/line layout and timing; this changes display text only.
const SIMPLE_WORDS = {};
const SIMPLE_WORD_LOADS = {};
function simpleWordKey(v, wIdx) { return v.surah + ':' + v.ayah + ':' + wIdx; }
function visualWordText(v, wIdx, fallback) {
  if (textScript !== 'uthmani-simple') return fallback || '';
  return (SIMPLE_WORDS[v.surah] || {})[simpleWordKey(v, wIdx)]
    || stripArabicRecitationMarks(fallback || '');
}
async function ensureUthmaniSimple(surah) {
  if (SIMPLE_WORDS[surah]) return SIMPLE_WORDS[surah];
  if (SIMPLE_WORD_LOADS[surah]) return SIMPLE_WORD_LOADS[surah];
  SIMPLE_WORD_LOADS[surah] = (async () => {
    const out = {};
    let page = 1, totalPages = 1;
    do {
      const url = 'https://api.quran.com/api/v4/verses/by_chapter/' + surah
        + '?words=true&word_fields=text_uthmani_simple,text_uthmani'
        + '&fields=text_uthmani_simple&per_page=50&page=' + page;
      const res = await fetch(url);
      if (!res.ok) throw new Error('Uthmani Simple request failed: ' + res.status);
      const data = await res.json();
      for (const verse of (data.verses || [])) {
        for (const word of (verse.words || [])) {
          if (word.char_type_name && word.char_type_name !== 'word') continue;
          const pos = Number(word.position);
          if (!pos) continue;
          const value = word.text_uthmani_simple
            || (word.text_uthmani ? stripArabicRecitationMarks(word.text_uthmani) : '');
          if (value) out[verse.verse_key + ':' + pos] = value;
        }
      }
      totalPages = Number(data.pagination && data.pagination.total_pages) || 1;
      page++;
    } while (page <= totalPages);
    SIMPLE_WORDS[surah] = out;
    return out;
  })().catch((err) => {
    console.warn(err);
    SIMPLE_WORDS[surah] = {};
    return SIMPLE_WORDS[surah];
  });
  return SIMPLE_WORD_LOADS[surah];
}
function hydrateSimpleTextForVisibleVerses() {
  if (textScript !== 'uthmani-simple' || !VERSES.length) return;
  const missing = [...new Set(VERSES.map(v => v.surah))].filter(s => !SIMPLE_WORDS[s]);
  if (!missing.length) return;
  Promise.all(missing.map(ensureUthmaniSimple)).then(() => {
    if (textScript === 'uthmani-simple') renderMushafPages();
  });
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
  const qusxWords = v.qusxWords || [];
  const wordRow = (v.words || []).find(w => w[0] === wIdx);
  const { firstRunByWord, extraWindowsByWord } = getVerseLetterRuns(v);
  const run = firstRunByWord.get(wIdx);

  // QUSX may expose more words than letter runs — still render with word-level timing.
  if (!run) {
    if (!wordRow) return null;
    const absStart = v.source_offset_ms + wordRow[1];
    const wordSpan = document.createElement('span');
    wordSpan.className = 'word';
    wordSpan.dataset.word = wIdx;
    wordSpan.dataset.ayah = v.ayah;
    wordSpan.dataset.surah = v.surah;
    wordSpan.textContent = visualWordText(v, wIdx, qusxWords[wIdx - 1] || '');
    wordSpan.dataset.startMs = absStart;
    wordSpan.addEventListener('click', (e) => {
      e.stopPropagation();
      handleWordTap(v, wIdx, verseIdx, absStart);
    });
    bindGrammarHandlers(wordSpan, morphFor(v, wIdx), v, wIdx);
    return wordSpan;
  }

  // Always paint ONE visual word from QUSX text. Letter timestamps sometimes
  // contain the same word twice in one contiguous word_idx run when the
  // reciter repeats it — using letters.char naively then shows قالقال etc.
  const wordClusters = buildClusters(visualWordText(v, wIdx, qusxWords[wIdx - 1] || ''));
  const nClusters = wordClusters.length;
  if (!nClusters) return null;

  const runLen = run.end - run.start;
  const extras = [...(extraWindowsByWord.get(wIdx) || [])];
  // Contiguous re-recitation: N full copies of the word under one word_idx.
  let passLen = runLen;
  if (runLen > nClusters && runLen % nClusters === 0) {
    const passes = runLen / nClusters;
    passLen = nClusters;
    for (let p = 1; p < passes; p++) {
      const a = v.source_offset_ms + letters.start_ms[run.start + p * passLen];
      const b = v.source_offset_ms + letters.end_ms[run.start + p * passLen + passLen - 1];
      extras.push([a, b]);
    }
  }

  const wordSpan = document.createElement('span');
  wordSpan.className = 'word';
  wordSpan.dataset.word = wIdx;
  wordSpan.dataset.ayah = v.ayah;
  wordSpan.dataset.surah = v.surah;
  let wordStart = null;

  const appendLetter = (text, absStart, absEnd) => {
    if (wordStart === null) wordStart = absStart;
    const prevVisible = [...wordSpan.children].reverse().find(el => !el.classList.contains('mark-only'));
    // Timing often isolates a combining mark as its own step — attach to
    // previous visible letter for display, keep a zero-width timing ghost.
    if (isMarkOnly(text) && prevVisible) {
      prevVisible.textContent = displayLetterText(prevVisible.textContent + text);
      if (absEnd > +prevVisible.dataset.end) prevVisible.dataset.end = String(absEnd);
      const ghost = document.createElement('span');
      ghost.className = 'letter mark-only';
      ghost.dataset.start = absStart;
      ghost.dataset.end = absEnd;
      ghost.dataset.word = wIdx;
      ghost.dataset.ayah = v.ayah;
      ghost.dataset.surah = v.surah;
      ghost.dataset.gidx = flatLetters.length;
      ghost.dataset.attachPrev = '1';
      ghost.textContent = '';
      flatLetters.push({ verseIdx, verse: v, startMs: absStart, endMs: absEnd, char: text });
      wordSpan.appendChild(ghost);
      return;
    }
    const ch = document.createElement('span');
    ch.className = 'letter';
    ch.dataset.start = absStart;
    ch.dataset.end = absEnd;
    ch.dataset.word = wIdx;
    ch.dataset.ayah = v.ayah;
    ch.dataset.surah = v.surah;
    ch.dataset.gidx = flatLetters.length;
    const raw = isMarkOnly(text) ? ('\u0640' + text) : text;
    ch.textContent = displayLetterText(raw);
    if (!ch.textContent) ch.classList.add('mark-only');
    flatLetters.push({ verseIdx, verse: v, startMs: absStart, endMs: absEnd, char: text });
    wordSpan.appendChild(ch);
  };

  if (nClusters === passLen) {
    for (let c = 0; c < nClusters; c++) {
      const j = run.start + c;
      appendLetter(
        wordClusters[c],
        v.source_offset_ms + letters.start_ms[j],
        v.source_offset_ms + letters.end_ms[j]
      );
    }
  } else {
    // Timed segmentation differs from QUSX clusters (e.g. dagger-alif alone).
    // Still show clusters once; stretch timing across the first pass.
    for (let c = 0; c < nClusters; c++) {
      const j0 = run.start + Math.floor(c * passLen / nClusters);
      const j1 = run.start + Math.max(j0, Math.floor((c + 1) * passLen / nClusters) - 1);
      const jEnd = Math.min(j1, run.start + passLen - 1);
      appendLetter(
        wordClusters[c],
        v.source_offset_ms + letters.start_ms[j0],
        v.source_offset_ms + letters.end_ms[jEnd]
      );
    }
  }

  if (extras.length) {
    const json = JSON.stringify(extras);
    wordSpan.dataset.extraWindows = json;
    wordSpan.querySelectorAll('.letter').forEach(el => { el.dataset.extraWindows = json; });
  }
  if (wordStart != null) {
    wordSpan.dataset.startMs = wordStart;
    wordSpan.addEventListener('click', (e) => {
      e.stopPropagation();
      handleWordTap(v, wIdx, verseIdx, wordStart);
    });
  }
  bindGrammarHandlers(wordSpan, morphFor(v, wIdx), v, wIdx);
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

function buildMushafGlyphSpan(v, wIdx, wordStart, verseIdx) {
  const map = activeGlyphMap();
  if (!map) return null;
  const glyphWords = (map[v.surah] || map[String(v.surah)] || {})[v.ayah]
    || (map[v.surah] || map[String(v.surah)] || {})[String(v.ayah)]
    || '';
  const glyphChar = glyphWords[wIdx - 1];
  if (!glyphChar) return null;
  const gSpan = document.createElement('span');
  gSpan.className = 'word mushaf-glyph';
  gSpan.dataset.word = wIdx;
  gSpan.dataset.ayah = v.ayah;
  gSpan.dataset.surah = v.surah;
  gSpan.textContent = glyphChar;
  if (wordStart != null) {
    gSpan.addEventListener('click', (e) => {
      e.stopPropagation();
      handleWordTap(v, wIdx, verseIdx, wordStart);
    });
  }
  return gSpan;
}

// Unicode-script layouts (Qatar / IndoPak / Nastaleeq): plain word text in
// the layout's print face, still wrapped on THIS layout's real page/line
// pins from its own .qusx.xml.
function buildMushafPlainSpan(v, wIdx, wordText, wordStart, verseIdx) {
  if (!wordText) return null;
  const gSpan = document.createElement('span');
  gSpan.className = 'word mushaf-glyph';
  gSpan.dataset.word = wIdx;
  gSpan.dataset.ayah = v.ayah;
  gSpan.dataset.surah = v.surah;
  gSpan.textContent = visualWordText(v, wIdx, wordText);
  if (wordStart != null) {
    gSpan.addEventListener('click', (e) => {
      e.stopPropagation();
      handleWordTap(v, wIdx, verseIdx, wordStart);
    });
  }
  return gSpan;
}

function readerGroupWordPages(verses){
  const groups=[];
  for(const v of verses){
    const count=(v.qusxWords||[]).length;
    if(!count)continue;
    for(let wi=1;wi<=count;wi++){
      const page=v.wordPages?.[wi-1]??v.page;
      let g=groups[groups.length-1];
      if(!g||g.page!==page){g={page,verses:[],segments:[]};groups.push(g);}
      let segment=g.segments[g.segments.length-1];
      if(!segment||segment.v!==v){segment={v,from:wi,to:wi};g.segments.push(segment);g.verses.push(v);}
      else segment.to=wi;
    }
  }
  return groups;
}
function readerPageNumbers(verses){
  return [...new Set(verses.flatMap(v=>[v.page,...(v.wordPages||[])]).filter(Boolean))];
}
function renderMushafPages() {
  if(readerPresentation==='translation'){renderVerseReader();return;}
  readerStopGloss();readerClearLetterRange();
  mushafPagesEl.innerHTML = '';
  if (!VERSES.length) return;
  // Both views use intact Arabic word text for Unicode, with ranges for
  // phoneme highlighting. Authentic loaded QCF word glyphs stay unchanged.
  const withLetters = mode !== 'mushaf' || textScript === 'uthmani-simple';
  flatLetters = [];
  hydrateSimpleTextForVisibleVerses();
  const sMeta = SURAH_INDEX.find(x => x.num === currentSurah);

  const pageGroups=readerGroupWordPages(VERSES);

  pageGroups.forEach((g, gi) => {
    const pageDiv = document.createElement('div');
    pageDiv.className = 'mushaf-page';
    pageDiv.dataset.pageIdx = gi;
    if (g.page != null) pageDiv.dataset.pageNum = g.page;

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

    // Per-surah basmalah (not only at the start of the whole view — needed for Juz mode).
    // Injected just before the first ayah of each eligible surah on this page.
    const shownBismillah = new Set();

    const flow = document.createElement('div');
    flow.className = 'verse-text mushaf-text' + (withLetters ? ' with-letters' : '');
    flow.lang='ar';flow.dir='rtl';
    const profile = layoutProfile();
    const fontEdition=profile.pageFont==='v1'?'v1':((tajweedOn||profile.tajweedForced)?'v4':'v2');
    const useGlyphs=!withLetters&&profile.kind==='glyph'&&g.page&&loadedPageFonts.has(fontEdition+':'+g.page);
    if(!useGlyphs)flow.classList.add('native-words');
    if (useGlyphs) {
      flow.style.fontFamily = QCF_FAMILY_PREFIX[fontEdition] + g.page + ', "Traditional Arabic", serif';
    } else if (withLetters) {
      flow.style.fontFamily = textFontCss();
      if (textFontIsNastaleeq()) flow.classList.add('is-nastaleeq');
    } else if (profile.unicodeFamily) {
      flow.style.fontFamily = "'" + profile.unicodeFamily + "', 'UthmanicHafs', 'Traditional Arabic', serif";
      if (profile.unicodeFamily === 'IndoPakNastaleeq' || profile.unicodeFamily === 'KFGQPCNastaleeq') {
        flow.classList.add('is-nastaleeq');
      }
    } else {
      flow.style.fontFamily = "'UthmanicHafs', 'Traditional Arabic', 'Scheherazade New', serif";
    }

    let curLineNum = null;
    let lineDiv = null;
    for(const segment of g.segments){
      const v=segment.v;
      const verseIdx=VERSES.indexOf(v);
      const vMeta = SURAH_INDEX.find(x => x.num === v.surah);
      if (segment.from===1 && v.ayah === 1 && vMeta && vMeta.bismillahPre && v.surah !== 1 && !shownBismillah.has(v.surah)) {
        shownBismillah.add(v.surah);
        const bismRows = v.basmalahWords;
        const b = document.createElement('div');
        b.className = 'bismillah';
        b.dataset.surah = v.surah;
        if (bismRows && bismRows.length) {
          bismRows.forEach(([wIdx, s, e, text]) => {
            const span = document.createElement('span');
            span.className = 'word bismillah-word';
            span.dataset.bismillah = '1';
            span.dataset.word = wIdx;
            span.dataset.startMs = v.source_offset_ms + s;
            span.dataset.endMs = v.source_offset_ms + e;
            span.textContent = textScript === 'uthmani-simple' ? stripArabicRecitationMarks(text || '') : (text || '');
            const absStart = v.source_offset_ms + s;
            span.addEventListener('click', (e2) => {
              e2.stopPropagation();
              seekToWordMs(absStart, verseIdx, true);
            });
            b.appendChild(span);
            b.appendChild(document.createTextNode(' '));
          });
        } else {
          b.textContent = textScript === 'uthmani-simple'
            ? 'بسم الله الرحمن الرحيم'
            : 'بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ';
        }
        // Put basmalah above the flow for first page verse, else as a line break inside flow.
        if (!flow.childNodes.length && pageDiv.childNodes.length <= 1) {
          pageDiv.appendChild(b);
        } else {
          const wrap = document.createElement('div');
          wrap.className = 'mushaf-line is-short';
          wrap.appendChild(b);
          flow.appendChild(wrap);
          lineDiv = null;
          curLineNum = null;
        }
      }
      const wordLines = v.wordLines || [];
      const qusxWords = v.qusxWords || [];
      const wordTimeMs = new Map();
      for (const [wIdx, s] of (v.words || [])) wordTimeMs.set(wIdx, v.source_offset_ms + s);

      for(let wIdx=segment.from;wIdx<=segment.to;wIdx++){
        const thisLine = wordLines[wIdx - 1];
        if (!lineDiv || (thisLine != null && thisLine !== curLineNum)) {
          lineDiv = document.createElement('div');
          lineDiv.className = 'mushaf-line';
          flow.appendChild(lineDiv);
          curLineNum = thisLine;
        }
        const wordStart=wordTimeMs.has(wIdx)?wordTimeMs.get(wIdx):null;
        let word=useGlyphs?buildMushafGlyphSpan(v,wIdx,wordStart,verseIdx):null;
        if(!word){
          word=readerBuildShapedWord(v,wIdx,verseIdx);
          if(useGlyphs)word.classList.add('unicode-fallback');
        }
        lineDiv.appendChild(word);
      }
      if(segment.to!==qusxWords.length)continue;
      if (useGlyphs) {
        // The font's own trailing ayah-number glyph — the real mushaf's
        // ornamental end-of-verse marker, non-interactive (no audio of its
        // own), inline right after the verse's last word like the real page.
        const map = activeGlyphMap() || {};
        const glyphWords = (map[v.surah] || map[String(v.surah)] || {})[v.ayah]
          || (map[v.surah] || map[String(v.surah)] || {})[String(v.ayah)]
          || '';
        const numGlyph = glyphWords[glyphWords.length - 1];
        if (numGlyph && lineDiv) {
          const numSpan = document.createElement('span');
          numSpan.className = 'mushaf-num-glyph';
          numSpan.textContent = numGlyph;
          lineDiv.appendChild(numSpan);
        }
      } else if (lineDiv) {
        // Letter/Word hybrid + Unicode layouts: circled ayah pin.
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
  mushafPageCount = pageGroups.length;
  // Keep the viewer on the page that matches the current ayah (or first page).
  currentPageIdx=pageIndexForVerse(currentVerseIdx,VERSES[currentVerseIdx]?readerActiveWordForVerse(VERSES[currentVerseIdx]):null);
  applyPageViewMode();
  // Defer until fonts/glyphs have laid out so short-line detection is real.
  requestAnimationFrame(() => requestAnimationFrame(markShortMushafLines));
}


function readerFitScale(available,required) {
  return available>0&&required>0?Math.min(1,available/required):1;
}
function markShortMushafLines() {
  // Measure at the requested type size, not at a previously reduced size.
  // Scale an entire printed page uniformly; never wrap/reorder its lines.
  const pages=[...mushafPagesEl.querySelectorAll('.mushaf-text')].filter(page=>page.getBoundingClientRect().width>0);
  for(const page of pages)page.style.removeProperty('font-size');
  for(const page of pages){
    const base=parseFloat(getComputedStyle(page).fontSize);
    let factor=1;
    for(const line of page.querySelectorAll('.mushaf-line')){
      line.classList.toggle('is-short',line.children.length<2);
      if(line.querySelector(':scope > .bismillah'))continue;
      const children=[...line.children];
      if(!children.length)continue;
      const gap=parseFloat(getComputedStyle(line).columnGap)||0;
      const width=children.reduce((sum,child)=>{
        const style=getComputedStyle(child);
        return sum+child.getBoundingClientRect().width+(parseFloat(style.marginLeft)||0)+(parseFloat(style.marginRight)||0);
      },0)+gap*Math.max(0,children.length-1);
      // Sparse lines (especially chapter starts/ends) should not be stretched
      // into widely separated words. Genuine full lines retain their layout.
      if(width<line.clientWidth*.68)line.classList.add('is-short');
      factor=Math.min(factor,readerFitScale(Math.max(1,line.clientWidth-6),width));
    }
    if(factor<1&&base>0)page.style.fontSize=(Math.floor(base*factor*10)/10)+'px';
  }
}
function syncReaderChromeInsets(){
  const header=document.getElementById('readerHeader');
  const bar=document.getElementById('readerModeBar');
  const player=document.querySelector('.controls');
  const sticky=bar&&getComputedStyle(bar).position==='sticky';
  const top=(header?.getBoundingClientRect().height||56)+(sticky?bar.getBoundingClientRect().height:0);
  const bottom=player?.getBoundingClientRect().height||0;
  document.documentElement.style.setProperty('--reader-top-inset',Math.ceil(top)+'px');
  document.documentElement.style.setProperty('--reader-bottom-inset',Math.ceil(bottom)+'px');
}

let mushafJustifyTimer = null;
window.addEventListener('resize', () => {
  clearTimeout(mushafJustifyTimer);
  mushafJustifyTimer = setTimeout(()=>{syncReaderChromeInsets();markShortMushafLines();},120);
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
    b.textContent = (browseMode === 'juz') ? (v.surah + ':' + v.ayah) : String(v.ayah);
    b.title = v.surah + ':' + v.ayah;
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
  const v = VERSES[idx];
  if (!v) return;
  currentSurah = v.surah;
  const s = SURAH_INDEX.find(x => x.num === v.surah);
  const place = s && s.revelationPlace ? (s.revelationPlace === 'makkah' ? 'Makkan' : 'Madinan') : null;
  let text = (browseMode === 'juz' ? ('Juz ' + (currentJuz || v.localJuz || '') + ' · ') : '')
    + (s ? s.name : v.surah) + ' ' + v.ayah;
  if (place) text += ' · ' + place;
  infoMeta.textContent = text;
  readerSync(idx);
  readerUpdatePlayButtons();
}

// The HF datasets-server /rows endpoint caps `length` at 100 — many surahs
// (Al-Baqarah has 286 ayahs) exceed that, so fetch in <=100-row pages and
// concatenate. Pages are independent (known offsets upfront), so fetch them
// concurrently rather than sequentially.
const ROWS_PAGE_SIZE = 100;
async function fetchAllRows(surah,length){
  const config=RECITER_CONFIG,result=[];
  for(let offset=0;offset<=length+100;offset+=100){
    const query=new URLSearchParams({dataset:'hetchyy/quranic-universal-ayahs',config,split:'train',where:'"surah"='+surah,offset:String(offset),length:'100'});
    const res=await fetch('https://datasets-server.huggingface.co/filter?'+query);
    if(!res.ok)throw Error('Recitation lookup failed ('+res.status+'). Try another reciter.');
    const data=await res.json();
    if(!Array.isArray(data.rows))throw Error('Invalid recitation response');
    result.push(...data.rows);
    if(data.rows.length<100||result.length>=Number(data.num_rows_total))break;
  }
  return result.filter(x=>Number(x.row?.surah)===surah);
}
function readerClipUrl(row){
  const entry=Array.isArray(row.audio)?row.audio[0]:row.audio;
  const src=typeof entry==='string'?entry:entry?.src;
  return typeof src==='string'&&src.startsWith('https://')?src:null;
}
function readerWordMapping(canonical,recited,allowBasmalah){
  const base=canonical.map(normalizeArabicLocal);
  const raw=String(recited||'').trim().split(/\s+/);
  // Standalone punctuation is not a recited word. Preserve its original index
  // rather than shifting subsequent timestamp identifiers.
  const tokens=raw.map(normalizeArabicLocal);
  if(!base.length||base.some(x=>!x)||!tokens.length)return null;
  const basmalah=['بسم','الله','الرحمن','الرحيم'];
  const skip=allowBasmalah&&tokens.length>base.length&&basmalah.every((x,i)=>tokens[i]===x)?4:0;
  const map=new Map();let next=0,prev=-1;
  for(let i=skip;i<tokens.length;i++){
    const token=tokens[i];if(!token)continue;
    let hit=-1;
    if(next<base.length&&token===base[next]){hit=next;next++;}
    else if(prev+1<next&&token===base[prev+1])hit=prev+1;
    else{
      const matches=[];
      for(let j=0;j<next;j++)if(base[j]===token)matches.push(j);
      if(matches.length!==1)return null;
      hit=matches[0];
    }
    prev=hit;map.set(i+1,hit+1);
  }
  return next===base.length?{map,skip,raw}:null;
}
function readerValidSpan(offset,duration){
  const numeric=x=> (typeof x==='number'||(typeof x==='string'&&x.trim()!==''))&&Number.isFinite(Number(x));
  return numeric(offset)&&numeric(duration)&&Number(offset)>=0&&Number(duration)>0&&Number.isFinite(Number(offset)+Number(duration));
}
function readerContainsTime(v,ms){
  return !!v&&Number.isFinite(ms)&&readerValidSpan(v.source_offset_ms,v.duration_ms)&&ms>=Number(v.source_offset_ms)&&ms<Number(v.source_offset_ms)+Number(v.duration_ms);
}
function readerAlignTiming(row,canonical,allowBasmalah){
  const mapping=readerWordMapping(canonical,row.text_uthmani||row.text,allowBasmalah);
  const duration=Number(row.duration_ms),offset=Number(row.source_offset_ms);
  const empty={words:[],letters:{word_idx:[],start_ms:[],end_ms:[]},basmalahWords:null,source_offset_ms:offset,duration_ms:duration,alignmentVerified:false};
  if(!readerValidSpan(row.source_offset_ms,row.duration_ms)||!mapping)return empty;
  if(!Array.isArray(row.word_timestamps))return empty;
  const words=[],basmalahWords=[],seenIds=new Set();
  for(const item of row.word_timestamps){
    if(!Array.isArray(item)||item.length<3||item.slice(0,3).some(x=>x==null||x===''||typeof x==='boolean'))return empty;
    const [id,s,e]=item.map(Number);
    if(!Number.isInteger(id)||id<1||!Number.isFinite(s)||!Number.isFinite(e)||s<0||e<s||s>duration+100||e>duration+100)return empty;
    if(seenIds.has(id))return empty;
    seenIds.add(id);
    if(id<=mapping.skip){basmalahWords.push([id,s,e,mapping.raw[id-1]||'']);continue;}
    const w=mapping.map.get(id);if(!w)return empty;
    words.push([w,s,e]);
  }
  if(!words.length||new Set(words.map(w=>w[0])).size!==canonical.length)return empty;
  const input=row.letter_timestamps||{},letters={word_idx:[],start_ms:[],end_ms:[]};
  for(let i=0;i<(input.word_idx||[]).length;i++){
    const w=mapping.map.get(Number(input.word_idx[i])),s=Number(input.start_ms?.[i]),e=Number(input.end_ms?.[i]);
    if(!w||!Number.isFinite(s)||!Number.isFinite(e)||s<0||e<s||e>duration+100)continue;
    letters.word_idx.push(w);letters.start_ms.push(s);letters.end_ms.push(e);
  }
  return {...empty,words:repairWordTimestamps(words),letters,basmalahWords:basmalahWords.length?basmalahWords:null,alignmentVerified:true};
}
function readerOnlineVerse(row,meta,surah,ayah,hasBasmalah){
  const canonical=meta.words||[],clip=row&&readerClipUrl(row),duration=Number(row?.duration_ms);
  const available=!!clip&&readerValidSpan(0,row?.duration_ms);
  const timing=available?readerAlignTiming({...row,source_offset_ms:0},canonical,hasBasmalah):{words:[],letters:{word_idx:[],start_ms:[],end_ms:[]},basmalahWords:null,alignmentVerified:false};
  return {surah,ayah,text:meta.text||canonical.join(' '),qusxWords:canonical,audio:available?clip:null,source_offset_ms:0,duration_ms:available?duration:0,...timing,clipRelative:true,
    juz:meta.juz,hizb:meta.hizb,rub:meta.rub,manzil:meta.manzil,page:meta.page,ruku:meta.ruku,sajda:meta.sajda,fragments:meta.fragments||{},wordLines:meta.wordLines||[],wordPages:meta.wordPages||[]};
}

let surahAdvanceBusy = false;

function normalizeArabicLocal(s) {
  if (!s) return '';
  return s
    .normalize('NFD')
    .replace(/[\u064B-\u065F\u0670\u06D6-\u06ED\u0610-\u061A]/g, '')
    .replace(/ـ/g, '') // tatweel is typography, not a recited letter
    .replace(/[ٱأإآ]/g, 'ا')
    .replace(/ة/g, 'ه')
    .replace(/ى/g, 'ي')
    .replace(/[^\u0621-\u064A]/g, '');
}

// Canonical Uthmani alignments store basmalah as the first words of each
// surah's ayah 1. QUSX keeps basmalah out of the ayah word stream
// (bismillahPre) — so without remapping, الم is timing word 5 while the
// on-screen QUSX word is position 1, and Alif-Laam-Meem never highlights.
function remapLocalTimingToQusx(r, qusxWords, bismillahPre) {
  const alignWords = String(r.text || '').trim().split(/\s+/).filter(Boolean);
  let skip = 0;
  if (bismillahPre && qusxWords.length && alignWords.length > qusxWords.length) {
    if (normalizeArabicLocal(alignWords[0]) === 'بسم') {
      skip = Math.min(4, alignWords.length - qusxWords.length);
    }
  }
  if (!skip) {
    return {
      words: r.word_timestamps,
      letters: r.letter_timestamps,
      source_offset_ms: r.source_offset_ms,
      duration_ms: r.duration_ms,
      basmalahWords: null,
    };
  }
  const body = (r.word_timestamps || []).filter(([wIdx]) => wIdx > skip);
  if (!body.length) {
    return {
      words: r.word_timestamps,
      letters: r.letter_timestamps,
      source_offset_ms: r.source_offset_ms,
      duration_ms: r.duration_ms,
      basmalahWords: null,
    };
  }
  const basmalahRows = (r.word_timestamps || [])
    .filter(([wIdx]) => wIdx <= skip)
    .map(([wIdx, s, e]) => [wIdx, s, e, alignWords[wIdx - 1] || '']);
  // Keep ayah span covering basmalah + body so verseAtMs still tracks the
  // full recited block; body word indexes match QUSX (الم = 1).
  const words = body.map(([wIdx, s, e]) => [wIdx - skip, s, e]);
  const letters = r.letter_timestamps || { word_idx: [], start_ms: [], end_ms: [] };
  const lw = [], ls = [], le = [];
  for (let i = 0; i < (letters.word_idx || []).length; i++) {
    const w = letters.word_idx[i];
    if (w <= skip) continue;
    lw.push(w - skip);
    ls.push(letters.start_ms[i]);
    le.push(letters.end_ms[i]);
  }
  return {
    words,
    letters: { word_idx: lw, start_ms: ls, end_ms: le },
    source_offset_ms: r.source_offset_ms,
    duration_ms: r.duration_ms,
    basmalahWords: basmalahRows,
  };
}

function morphFor(v, wIdx) {
  if (!v) return null;
  return MORPHOLOGY[v.surah + ':' + v.ayah + ':' + wIdx]
    || MORPHOLOGY[v.ayah + ':' + wIdx]
    || null;
}

function parseQusxXml(xmlText) {
  const doc = new DOMParser().parseFromString(xmlText, 'application/xml');
  if (doc.querySelector('parsererror')) throw new Error('QUSX XML parse error');
  const newMorph = {};
  const ayahMeta = {};
  let curAyah = null;
  let curJuz = null, curHizb = null, curRub = null, curManzil = null, curPage = null, curRuku = null, curLine = null;
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
        words: [], wordIds: [], wordLines: [], wordPages: [],
      }, ayahMeta[curAyah] || {});
    } else if (tag === 'word' && curAyah) {
      if (el.getAttribute('type') !== 'number') {
        wordBuf.push(el.textContent);
        ayahMeta[curAyah].words.push(el.textContent);
        ayahMeta[curAyah].wordIds.push(el.getAttribute('id'));
        ayahMeta[curAyah].wordLines.push(curLine);
        ayahMeta[curAyah].wordPages.push(curPage);
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
  return { ayahMeta, newMorph };
}

function repairWordTimestamps(words) {
  // Expand zero-duration stamps so highlight windows are never empty.
  const rows = [...(words || [])].sort((a, b) => a[1] - b[1] || a[0] - b[0]);
  return rows.map((row, i) => {
    const [wIdx, s, e] = row;
    let end = e;
    if (!(end > s)) {
      end = (i + 1 < rows.length) ? Math.max(s + 40, rows[i + 1][1]) : s + 80;
      if (!(end > s)) end = s + 80;
    }
    return [wIdx, s, end];
  });
}

function buildLocalVerse(r, metaA, surahNumForBismillah) {
  if(!Array.isArray(metaA.words)||!metaA.words.length)throw Error('Missing canonical text for '+r.surah+':'+r.ayah);
  const qusxWords = metaA.words;
  const sMeta = SURAH_INDEX.find(s => s.num === (surahNumForBismillah || r.surah));
  const bismillahPre = !!(sMeta && sMeta.bismillahPre);
  const remapped=readerAlignTiming(r,qusxWords,bismillahPre&&r.ayah===1&&r.surah!==1);
  return {
    surah: r.surah,
    ayah: r.ayah,
    text: metaA.text || qusxWords.join(' '),
    qusxWords,
    audio: readerValidSpan(r.source_offset_ms,r.duration_ms)?r.audio:null,
    duration_ms: remapped.duration_ms,
    source_offset_ms: remapped.source_offset_ms,
    words: repairWordTimestamps(remapped.words),
    letters: remapped.letters,
    basmalahWords: remapped.basmalahWords,
    alignmentVerified:remapped.alignmentVerified,
    juz: metaA.juz, hizb: metaA.hizb, rub: metaA.rub, manzil: metaA.manzil, page: metaA.page, ruku: metaA.ruku, sajda: metaA.sajda,
    fragments: metaA.fragments || {},
    wordLines: metaA.wordLines || [], wordPages: metaA.wordPages || [],
    localJuz: r.juz,
  };
}

function readerLocalSurahVerses(pack,ayahMeta,num,count){
  const byAyah=new Map(),duplicates=new Set();
  for(const row of (Array.isArray(pack?.ayahs)?pack.ayahs:[])){
    const ayah=Number(row?.ayah);
    if(Number(row?.surah)!==num||!Number.isInteger(ayah)||ayah<1||ayah>count)continue;
    if(byAyah.has(ayah))duplicates.add(ayah);
    else byAyah.set(ayah,row);
  }
  return Array.from({length:count},(_,i)=>{
    const ayah=i+1;
    const row=duplicates.has(ayah)?null:byAyah.get(ayah);
    return buildLocalVerse(row?{...row,surah:num,ayah}:{surah:num,ayah,text:'',audio:null,source_offset_ms:0,duration_ms:0,word_timestamps:[]},ayahMeta[ayah]||{},num);
  });
}
function collectLocalJuzAyahs(juz) {
  const want = +juz;
  const out = [];
  for (const sn of (LOCAL_MANIFEST.surahNumbers || [])) {
    const pack = LOCAL_MANIFEST.surahs[String(sn)];
    if (!pack) continue;
    for (const a of pack.ayahs) {
      if (+a.juz === want) out.push(a);
    }
  }
  // Keep mushaf order: surah then ayah (surahNumbers is already sorted).
  out.sort((a, b) => (a.surah - b.surah) || (a.ayah - b.ayah));
  return out;
}

async function loadJuz(juzNum, opts) {
  opts = opts || {};
  if (!isLocalReciter()) throw new Error('Juz mode requires local Al-Hadr reciter');
  const wasPlaying=!audio.paused||!!pendingAudioSeek?.autoplay;
  const request=++readerLoadToken;readerLoading=true;cancelPendingAudioSeek();cancelTapWordStop();audio.pause();
  try{await ensureLocalManifest();}catch(e){if(request===readerLoadToken){readerLoading=false;currentAudioKey=null;clearHighlights();loadStatusEl.textContent='Could not load Al-Hadr timing: '+e.message;loadStatusEl.classList.add('error');}return;}
  if(request!==readerLoadToken)return;
  browseMode = 'juz';
  browseModeSelect.value = 'juz';
  surahSelect.style.display = 'none';
  juzSelect.style.display = '';
  currentJuz = juzNum;
  refreshJuzSelect();
  juzSelect.value = String(juzNum);

  const continuePlayback = !!opts.continuePlayback;
  const prevAudioKey = currentAudioKey;
  const prevTime = audio.currentTime;
  const keepPlaying = opts.keepPlaying != null ? !!opts.keepPlaying : (wasPlaying || continuePlayback);

  loadStatusEl.textContent = 'Loading Juz ' + juzNum + '…';
  loadStatusEl.classList.remove('error');
  audio.pause();
  if (!continuePlayback) currentAudioKey = null;
  hideInspector();

  try {
    const ayahs = collectLocalJuzAyahs(juzNum);
    if (!ayahs.length) throw new Error('No local ayahs for Juz ' + juzNum);
    const surahNums = [...new Set(ayahs.map(a => a.surah))];
    const xmlResults = await Promise.all(surahNums.map(async sn => {
      const xmlUrl = 'https://raw.githubusercontent.com/dfordev1/usxv2/main/output/' + currentLayout + '/'
        + String(sn).padStart(3, '0') + '.qusx.xml';
      const res = await fetch(xmlUrl);
      if (!res.ok) throw new Error('QUSX fetch failed for surah ' + sn + ' (' + res.status + ')');
      return [sn, parseQusxXml(await res.text())];
    }));
    if(request!==readerLoadToken)return;
    const bySurah = Object.fromEntries(xmlResults);
    MORPHOLOGY = {};
    for (const sn of surahNums) {
      for (const [k, v] of Object.entries(bySurah[sn].newMorph)) {
        MORPHOLOGY[sn + ':' + k] = v; // sn:ayah:pos
      }
    }

    VERSES = ayahs.map(r => {
      const parsed = bySurah[r.surah];
      const metaA = (parsed && parsed.ayahMeta[r.ayah]) || {};
      return buildLocalVerse(r, metaA, r.surah);
    });
    if(!VERSES.length)throw Error('No aligned verses available');
    currentSurah = VERSES[0].surah;
    currentVerseIdx=0;
    renderAll();
    lastScrollKey = '';
    const resumeAt = opts.resumeAt != null ? opts.resumeAt : prevTime;
    const targetIdx=opts.resumeSurah!=null&&opts.resumeAyah!=null?findVerseIdx(opts.resumeSurah,opts.resumeAyah):-1;
    let idx=targetIdx>=0?targetIdx:(Number.isInteger(opts.resumeVerseIdx)&&VERSES[opts.resumeVerseIdx]?opts.resumeVerseIdx:0);
    if(targetIdx<0 && opts.resumeVerseIdx==null && continuePlayback && prevAudioKey && VERSES.some(v=>v.audio===prevAudioKey)){
      const located=readerVerseAtTime(VERSES,prevAudioKey,prevTime*1000,idx);
      if(located>=0)idx=located;
    }
    const target=VERSES[idx];
    const requestedTime=Number(opts.resumeAt);
    const candidate=targetIdx>=0&&opts.resumeAt!=null?requestedTime:(continuePlayback&&prevAudioKey===target.audio?resumeAt:NaN);
    const start=Number(target.source_offset_ms),end=start+Number(target.duration_ms);
    const ms=Number.isFinite(candidate)&&candidate*1000>=start-40&&candidate*1000<end?Math.max(start,candidate*1000):start;
    seekToWordMs(ms,idx,keepPlaying);
    finalizeLoadPosition({openPage:opts.openPage});

    const profile = layoutProfile();
    if (profile.kind === 'glyph') {
      const pages = readerPageNumbers(VERSES);
      const useV4 = tajweedOn || profile.tajweedForced;
      const edition = profile.pageFont === 'v1' ? 'v1' : (useV4 ? 'v4' : 'v2');
      Promise.all(pages.map(p => ensurePageFont(edition, p))).then(() => {
        if (request===readerLoadToken&&currentJuz===juzNum&&readerPresentation==='reading'){renderMushafPages();lastScrollKey='';updateHighlight();}
      }).catch(() => {});
    }

    if(!pendingAudioSeek&&!loadStatusEl.classList.contains('error'))loadStatusEl.textContent = 'Juz ' + juzNum + ' · ' + VERSES.length + ' ayahs';
  } catch (err) {
    if(request===readerLoadToken){audio.pause();loadStatusEl.textContent = 'Could not load Juz ' + juzNum + ': ' + err.message;loadStatusEl.classList.add('error');}
  }finally{if(request===readerLoadToken){readerLoading=false;if(!pendingAudioSeek&&!audio.seeking)updateHighlight();if(!loadStatusEl.classList.contains('error'))saveResumeState();}}
}

function nextLocalSurah(from) {
  if (!LOCAL_MANIFEST) return null;
  const nums = LOCAL_MANIFEST.surahNumbers || [];
  for (const n of nums) {
    if (n > from) return n;
  }
  return null;
}
function prevLocalSurah(from) {
  if (!LOCAL_MANIFEST) return null;
  const nums = LOCAL_MANIFEST.surahNumbers || [];
  let prev = null;
  for (const n of nums) {
    if (n >= from) break;
    prev = n;
  }
  return prev;
}

function nextLocalJuz(from) {
  if (!LOCAL_MANIFEST?.tracks) return null;
  const juzes = [...new Set(LOCAL_MANIFEST.tracks.map(t => t.juz))].sort((a, b) => a - b);
  for (const j of juzes) if (j > from) return j;
  return null;
}
function prevLocalJuz(from) {
  if (!LOCAL_MANIFEST?.tracks) return null;
  const juzes = [...new Set(LOCAL_MANIFEST.tracks.map(t => t.juz))].sort((a, b) => a - b);
  let prev = null;
  for (const j of juzes) {
    if (j >= from) break;
    prev = j;
  }
  return prev;
}

function findVerseIdx(surah, ayah) {
  return VERSES.findIndex(v => v.surah === +surah && v.ayah === +ayah);
}

function finalizeLoadPosition(opts){
  if(opts.openPage==='last') {
    showMushafPage(Math.max(0,mushafPageCount-1));seekToFirstVerseOnVisiblePage(false);
  }else if(opts.openPage==='first'){
    showMushafPage(0);seekToFirstVerseOnVisiblePage(false);
  }
  refreshPageNavButtons();saveResumeState();
}

const RESUME_KEY = 'quran-last-read';
let resumeSaveTimer = null;
function readResumeState() {
  try {
    const raw = localStorage.getItem(RESUME_KEY);
    if (!raw) return null;
    const s = JSON.parse(raw);
    if (!s || !s.surah) return null;
    return s;
  } catch (_) { return null; }
}
function saveResumeState() {
  if(readerLoading)return;
  const v = VERSES[currentVerseIdx];
  if (!v) return;
  const state = {
    browseMode,
    surah: v.surah,
    ayah: v.ayah,
    juz: currentJuz,
    time: pendingAudioSeek?.verse===v?pendingAudioSeek.ms/1000:(currentAudioKey===v.audio?audio.currentTime:(v.source_offset_ms/1000)),
    reciter: RECITER_CONFIG,
    layout: currentLayout,
    ts: Date.now(),
  };
  try { localStorage.setItem(RESUME_KEY, JSON.stringify(state)); } catch (_) {}
}
function scheduleSaveResume() {
  clearTimeout(resumeSaveTimer);
  resumeSaveTimer = setTimeout(saveResumeState, 800);
}

function applyPlaybackSpeed(rate) {
  const r = +rate || 1;
  audio.playbackRate = r;
  try { localStorage.setItem('quran-playback-speed', String(r)); } catch (_) {}
  if (speedSelect && String(speedSelect.value) !== String(r)) speedSelect.value = String(r);
}

const speedSelect = document.getElementById('speedSelect');
(function initSpeed() {
  const saved = localStorage.getItem('quran-playback-speed') || '1';
  if (speedSelect) {
    if (![...speedSelect.options].some(o => o.value === saved)) speedSelect.value = '1';
    else speedSelect.value = saved;
    speedSelect.addEventListener('change', () => applyPlaybackSpeed(speedSelect.value));
  }
  applyPlaybackSpeed(speedSelect ? speedSelect.value : saved);
})();

// Fetch a surah's audio timing (QUA, per-reciter) + text/morphology (QUSX,
// canonical) live and merge them client-side by (ayah, word position) — the
// two datasets share that indexing convention, so no server-side join needed.
// Local Al-Hadr mode swaps QUA for offline juz opus + canonical word alignments.
// opts.continuePlayback: keep audio rolling across surah boundaries (Fatiha→Baqarah).
async function loadSurah(num, opts) {
  opts = opts || {};
  const wasPlaying=!audio.paused||!!pendingAudioSeek?.autoplay;
  const request=++readerLoadToken;readerLoading=true;cancelPendingAudioSeek();cancelTapWordStop();
  browseMode = 'surah';
  browseModeSelect.value = 'surah';
  surahSelect.style.display = '';
  juzSelect.style.display = 'none';
  currentJuz = null;
  const continuePlayback = !!opts.continuePlayback;
  const prevAudioKey = currentAudioKey;
  const prevTime = audio.currentTime;
  const keepPlaying = opts.keepPlaying != null ? !!opts.keepPlaying : (wasPlaying || continuePlayback);

  currentSurah = num;
  surahSelect.value = String(num);
  const meta = SURAH_INDEX.find(s => s.num === num);
  loadStatusEl.textContent = 'Loading ' + meta.name + '…';
  loadStatusEl.classList.remove('error');
  audio.pause();
  if (!continuePlayback) currentAudioKey = null;
  hideInspector(); // the previously-inspected word's DOM node is about to be discarded by renderAll()

  try {
    const xmlUrl = 'https://raw.githubusercontent.com/dfordev1/usxv2/main/output/' + currentLayout + '/'
      + String(num).padStart(3, '0') + '.qusx.xml';

    let localPack = null;
    if (isLocalReciter()) {
      await ensureLocalManifest();
      if(request!==readerLoadToken)return;
      refreshSurahAvailability();
      localPack = LOCAL_MANIFEST.surahs[String(num)];
      if (!localPack) throw new Error('No local Al-Hadr timing for surah ' + num);
    }

    const timingPromise = localPack
      ? Promise.resolve(null)
      : fetchAllRows(num, meta.ayahCount);
    const [rows, xmlRes] = await Promise.all([timingPromise, fetch(xmlUrl)]);
    if (!xmlRes.ok) throw new Error('QUSX text fetch failed (' + xmlRes.status + ')');
    const xmlText = await xmlRes.text();
    if(request!==readerLoadToken)return;

    // Actually walk QUSX's milestone structure — this is a USX-style flat
    // word stream sliced by independent sid/eid boundary pins (juz, hizb,
    // rub, manzil, page, sajda, ayah), not just a bag of <word> attributes.
    // We track each axis's *currently open* pin as we walk in document
    // order, snapshot it onto each ayah, and reconstruct the ayah's own
    // canonical text from its word stream (not QUA's copy) — so QUSX is the
    // real text/structure source, and QUA is used only for audio + timing,
    // which is the division of labor this integration should have had from
    // the start.
    const { ayahMeta, newMorph } = parseQusxXml(xmlText);
    // Prefer surah-scoped morph keys; keep ayah:pos fallback for older paths.
    MORPHOLOGY = {};
    for (const [k, v] of Object.entries(newMorph)) {
      MORPHOLOGY[num + ':' + k] = v;
      MORPHOLOGY[k] = v;
    }

    if (localPack) {
      VERSES = readerLocalSurahVerses(localPack,ayahMeta,num,meta.ayahCount);
    } else {
      const byAyah=new Map();
      for(const {row} of rows){
        const ayah=Number(row?.ayah);
        if(Number(row?.surah)===num&&Number.isInteger(ayah)&&ayah>=1&&ayah<=meta.ayahCount&&!byAyah.has(ayah))byAyah.set(ayah,row);
      }
      VERSES=Array.from({length:meta.ayahCount},(_,i)=>{
        const ayah=i+1,canonical=ayahMeta[ayah];
        if(!canonical?.words?.length)throw Error('Missing canonical text for '+num+':'+ayah);
        return readerOnlineVerse(byAyah.get(ayah),canonical,num,ayah,ayah===1&&num!==1&&!!meta.bismillahPre);
      });
    }

    if(!VERSES.length)throw Error('No aligned verses available');
    currentVerseIdx=0;
    renderAll();
    lastScrollKey = '';
    const resumeAt = opts.resumeAt != null ? opts.resumeAt : prevTime;

    const targetIdx=opts.resumeSurah!=null&&opts.resumeAyah!=null?findVerseIdx(opts.resumeSurah,opts.resumeAyah):-1;
    let idx=targetIdx>=0?targetIdx:(Number.isInteger(opts.resumeVerseIdx)&&VERSES[opts.resumeVerseIdx]?opts.resumeVerseIdx:0);
    if(targetIdx<0 && opts.resumeVerseIdx==null && continuePlayback && prevAudioKey && VERSES.some(v=>v.audio===prevAudioKey)){
      const located=readerVerseAtTime(VERSES,prevAudioKey,prevTime*1000,idx);
      if(located>=0)idx=located;
    }
    const target=VERSES[idx];
    const requestedTime=Number(opts.resumeAt);
    const candidate=targetIdx>=0&&opts.resumeAt!=null?requestedTime:(continuePlayback&&prevAudioKey===target.audio?resumeAt:NaN);
    const start=Number(target.source_offset_ms),end=start+Number(target.duration_ms);
    const ms=Number.isFinite(candidate)&&candidate*1000>=start-40&&candidate*1000<end?Math.max(start,candidate*1000):start;
    seekToWordMs(ms,idx,keepPlaying);
    finalizeLoadPosition({openPage:opts.openPage});

    // Preload mushaf fonts in the background — never block Fatiha→Baqarah handoff.
    const profile = layoutProfile();
    if (profile.kind === 'glyph') {
      const pages = readerPageNumbers(VERSES);
      const useV4 = tajweedOn || profile.tajweedForced;
      const edition = profile.pageFont === 'v1' ? 'v1' : (useV4 ? 'v4' : 'v2');
      Promise.all(pages.map(p => ensurePageFont(edition, p))).then(() => {
        if(request===readerLoadToken&&currentSurah===num&&readerPresentation==='reading'){renderMushafPages();lastScrollKey='';updateHighlight();}
      }).catch(() => {});
    }

    if (browsing) exitBrowse();
    if(VERSES[currentVerseIdx]?.audio&&!pendingAudioSeek&&!loadStatusEl.classList.contains('error')){const missing=VERSES.filter(v=>!v.audio).length;loadStatusEl.textContent=meta.nameArabic+' · '+VERSES.length+' ayahs'+(missing?' · '+missing+' without aligned audio':'');}
    refreshTraditionInfo(num, meta.ayahCount);
  } catch (err) {
    if(request===readerLoadToken){audio.pause();loadStatusEl.textContent = 'Could not load ' + meta.name + ': ' + err.message;loadStatusEl.classList.add('error');}
  }finally{if(request===readerLoadToken){readerLoading=false;if(!pendingAudioSeek&&!audio.seeking)updateHighlight();if(!loadStatusEl.classList.contains('error'))saveResumeState();}}
}

function localSurahEndMs(surahNum) {
  const pack = LOCAL_MANIFEST?.surahs?.[String(surahNum)];
  if (!pack?.ayahs?.length) return null;
  const last = pack.ayahs[pack.ayahs.length - 1];
  return last.source_offset_ms + last.duration_ms;
}

async function advanceToNextLocalSurah() {
  if (!isLocalReciter() || surahAdvanceBusy) return false;
  surahAdvanceBusy = true;
  try {
    await ensureLocalManifest();
    if (browseMode === 'juz') {
      const next = nextLocalJuz(currentJuz || 0);
      if (next == null) return false;
      loadStatusEl.textContent = 'Continuing to Juz ' + next + '…';
      await loadJuz(next, { continuePlayback: true, keepPlaying:true });
      return true;
    }
    const next = nextLocalSurah(currentSurah);
    if (next == null) return false;
    loadStatusEl.textContent = 'Continuing to surah ' + next + '…';
    await loadSurah(next, { continuePlayback: true, keepPlaying:true });
    return true;
  } catch (err) {
    loadStatusEl.textContent = 'Could not continue: ' + err.message;
    loadStatusEl.classList.add('error');
    return false;
  } finally {
    surahAdvanceBusy = false;
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

let lastScrollKey = '';

function jumpToVerse(idx, autoplay=true) {
  if(!VERSES[idx])return;
  cancelTapWordStop();
  seekVerseStart(idx,autoplay);
}

function scrollToPlayback(idx, force) {
  const v = VERSES[idx];
  if (!v) return;
  syncPageToVerse(idx);
  if(readerPresentation==='translation' && audio.paused && !force)return;
  if(readerPresentation==='translation' && force && idx===0 && audio.paused){window.scrollTo({top:0,behavior:'auto'});return;}
  if (!force && followScrollMode === 'off') return;
  const scope = verseDomScope(v);
  const activeW=readerActiveWordForVerse(v);
  // Never fall back to word 1 — that caused the highlight/viewport to jump
  // backward whenever there was a gap between word windows.
  let target = null;
  if (activeW != null) {
    target = document.querySelector('.mushaf-pages .word' + scope + '[data-word="' + activeW + '"]');
  }
  if(!target&&(force||v.alignmentVerified===false)){
    target =
      document.querySelector('.mushaf-pages .word.active-word' + scope) ||
      document.querySelector('.mushaf-pages .word' + scope) ||
      document.querySelector('.mushaf-pages .mushaf-glyph' + scope);
  }
  const key = v.surah + ':' + v.ayah + ':' + (activeW != null ? activeW : (force ? 'force' : 'gap'));

  // In gaps (no active word), do not scroll at all unless forced (verse jump).
  if(!force&&activeW==null&&v.alignmentVerified!==false)return;
  if(!target)return;
  if(!force&&lastScrollKey===key)return;
  lastScrollKey=key;

  const scrollMode=force?'keep-up':followScrollMode;

  // keep-up: if the recited word sits too low (near the fixed player) or
  // off-screen, lift the page so it rests in the upper-middle reading band.
  const rect = target.getBoundingClientRect();
  const viewH = window.innerHeight || document.documentElement.clientHeight;
  const controlsEl = document.querySelector('.controls');
  const controlsH = controlsEl ? controlsEl.getBoundingClientRect().height : 110;
  const topInset=parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--reader-top-inset'))||56;
  const topBand = Math.max(viewH * 0.16,topInset+12);
  const bottomBand = viewH - controlsH - 28;
  const inComfort = rect.top >= topBand && rect.bottom <= bottomBand;
  if (!force && inComfort) return;
  if(scrollMode==='nearest'&&rect.top>=topBand&&rect.bottom<=bottomBand)return;

  const desiredTop = Math.max(topBand+8,viewH * 0.28);
  const delta = rect.top - desiredTop;
  if (Math.abs(delta) > 10) {
    window.scrollBy({top:delta,behavior:force||innerWidth<900?'auto':'smooth'});
  }
}

function readerAdvancePlayback(ended){
  if(readerLoading||pendingAudioSeek||audio.seeking||surahAdvanceBusy||browsing||tapFrameId)return;
  const v=VERSES[currentVerseIdx];
  if(!v||v.audio!==currentAudioKey||!readerAudioMatches(v.audio))return;
  if(!ended&&(v.clipRelative||audio.currentTime*1000<Number(v.source_offset_ms)+Number(v.duration_ms)))return;
  const next=VERSES[currentVerseIdx+1];
  if(next){
    if(ended||next.audio!==v.audio)jumpToVerse(currentVerseIdx+1,true);
    return;
  }
  if(isLocalReciter()){
    const available=browseMode==='juz'?nextLocalJuz(currentJuz||0):nextLocalSurah(currentSurah);
    if(available==null){audio.pause();return;}
    audio.pause();
    advanceToNextLocalSurah();
  }else if(currentSurah<114){
    audio.pause();
    loadSurah(currentSurah+1,{continuePlayback:false,keepPlaying:true});
  }else audio.pause();
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
  readerClearLetterRange();
  document.querySelectorAll('.letter.lit').forEach(el => el.classList.remove('lit'));
  document.querySelectorAll('.word.active-word,.word.active-ayah').forEach(el=>el.classList.remove('active-word','active-ayah'));
}

function readerVerseAtTime(verses,file,ms,preferred=0){
  if(!file||!Number.isFinite(ms))return -1;
  const same=v=>v&&v.audio===file&&readerValidSpan(v.source_offset_ms,v.duration_ms);
  const next=verses[preferred+1];
  if(next&&same(next)&&ms>=Number(next.source_offset_ms)&&ms<Number(next.source_offset_ms)+Number(next.duration_ms))return preferred+1;
  const cur=verses[preferred];
  if(cur&&same(cur)&&ms>=Number(cur.source_offset_ms)&&ms<Number(cur.source_offset_ms)+Number(cur.duration_ms))return preferred;
  let best=-1,bestStart=-Infinity;
  for(let i=0;i<verses.length;i++){
    const v=verses[i];if(!same(v))continue;
    const start=Number(v.source_offset_ms);
    if(start<=ms&&ms<start+Number(v.duration_ms)&&start>=bestStart){best=i;bestStart=start;}
  }
  return best;
}
function verseAtMs(ms){
  const idx=readerVerseAtTime(VERSES,currentAudioKey,ms,currentVerseIdx);
  return idx>=0?idx:currentVerseIdx;
}

function updateHighlight() {
  if(readerLoading||pendingAudioSeek||audio.seeking||!currentAudioKey||!readerAudioMatches(currentAudioKey)||loadStatusEl.classList.contains('error'))return;
  const ms=audio.currentTime*1000;
  const idx=readerVerseAtTime(VERSES,currentAudioKey,ms,currentVerseIdx);
  if(idx<0){clearHighlights();if(!audio.paused)readerAdvancePlayback(false);return;}
  const changed=idx!==currentVerseIdx;
  if (idx !== currentVerseIdx) {
    currentVerseIdx = idx;
    lastScrollKey = '';
    clearHighlights();
    refreshScrubber(idx);
    refreshInfoBar(idx);
    syncPageToVerse(idx);
  }

  const v = VERSES[currentVerseIdx];
  if (!v) return;

  const activeWord=activeWordAtMs(v,ms);
  syncPageToVerse(currentVerseIdx);
  const scope = verseDomScope(v);

  // Timed basmalah header (local Al-Hadr, surahs with bismillahPre).
  const bodyWordStart = (v.basmalahWords && v.words && v.words[0])
    ? v.source_offset_ms + v.words[0][1]
    : null;
  document.querySelectorAll('.bismillah .bismillah-word').forEach(el => {
    const parentSurah = el.closest('.bismillah');
    if (v.ayah!==1 || (parentSurah && parentSurah.dataset.surah !== String(v.surah))) {
      el.classList.remove('active-word');
      return;
    }
    const s = +el.dataset.startMs, e = +el.dataset.endMs;
    let end = e + 40;
    const nextEl = el.nextElementSibling;
    if (nextEl && nextEl.classList && nextEl.classList.contains('bismillah-word')) {
      end = +nextEl.dataset.startMs;
    } else if (bodyWordStart != null) {
      end = bodyWordStart;
    }
    el.classList.toggle('active-word', ms >= s && ms < end);
  });

  readerHighlightCurrentLetter(v,activeWord,ms);
  // Native text range highlighting works in both views; no per-letter DOM split.
  document.querySelectorAll('.mushaf-pages .letter.lit').forEach(el=>el.classList.remove('lit'));

  // Word wash/box for Letter, Word, and Mushaf (Letter uses a lighter wash via CSS).
  document.querySelectorAll('.mushaf-pages .word' + scope).forEach(el => {
    el.classList.toggle('active-word',activeWord!==null&&+el.dataset.word===activeWord);
    el.classList.toggle('active-ayah',v.alignmentVerified===false&&!audio.paused);
  });
  document.querySelectorAll('.mushaf-pages .word.active-word,.mushaf-pages .word.active-ayah').forEach(el => {
    if(el.classList.contains('bismillah-word'))return;
    if (el.dataset.surah !== String(v.surah) || el.dataset.ayah !== String(v.ayah)) {
      el.classList.remove('active-word','active-ayah');
    }
  });
  scrollToPlayback(currentVerseIdx,changed&&!audio.paused&&followScrollMode!=='off');
  if(!audio.paused)readerAdvancePlayback(false);
}

audio.addEventListener('timeupdate', () => {
  updateHighlight();
  if (audio.duration && !userSeeking) {
    seek.value = (audio.currentTime / audio.duration) * 1000;
  }
  curTimeEl.textContent = fmtTime(audio.currentTime * 1000);
  totTimeEl.textContent = fmtTime((audio.duration || 0) * 1000);
  scheduleSaveResume();
});

audio.addEventListener('play', () => {
  revealPlaybackChrome();
  playBtn.innerHTML = '&#10074;&#10074;';
  applyPlaybackSpeed(speedSelect ? speedSelect.value : (localStorage.getItem('quran-playback-speed') || '1'));
});
audio.addEventListener('pause', () => {
  playBtn.innerHTML = '&#9658;';
  saveResumeState();
  scheduleChromeConceal();
});
audio.addEventListener('ended',()=>{
  const singleWord=!!tapFrameId;cancelTapWordStop();
  updateHighlight();playBtn.innerHTML='&#9658;';saveResumeState();if(!singleWord)readerAdvancePlayback(true);
});
audio.addEventListener('seeked',()=>{lastScrollKey='';updateHighlight();});
audio.addEventListener('playing',()=>{lastScrollKey='';updateHighlight();});
document.addEventListener('visibilitychange',()=>{if(!document.hidden){lastScrollKey='';updateHighlight();}});

window.addEventListener('beforeunload', saveResumeState);
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') saveResumeState();
});

prevAyahBtn.addEventListener('click', () => {
  if(readerLoading)return;
  revealPlaybackChrome();
  if (currentVerseIdx > 0) jumpToVerse(currentVerseIdx - 1, !audio.paused);
});
nextAyahBtn.addEventListener('click', () => {
  if(readerLoading)return;
  revealPlaybackChrome();
  if (currentVerseIdx < VERSES.length - 1) jumpToVerse(currentVerseIdx + 1, !audio.paused);
});

playBtn.addEventListener('click', () => {
  if(readerLoading)return;
  if(pendingAudioSeek){pendingAudioSeek.autoplay=!pendingAudioSeek.autoplay;if(!pendingAudioSeek.autoplay)cancelTapWordStop();return;}
  if (audio.paused) {
    if (browsing) exitBrowse();
    if(VERSES[currentVerseIdx])ensureAudioForVerse(currentVerseIdx,true);
  } else {
    if(pendingAudioSeek)pendingAudioSeek.autoplay=false;
    cancelTapWordStop();audio.pause();
  }
});

let chromeConcealTimer = null;
function revealPlaybackChrome() {
  if (chromeConcealTimer) clearTimeout(chromeConcealTimer);
  chromeConcealTimer = null;
  controlsEl.classList.remove('is-concealed');
  controlsRevealBtn.classList.remove('show');
}
function concealPlaybackChrome() { revealPlaybackChrome(); }
function scheduleChromeConceal() {
  if (chromeConcealTimer) clearTimeout(chromeConcealTimer);
  if (!audio.paused) return;
  chromeConcealTimer = setTimeout(concealPlaybackChrome, 2400);
}
controlsRevealBtn.addEventListener('click', () => {
  revealPlaybackChrome();
  scheduleChromeConceal();
});
controlsEl.addEventListener('pointerdown', revealPlaybackChrome);
mushafPagesEl.addEventListener('click', () => {
  if (controlsEl.classList.contains('is-concealed')) revealPlaybackChrome();
  else scheduleChromeConceal();
});
scheduleChromeConceal();

seek.addEventListener('mousedown', () => userSeeking = true);
seek.addEventListener('touchstart', () => userSeeking = true);
seek.addEventListener('change', () => {
  userSeeking=false;
  if(readerLoading||pendingAudioSeek)return;
  cancelTapWordStop();
  if(!audio.duration||!currentAudioKey)return;
  const ms=Number(seek.value)/1000*audio.duration*1000;
  const candidates=VERSES.map((v,idx)=>({v,idx})).filter(x=>x.v.audio===currentAudioKey&&readerValidSpan(x.v.source_offset_ms,x.v.duration_ms));
  if(!candidates.length)return;
  const start=Math.min(...candidates.map(x=>Number(x.v.source_offset_ms)));
  const end=Math.max(...candidates.map(x=>Number(x.v.source_offset_ms)+Number(x.v.duration_ms)));
  const target=Math.max(start,Math.min(end-1,ms));
  const idx=readerVerseAtTime(VERSES,currentAudioKey,target,currentVerseIdx);
  if(idx>=0)seekToWordMs(target,idx,!audio.paused);
  else {
    const next=candidates.filter(x=>Number(x.v.source_offset_ms)>target).sort((a,b)=>Number(a.v.source_offset_ms)-Number(b.v.source_offset_ms))[0];
    if(next)seekToWordMs(Number(next.v.source_offset_ms),next.idx,!audio.paused);
  }
});

document.getElementById('modeLetter').addEventListener('click', () => setMode('letter'));
document.getElementById('modeWord').addEventListener('click', () => setMode('word'));
document.getElementById('modeMushaf').addEventListener('click', () => setMode('mushaf'));
const tapWordBtn = document.getElementById('tapWordToggle');
function syncTapWordButton() {
  tapWordBtn.classList.toggle('on', tapWordMode);
  tapWordBtn.setAttribute('aria-pressed', tapWordMode ? 'true' : 'false');
}
syncTapWordButton();
tapWordBtn.addEventListener('click', () => {
  tapWordMode = !tapWordMode;
  localStorage.setItem('quran-tap-word-audio', tapWordMode ? '1' : '0');
  if (!tapWordMode) cancelTapWordStop();
  syncTapWordButton();
});
if (scriptSelect) {
  scriptSelect.addEventListener('change', async () => {
    textScript = scriptSelect.value;
    localStorage.setItem('quran-text-script', textScript);
    if (textScript === 'uthmani-simple') {
      tajweedOn = false;
      await Promise.all([...new Set(VERSES.map(v => v.surah))].map(ensureUthmaniSimple));
    }
    renderMushafPages();
    setMode(mode);
  });
}
const tajweedBtn = document.getElementById('tajweedToggle');
tajweedBtn.addEventListener('click', async () => {
  if (mode !== 'mushaf' || textScript === 'uthmani-simple' || !mushafSupportsTajweed()) return;
  const profile = layoutProfile();
  if (profile.tajweedForced) return; // V4 layout is always colored
  tajweedOn = !tajweedOn;
  tajweedBtn.classList.toggle('on', tajweedOn);
  if (tajweedOn) {
    const pages = readerPageNumbers(VERSES);
    await Promise.all(pages.map(p => ensurePageFont('v4', p)));
  }
  renderMushafPages();
});
function setMode(m) {
  const prev = mode;
  mode = m;
  document.body.classList.remove('follow-mode-letter', 'follow-mode-word', 'follow-mode-mushaf');
  document.body.classList.add('follow-mode-' + m);
  document.getElementById('modeLetter').classList.toggle('on', m === 'letter');
  document.getElementById('modeWord').classList.toggle('on', m === 'word');
  document.getElementById('modeMushaf').classList.toggle('on', m === 'mushaf');
  // All reading modes preserve canonical word order. Unicode words use
  // native joining; authentic QCF glyphs are used only with a loaded font.
  versesEl.style.display = 'none';
  mushafPagesEl.style.display = 'flex';
  tajweedBtn.disabled = m !== 'mushaf' || textScript === 'uthmani-simple'
    || !mushafSupportsTajweed() || !!layoutProfile().tajweedForced;
  if (textScript === 'uthmani-simple') tajweedBtn.classList.remove('on');
  fontSelect.disabled = m === 'mushaf' && textScript !== 'uthmani-simple';
  // Auto font resolves differently for Letter vs Word; always re-paint when
  // leaving/entering mushaf or when Auto is selected.
  if (VERSES.length && ((prev === 'mushaf') !== (m === 'mushaf') || currentTextFont === 'auto' || prev !== m)) {
    renderMushafPages();
  }
  clearHighlights();
}

const experienceButtons = {
  read: document.getElementById('experienceRead'),
  follow: document.getElementById('experienceFollow'),
  explore: document.getElementById('experienceExplore'),
};
function setTapWordMode(on) {
  tapWordMode = !!on;
  localStorage.setItem('quran-tap-word-audio', tapWordMode ? '1' : '0');
  if (!tapWordMode) cancelTapWordStop();
  syncTapWordButton();
}
function applyExperience(shouldRender = true) {
  document.body.dataset.experience = experience;
  document.body.dataset.readingStyle = readingStyle;
  Object.entries(experienceButtons).forEach(([key, btn]) => btn.classList.toggle('on', key === experience));
  const reflow = readingStyle === 'reflow';
  typographyPanel.classList.toggle('settings-hidden', !reflow);
  fontRow.classList.toggle('settings-hidden', !reflow);
  if (experience === 'explore') {
    setTapWordMode(true);
    setMode('word');
  } else if (experience === 'follow') {
    setTapWordMode(false);
    setMode(followPreference);
  } else {
    setTapWordMode(false);
    setMode(reflow ? 'word' : 'mushaf');
  }
  if (shouldRender && VERSES.length) renderMushafPages();
}
Object.entries(experienceButtons).forEach(([key, btn]) => {
  btn.addEventListener('click', () => {
    experience = key;
    localStorage.setItem('quran-experience', experience);
    applyExperience();
  });
});
readingStyleSelect.addEventListener('change', () => {
  readingStyle = readingStyleSelect.value;
  localStorage.setItem('quran-reading-style', readingStyle);
  applyExperience();
});
followModeSelect.addEventListener('change', () => {
  followPreference = followModeSelect.value;
  localStorage.setItem('quran-follow-mode', followPreference);
  if (experience === 'follow') applyExperience();
});
applyExperience(false);

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
  if(!flatLetters.length)return;
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
  if(!flatLetters.length)return;
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
  } else {
    for(const word of mushafPagesEl.querySelectorAll('.word'+verseDomScope(L.verse))){
      const match=(readerLetterRanges.get(word)||[]).find(r=>r.gidx===browseIdx);
      if(match){readerPaintLetterRange(word,match);word.scrollIntoView({behavior:'smooth',block:'center'});break;}
    }
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
seek.addEventListener('click', () => { if (browsing) exitBrowse(); });


  // Navigation and bookmarks delegate all reading/audio changes to the existing
  // QUSX engine. No changes to canonical words, glyphs or timing data.
  const readerUI = id => document.getElementById(id);
  let readerTab = 'surah', readerBusy = false, readerLastLocation = '';
  let readerBookmarks = [];
  try {
    const saved = JSON.parse(localStorage.getItem('qusx-reader-bookmarks') || '[]');
    if (Array.isArray(saved)) readerBookmarks = saved.filter(x => typeof x === 'string' && /^[0-9]+:[0-9]+$/.test(x));
  } catch (_) {}
  function readerSidebar(open) {
    readerUI('readerSidebar').hidden = !open;
    readerUI('readerShade').hidden = !open || innerWidth >= 900;
    document.body.classList.toggle('reader-nav-open', open);
    readerUI('readerNavToggle').setAttribute('aria-expanded', String(open));
    requestAnimationFrame(()=>{syncReaderChromeInsets();markShortMushafLines();});
  }
  function readerNav() {
    const list = readerUI('readerNavList');
    const term = readerUI('readerSearch').value.trim().toLowerCase();
    list.replaceChildren();
    let items;
    if (readerTab === 'surah') {
      items = SURAH_INDEX.map(s => ({key:String(s.num), number:s.num, name:s.name, ar:s.nameArabic, disabled:!!Array.from(surahSelect.options).find(o=>+o.value===s.num)?.disabled}));
    } else if (readerTab === 'juz') {
      if (!isLocalReciter() || !LOCAL_ALHADR_AVAILABLE) {
        const note=document.createElement('p'); note.className='reader-nav-help'; note.textContent='Choose the Al-Hadr reciter in settings to browse available juz alignments.'; list.append(note); return;
      }
      items=Array.from(juzSelect.options).map(o=>({key:o.value,number:o.value,name:'Juz '+o.value,disabled:o.disabled}));
    } else {
      items=readerBookmarks.map(key=>{const s=SURAH_INDEX.find(x=>x.num===+key.split(':')[0]); return {key,number:'★',name:(s?.name||'Surah')+' · '+key};});
    }
    for(const item of items) {
      if(term && !(item.key+' '+item.name+' '+(item.ar||'')).toLowerCase().includes(term))continue;
      const btn=document.createElement('button');btn.type='button';btn.disabled=!!item.disabled || readerBusy;
      const num=document.createElement('span');num.className='reader-nav-num';num.textContent=item.number;
      const name=document.createElement('span');name.textContent=item.name;btn.append(num,name);
      if(item.ar){const ar=document.createElement('span');ar.className='reader-nav-ar';ar.lang='ar';ar.textContent=item.ar;btn.append(ar);}
      const current=readerTab==='surah'?+item.key===currentSurah:readerTab==='juz'?browseMode==='juz'&&+item.key===currentJuz:item.key===readerLastLocation;
      if(current)btn.setAttribute('aria-current','true');
      btn.onclick=()=>readerNavigate(item.key,readerTab);list.append(btn);
    }
    if(!list.children.length){const note=document.createElement('p');note.className='reader-nav-help';note.textContent=readerTab==='saved'&&!readerBookmarks.length?'No saved verses yet.':'No matching results.';list.append(note);}
  }
  function readerSetTab(tab) {
    readerTab=tab;
    for(const [id,t] of [['readerSurahs','surah'],['readerJuz','juz'],['readerSaved','saved']])readerUI(id).setAttribute('aria-pressed',String(t===tab));
    readerUI('readerSearch').value='';readerUI('readerSearch').placeholder='Search '+(tab==='saved'?'saved verses':tab);readerNav();
  }
  function readerSync(idx) {
    const v=VERSES[idx]; if(!v)return;
    const key=v.surah+':'+v.ayah;
    if(key===readerLastLocation)return;
    readerLastLocation=key;
    const meta=SURAH_INDEX.find(s=>s.num===v.surah);
    readerUI('readerArabicName').textContent=meta?.nameArabic||'';
    readerUI('readerChapterName').textContent=meta?.name||'The Quran';
    readerUI('readerChapterMeta').textContent=(browseMode==='juz'?'Juz '+currentJuz+' · ':'')+'Surah '+v.surah+' · '+(meta?.ayahCount||'')+' verses · '+key;
    readerUI('readerAyah').max=meta?.ayahCount||1;
    if(document.activeElement!==readerUI('readerAyah'))readerUI('readerAyah').value=v.ayah;
    const saved=readerBookmarks.includes(key);
    readerUI('readerBookmark').textContent=saved?'★ Saved':'☆ Save verse';
    readerUI('readerBookmark').setAttribute('aria-pressed',String(saved));
    readerUI('readerMeanings').href='https://dfordev1.github.io/qusx-audio/#'+key;
    readerNav();
  }
  async function readerNavigate(key,tab) {
    if(readerBusy)return;
    readerBusy=true;readerNav();readerUI('readerNotice').textContent='';
    try {
      readerStopGloss();audio.pause();
      if(tab==='juz'){await loadJuz(+key,{keepPlaying:false});}
      else {
        const [sn,an]=String(key).split(':').map(Number);
        const meta=SURAH_INDEX.find(s=>s.num===sn);
        if(!meta || (an && (an<1 || an>meta.ayahCount)))throw new Error('Invalid verse');
        if(Array.from(surahSelect.options).find(o=>+o.value===sn)?.disabled)throw new Error('This surah is unavailable for the selected reciter.');
        if(browseMode!=='surah'||currentSurah!==sn||!VERSES.some(v=>v.surah===sn))await loadSurah(sn,{keepPlaying:false});
        if(loadStatusEl.classList.contains('error'))throw new Error(loadStatusEl.textContent);
        const idx=VERSES.findIndex(v=>v.surah===sn&&v.ayah===(an||1));
        if(idx<0)throw new Error('Verse is not available in the current alignment.');
        seekVerseStart(idx,false);
        saveResumeState();
      }
      if(innerWidth<900)readerSidebar(false);
    }catch(e){readerUI('readerNotice').textContent=e.message||String(e);}
    finally{readerBusy=false;readerLastLocation='';readerSync(currentVerseIdx);readerNav();}
  }
  readerUI('readerNavToggle').onclick=()=>readerSidebar(readerUI('readerSidebar').hidden);
  readerUI('readerShade').onclick=()=>readerSidebar(false);
  readerUI('readerSurahs').onclick=()=>readerSetTab('surah');
  readerUI('readerJuz').onclick=()=>readerSetTab('juz');
  readerUI('readerSaved').onclick=()=>readerSetTab('saved');
  readerUI('readerSearch').oninput=readerNav;
  readerUI('readerGo').onclick=()=>{const ayah=Number(readerUI('readerAyah').value);if(Number.isInteger(ayah)&&ayah>=1&&ayah<=Number(readerUI('readerAyah').max))readerNavigate(currentSurah+':'+ayah,'saved');else readerUI('readerNotice').textContent='Enter a valid verse number.';};
  readerUI('readerAyah').onkeydown=e=>{if(e.key==='Enter')readerUI('readerGo').click();};
  readerUI('readerBookmark').onclick=()=>{
    const v=VERSES[currentVerseIdx];if(!v)return;
    const key=v.surah+':'+v.ayah;
    readerBookmarks=readerBookmarks.includes(key)?readerBookmarks.filter(k=>k!==key):[...readerBookmarks,key];
    try{localStorage.setItem('qusx-reader-bookmarks',JSON.stringify(readerBookmarks));}catch(_){}
    readerLastLocation='';readerSync(currentVerseIdx);
  };
  readerUI('readerShare').onclick=async()=>{
    const v=VERSES[currentVerseIdx];if(!v)return;
    const url=new URL(location.href);url.hash=v.surah+':'+v.ayah;
    try{await navigator.clipboard.writeText(url.href);readerUI('readerNotice').textContent='Verse link copied.';}
    catch(_){history.replaceState(null,'',url);readerUI('readerNotice').textContent='Verse link is in the address bar.';}
  };
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&innerWidth<900)readerSidebar(false);});
  const readerMedia=matchMedia('(min-width:900px)');
  readerMedia.addEventListener('change',e=>readerSidebar(e.matches));
  readerSidebar(readerMedia.matches);readerNav();
  // Existing native selectors remain available and govern reciter restrictions.
  const readerObserver=new MutationObserver(()=>readerNav());
  readerObserver.observe(surahSelect,{childList:true,subtree:true,attributes:true,attributeFilter:['disabled']});
  readerObserver.observe(juzSelect,{childList:true,subtree:true,attributes:true,attributeFilter:['disabled']});
  reciterSelect.addEventListener('change',()=>readerNav());


  // Separate translation renderer using QUSX's canonical text and timing.
  function readerEl(tag,cls,content){
    const e=document.createElement(tag);if(cls)e.className=cls;
    if(content!=null)e.textContent=content;return e;
  }
  function readerVerseKey(v){return v.surah+':'+v.ayah;}
  function readerIconButton(icon,label,handler){
    const b=readerEl('button','qv-action',icon);b.type='button';b.title=label;b.setAttribute('aria-label',label);b.onclick=handler;return b;
  }
  function readerSetSaved(v,btn){
    const key=readerVerseKey(v);
    readerBookmarks=readerBookmarks.includes(key)?readerBookmarks.filter(x=>x!==key):[...readerBookmarks,key];
    try{localStorage.setItem('qusx-reader-bookmarks',JSON.stringify(readerBookmarks));}catch(_){}
    readerRefreshVerseActions();readerLastLocation='';readerSync(currentVerseIdx);readerNav();
  }
  function readerRefreshVerseActions(){
    for(const b of document.querySelectorAll('.qv-save')){
      const saved=readerBookmarks.includes(b.dataset.key);b.textContent=saved?'★':'☆';
      b.setAttribute('aria-pressed',String(saved));
    }
  }
  async function readerCopyVerse(v,btn){
    const url=new URL(location.href);url.hash=readerVerseKey(v);
    try{await navigator.clipboard.writeText(url.href);btn.title='Copied';readerUI('readerNotice').textContent='Verse link copied.';}
    catch(_){history.replaceState(null,'',url);readerUI('readerNotice').textContent='Verse link is in the address bar.';}
  }
  const readerTranslations=new Map();
  function readerGetTranslation(sn){
    if(readerTranslations.has(sn))return readerTranslations.get(sn);
    const task=fetch('https://api.alquran.cloud/v1/surah/'+sn+'/en.pickthall')
      .then(r=>{if(!r.ok)throw Error('Translation unavailable');return r.json();})
      .then(j=>{
        if(j.data?.number!==sn||!Array.isArray(j.data.ayahs)||j.data.edition?.identifier!=='en.pickthall')throw Error('Unexpected translation response');
        return new Map(j.data.ayahs.filter(a=>Number.isInteger(a.numberInSurah)&&typeof a.text==='string').map(a=>[a.numberInSurah,a.text]));
      }).catch(e=>{readerTranslations.delete(sn);throw e;});
    readerTranslations.set(sn,task);return task;
  }
  function readerFillTranslation(v,el,credit){
    el.textContent='Loading translation…';credit.textContent='';
    readerGetTranslation(v.surah).then(map=>{
      if(!el.isConnected)return;
      if(!map.has(v.ayah))throw Error('Verse translation unavailable');
      el.textContent=map.get(v.ayah);credit.textContent='— Marmaduke Pickthall · Al Quran Cloud';
    }).catch(()=>{
      if(!el.isConnected)return;el.textContent='Translation unavailable. ';
      const b=readerEl('button','qv-retry','Retry');b.type='button';
      b.onclick=()=>readerFillTranslation(v,el,credit);el.append(b);
    });
  }
  const readerGlossPromises=new Map();
  function readerGetGloss(lang,sn){
    const key=lang+':'+sn;
    if(!readerGlossPromises.has(key)){
      const p=fetchGlossIndex(lang,sn).then(idx=>{if(!idx)readerGlossPromises.delete(key);return idx;});
      readerGlossPromises.set(key,p);
    }
    return readerGlossPromises.get(key);
  }
  let readerPlayingGloss=null;
  function readerStopGloss(){
    glossAudio.pause();
    if(readerPlayingGloss)readerPlayingGloss.setAttribute('aria-pressed','false');
    readerPlayingGloss=null;
  }
  function readerGlossWord(v,wIdx,span){
    const wrap=readerEl('span','qv-gloss');wrap.append(span);
    const b=readerEl('button','','…');b.type='button';b.disabled=true;b.setAttribute('aria-pressed','false');wrap.append(b);
    const id=String(morphFor(v,wIdx)?.id||'');
    const lang=readerGlossLanguage;
    if(!id){b.textContent='—';return wrap;}
    readerGetGloss(lang,v.surah).then(idx=>{
      if(!b.isConnected)return;
      const clip=idx?.words?.[id];
      const owner=idx?.merged?.[id];
      if(!clip||!idx.text?.[clip]){b.textContent='—';return;}
      b.textContent=owner?'←':idx.text[clip];
      b.title=owner?'Meaning shown with adjacent word':'Play synthesised meaning (not recitation)';
      b.disabled=false;
      b.onclick=e=>{
        e.stopPropagation();
        const same=readerPlayingGloss===b;readerStopGloss();if(same)return;
        audio.pause();readerPlayingGloss=b;b.setAttribute('aria-pressed','true');
        glossAudio.src=GLOSS_BASE[lang]+'audio/'+clip+'.opus';
        glossAudio.play().catch(()=>readerStopGloss());
      };
    });
    return wrap;
  }

  // Mobile shaping: DOM boundaries between Arabic letters can break joining.
  // Preserve one intact text node per canonical word and keep timing metadata
  // outside that node. Range highlights do not introduce shaping boundaries.
  function readerBuildShapedWord(v,wIdx,verseIdx){
    const text=visualWordText(v,wIdx,(v.qusxWords||[])[wIdx-1]||'');
    let word=v.letters?.word_idx?buildTimedWordSpan(v,wIdx,verseIdx):null;
    if(!word){
      word=readerEl('span','word');
      word.dataset.word=wIdx;word.dataset.surah=v.surah;word.dataset.ayah=v.ayah;
      const timing=(v.words||[]).find(row=>row[0]===wIdx);
      if(timing){
        const start=v.source_offset_ms+timing[1];
        word.dataset.startMs=start;
        word.addEventListener('click',e=>{e.stopPropagation();handleWordTap(v,wIdx,verseIdx,start);});
      }
      bindGrammarHandlers(word,morphFor(v,wIdx),v,wIdx);
    }
    let offset=0;
    const ranges=[];
    const letters=[...word.querySelectorAll('.letter:not(.mark-only)')];
    // Build offsets against the exact displayed source. If an old letter
    // renderer has hidden an orthographic mark, decline the range rather than
    // modify Quran text or highlight an incorrect character.
    if(letters.length&&letters.map(el=>el.textContent).join('')===text){
      for(const el of letters){
        const length=el.textContent.length;
        if(length)ranges.push({from:offset,to:offset+length,start:Number(el.dataset.start),gidx:Number(el.dataset.gidx)});
        offset+=length;
      }
    }
    word.textContent=text;
    word.lang='ar';word.dir='rtl';
    if(ranges.length)readerLetterRanges.set(word,ranges);
    return word;
  }
  function readerClearLetterRange(){
    if(typeof CSS!=='undefined'&&CSS.highlights)CSS.highlights.delete('qusx-timed-letter');
  }
  function readerPaintLetterRange(word,entry){
    if(!entry||!word?.firstChild||typeof Highlight!=='function'||typeof CSS==='undefined'||!CSS.highlights)return;
    const node=word.firstChild;
    if(node.nodeType!==3||entry.to>node.length)return;
    const range=document.createRange();
    range.setStart(node,entry.from);range.setEnd(node,entry.to);
    CSS.highlights.set('qusx-timed-letter',new Highlight(range));
  }
  function readerHighlightCurrentLetter(v,activeWord,ms){
    readerClearLetterRange();
    if(mode!=='letter'||activeWord==null)return;
    const word=mushafPagesEl.querySelector('.word'+verseDomScope(v)+'[data-word="'+activeWord+'"]');
    if(!word)return;
    const ranges=readerLetterRanges.get(word)||[];
    let match=null;
    for(const entry of ranges){if(ms>=entry.start)match=entry;else break;}
    readerPaintLetterRange(word,match);
  }

  function renderVerseReader(){
    readerStopGloss();readerClearLetterRange();mushafPagesEl.replaceChildren();mushafPagesEl.classList.remove('page-mode');mushafPageCount=0;
    if(pageNavEl)pageNavEl.classList.remove('visible');
    flatLetters=[];hydrateSimpleTextForVisibleVerses();
    const frag=document.createDocumentFragment();
    for(const [i,v] of VERSES.entries()){
      if(v.ayah===1&&v.surah!==1&&v.surah!==9){
        const b=readerEl('div','bismillah','بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ');b.lang='ar';b.dir='rtl';frag.append(b);
      }
      const row=readerEl('article','qv');row.dataset.verseKey=readerVerseKey(v);
      const actions=readerEl('div','qv-actions');actions.append(readerEl('span','qv-ref',readerVerseKey(v)));
      const play=readerIconButton('▶','Play verse '+readerVerseKey(v),()=>{
        if(readerLoading)return;
        cancelTapWordStop();readerStopGloss();
        if(currentVerseIdx===i&&!audio.paused){audio.pause();return;}
        seekVerseStart(i,true);
      });
      play.classList.add('qv-play');play.dataset.idx=i;actions.append(play);
      const save=readerIconButton('☆','Save verse '+readerVerseKey(v),()=>readerSetSaved(v,save));
      save.classList.add('qv-save');save.dataset.key=readerVerseKey(v);actions.append(save);
      actions.append(readerIconButton('↗','Copy verse link '+readerVerseKey(v),e=>readerCopyVerse(v,e.currentTarget)));
      if(v.sajda)actions.append(readerEl('small','', '۩ Sajda'));
      const content=readerEl('div','qv-content');
      const ar=readerEl('div','qv-arabic verse-text');ar.lang='ar';ar.dir='rtl';
      for(let wi=1;wi<=(v.qusxWords||[]).length;wi++){
        const word=readerBuildShapedWord(v,wi,i);
        ar.append(readerGlossEnabled?readerGlossWord(v,wi,word):word,document.createTextNode(' '));
      }
      if(!(v.qusxWords||[]).length)ar.append(document.createTextNode(v.text||''));
      ar.append(readerEl('span','ayah-pin',toArabicDigits(v.ayah)));
      const tr=readerEl('p','qv-translation','Loading translation…');tr.lang='en';tr.dir='ltr';
      const credit=readerEl('small','qv-credit');
      content.append(ar,tr,credit);row.append(actions,content);frag.append(row);
      readerFillTranslation(v,tr,credit);
    }
    mushafPagesEl.append(frag);readerRefreshVerseActions();readerUpdatePlayButtons();
  }
  function readerUpdatePlayButtons(){
    for(const b of document.querySelectorAll('.qv-play')){
      const playing=Number(b.dataset.idx)===currentVerseIdx&&!audio.paused;b.textContent=playing?'Ⅱ':'▶';
      b.setAttribute('aria-pressed',String(playing));
    }
  }
  function readerSwitchPresentation(value){
    readerPresentation=value==='reading'?'reading':'translation';
    try{localStorage.setItem('qusx-presentation-v2',readerPresentation);}catch(_){}
    document.body.classList.toggle('reader-translation',readerPresentation==='translation');
    readerUI('readerTranslationMode').setAttribute('aria-pressed',String(readerPresentation==='translation'));
    readerUI('readerReadingMode').setAttribute('aria-pressed',String(readerPresentation==='reading'));
    readerUI('readerGlossToggle').hidden=readerPresentation!=='translation';
    readerUI('readerGlossLanguage').hidden=readerPresentation!=='translation'||!readerGlossEnabled;
    renderMushafPages();updateHighlight();
    if(VERSES[currentVerseIdx])scrollToPlayback(currentVerseIdx,true);
  }
  readerUI('readerTranslationMode').onclick=()=>readerSwitchPresentation('translation');
  readerUI('readerReadingMode').onclick=()=>readerSwitchPresentation('reading');
  readerUI('readerQuickSettings').onclick=()=>readerUI('chromeMoreBtn').click();
  readerUI('readerGlossToggle').onclick=()=>{
    readerGlossEnabled=!readerGlossEnabled;readerUI('readerGlossToggle').setAttribute('aria-pressed',String(readerGlossEnabled));
    readerUI('readerGlossLanguage').hidden=!readerGlossEnabled;renderMushafPages();updateHighlight();
  };
  readerUI('readerGlossLanguage').value=readerGlossLanguage;
  readerUI('readerGlossLanguage').onchange=()=>{
    readerGlossLanguage=readerUI('readerGlossLanguage').value;renderMushafPages();updateHighlight();
  };
  audio.addEventListener('play',()=>{readerStopGloss();readerUpdatePlayButtons();});
  audio.addEventListener('pause',readerUpdatePlayButtons);
  glossAudio.addEventListener('ended',readerStopGloss);
  glossAudio.addEventListener('error',readerStopGloss);
  document.body.classList.toggle('reader-translation',readerPresentation==='translation');
  readerUI('readerTranslationMode').setAttribute('aria-pressed',String(readerPresentation==='translation'));
  readerUI('readerReadingMode').setAttribute('aria-pressed',String(readerPresentation==='reading'));
  readerUI('readerGlossToggle').hidden=readerPresentation!=='translation';

// Refit when webfonts finish and when either fixed toolbar changes height.
syncReaderChromeInsets();
if(document.fonts){
  document.fonts.ready.then(markShortMushafLines);
  document.fonts.addEventListener?.('loadingdone',markShortMushafLines);
}
if(typeof ResizeObserver==='function'){
  const chromeObserver=new ResizeObserver(syncReaderChromeInsets);
  for(const el of [document.getElementById('readerHeader'),document.getElementById('readerModeBar'),controlsEl])if(el)chromeObserver.observe(el);
  let lastReaderWidth=0;
  const fitObserver=new ResizeObserver(entries=>{
    const width=entries[0]?.contentRect.width||0;
    if(width!==lastReaderWidth){lastReaderWidth=width;requestAnimationFrame(markShortMushafLines);}
  });
  fitObserver.observe(mushafPagesEl);
}
// init — probe optional Al-Hadr pack, resume last read when possible
(async () => {
  const bootHint = document.getElementById('bootHint');
  try {
    const saved = readResumeState();
    if (saved && saved.reciter && RECITERS.some(r => r[0] === saved.reciter)) {
      RECITER_CONFIG = saved.reciter;
      if (reciterSelect) reciterSelect.value = RECITER_CONFIG;
      refreshReciterInfo();
    }
    await probeLocalAlhadr();
    applyLocalAlhadrAvailability();
    if (LOCAL_ALHADR_AVAILABLE && isLocalReciter()) {
      refreshSurahAvailability();
      refreshJuzSelect();
    } else {
      refreshSurahAvailability();
    }
    if (saved && saved.layout && LAYOUTS.some(([k]) => k === saved.layout)) {
      currentLayout = saved.layout;
      if (layoutSelect) layoutSelect.value = currentLayout;
    }
    const requested = location.hash.slice(1).split(':').map(Number);
    const requestedMeta = SURAH_INDEX.find(s=>s.num===requested[0]);
    if (requested.length===2 && requestedMeta && Number.isInteger(requested[1]) && requested[1]>=1 && requested[1]<=requestedMeta.ayahCount) {
      await readerNavigate(requested.join(':'),'saved');
    } else if (saved && saved.surah) {
      const resumeOpts = {
        continuePlayback: true,
        keepPlaying: false,
        resumeAt: Number(saved.time) || 0,
        resumeSurah: saved.surah,
        resumeAyah: saved.ayah || 1,
      };
      const wantJuz = saved.browseMode === 'juz' && saved.juz != null && isLocalReciter() && LOCAL_ALHADR_AVAILABLE;
      if (wantJuz) await loadJuz(+saved.juz, resumeOpts);
      else await loadSurah(+saved.surah, resumeOpts);
      if (loadStatusEl && !loadStatusEl.classList.contains('error')) {
        loadStatusEl.textContent = 'Resumed ' + saved.surah + ':' + (saved.ayah || 1);
      }
    } else {
      await loadSurah(1);
    }
  } catch (err) {
    if (loadStatusEl) {
      loadStatusEl.textContent = err.message || String(err);
      loadStatusEl.classList.add('error');
    }
    if (bootHint) bootHint.textContent = 'Failed to load — ' + (err.message || err);
  } finally {
    if (bootHint) bootHint.classList.add('done');
    readerLastLocation='';readerSync(currentVerseIdx);readerNav();
  }
})();
</script>
</body>
</html>
"""

html = html.replace('__SURAH_INDEX_JSON__', surah_index_json)
html = html.replace('__GLYPH_V2_JSON__', glyph_v2_json)
html = html.replace('__GLYPH_V1_JSON__', glyph_v1_json)
html = html.replace('__RECITERS_JSON__', reciters_json)
html = html.replace('__TRADITION_DIFFS_JSON__', tradition_diffs_json)
with open(os.path.join(_DIR, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(html)
print('written', len(html), 'bytes')
