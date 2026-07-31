"""Build qpc_v1_glyphs.json from Quran.com API (code_v1), same shape as qpc_v2_glyphs.json.

Shape: { surah: { ayah: "<PUA chars one per word + trailing ayah-number glyph>" } }
"""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

OUT = Path(__file__).with_name("qpc_v1_glyphs.json")
UA = "qusx-followalong/1.0 (glyph fetch; +https://github.com/dfordev1/qusx)"


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def code_char(code: str | None) -> str | None:
    if not code:
        return None
    for ch in code:
        if not ch.isspace():
            return ch
    return None


def fetch_surah(surah: int) -> dict[str, str]:
    page = 1
    verses: list[dict] = []
    while True:
        url = (
            f"https://api.quran.com/api/v4/verses/by_chapter/{surah}"
            f"?words=true&word_fields=code_v1&per_page=50&page={page}"
        )
        data = get_json(url)
        verses.extend(data["verses"])
        total_pages = (data.get("pagination") or {}).get("total_pages", 1)
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.03)

    out: dict[str, str] = {}
    for v in verses:
        chars = []
        for w in v["words"]:
            ch = code_char(w.get("code_v1"))
            if ch:
                chars.append(ch)
        out[str(v["verse_number"])] = "".join(chars)
    return out


def main() -> None:
    result: dict[str, dict[str, str]] = {}
    for s in range(1, 115):
        result[str(s)] = fetch_surah(s)
        n = len(result[str(s)])
        print(f"surah {s:3d}: {n} ayahs", flush=True)
        time.sleep(0.05)

    # Sanity: Fatihah 1:1 should be 5 PUA glyphs (4 words + end mark)
    f1 = result["1"]["1"]
    assert len(f1) == 5, f"expected 5 glyphs for 1:1, got {len(f1)}"
    assert 0xFB50 <= ord(f1[0]) <= 0xFDFF, hex(ord(f1[0]))

    OUT.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
