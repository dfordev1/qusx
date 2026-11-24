#!/usr/bin/env python3
"""Download the actual Al-Hadr recordings, verify their identity and probe duration.

A duration match is necessary, not sufficient, for word/ayah synchronization.
Never rewrite timing offsets or scale timestamps from this report.
"""
import argparse
import hashlib
import json
import math
import pathlib
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "local_alhadr" / "manifest.json"

def inspect(job):
    juz, expected, last_end, url = job
    result = {"juz": juz, "expected_seconds": expected,
              "last_ayah_end_seconds": last_end, "url": url}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            file = pathlib.Path(tmp) / urllib.parse.urlsplit(url).path.split("/")[-1]
            digest = hashlib.sha256()
            size = 0
            req = urllib.request.Request(url, headers={"User-Agent": "QUSX-audio-audit/1.0"})
            with urllib.request.urlopen(req, timeout=45) as response, file.open("wb") as out:
                result["final_url"] = response.geturl()
                while True:
                    data = response.read(1024 * 1024)
                    if not data:
                        break
                    size += len(data)
                    if size > 150 * 1024 * 1024:
                        raise ValueError("Recording exceeds 150 MB safety limit")
                    digest.update(data)
                    out.write(data)
            result.update(bytes=size, sha256=digest.hexdigest())
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_format", "-show_streams",
                 "-of", "json", str(file)], capture_output=True, text=True,
                check=True, timeout=45)
            metadata = json.loads(probe.stdout)
            stream = next(s for s in metadata["streams"] if s.get("codec_type") == "audio")
            duration = float(metadata["format"]["duration"])
            if not math.isfinite(duration) or duration <= 0:
                raise ValueError("Invalid probed duration")
            delta = duration - expected
            result.update(actual_seconds=duration, delta_seconds=round(delta, 6),
                          codec=stream.get("codec_name"),
                          stream_duration_seconds=stream.get("duration"),
                          stream_start_time=stream.get("start_time"),
                          duration_matches=abs(delta) <= max(2, expected * .005),
                          tight_duration_match=abs(delta) <= .1,
                          contains_final_ayah=duration >= last_end)
            result["status"] = ("duration_match" if result["duration_matches"]
                                and result["contains_final_ayah"] else "duration_mismatch")
    except urllib.error.HTTPError as exc:
        result.update(status="not_found" if exc.code == 404 else "http_error",
                      error=str(exc), http_status=exc.code)
    except Exception as exc:
        result.update(status="probe_error", error=str(exc))
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--juz", nargs="+", type=int, choices=range(1, 31))
    parser.add_argument("--output", default="alhadr-audit.json")
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    base = manifest["audioBase"].rstrip("/")
    if base != "https://archive.org/download/quran-al-hadr-recitation/juz":
        raise ValueError("Unexpected recording base; review before auditing")
    tracks = {int(t["juz"]): t for t in manifest["tracks"]}
    selected = sorted(set(args.juz or tracks))
    ends = {}
    for surah in manifest["surahs"].values():
        for a in surah["ayahs"]:
            j = int(a["juz"])
            ends[j] = max(ends.get(j, 0), (float(a["source_offset_ms"]) +
                                         float(a["duration_ms"])) / 1000)
    jobs = []
    for j in selected:
        if j not in tracks:
            continue
        expected = float(tracks[j]["durationSeconds"])
        stem = pathlib.PurePosixPath(tracks[j]["audio"]).stem
        if stem != f"juz-{j:02d}":
            raise ValueError(f"Unexpected filename for juz {j}: {stem}")
        for extension in ("ogg", "opus", "mp3"):
            jobs.append((j, expected, ends[j], f"{base}/{stem}.{extension}"))
    rows = []
    with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 4))) as pool:
        for result in pool.map(inspect, jobs):
            rows.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
    unmatched = [j for j in selected if not any(
        r["juz"] == j and r["status"] == "duration_match" for r in rows)]
    report = {"manifest_sha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
              "missing_manifest_juz": sorted(set(range(1, 31)) - set(tracks)),
              "selected_juz": selected, "no_duration_matching_recording": unmatched,
              "results": rows, "warning": "Duration agreement does not prove internal audio/text alignment."}
    pathlib.Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Missing manifest juz:", report["missing_manifest_juz"])
    print("No duration-matching recording:", unmatched)
    return 1 if unmatched else 0

if __name__ == "__main__":
    raise SystemExit(main())
