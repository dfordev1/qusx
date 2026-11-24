"""Independently align actual Al-Hadr MP3 around 2:77–84; never auto-publish."""
import json, pathlib, subprocess, statistics
out=pathlib.Path("independent-alignment");out.mkdir(exist_ok=True)
manifest=json.loads(pathlib.Path("local_alhadr/manifest.json").read_text())
rows=[r for r in manifest["surahs"]["2"]["ayahs"] if 77<=int(r["ayah"])<=84]
assert len(rows)==8 and all(int(r["juz"])==1 for r in rows)
origin=max(0,int(rows[0]["source_offset_ms"])-3000)
end=int(rows[-1]["source_offset_ms"]+rows[-1]["duration_ms"])+3000
source=out/"source.mp3"; clip=out/"passage.wav"
subprocess.run(["curl","-fL","--retry","2","--max-time","180","https://archive.org/download/quran-al-hadr-recitation/juz/juz-01.mp3","-o",str(source)],check=True)
subprocess.run(["ffmpeg","-v","error","-i",str(source),"-ss",str(origin/1000),"-t",str((end-origin)/1000),"-ac","1","-ar","16000","-y",str(clip)],check=True)
source.unlink()
windows=[{"ayah":r["ayah"],"start_ms":r["source_offset_ms"]-origin,"end_ms":r["source_offset_ms"]+r["duration_ms"]-origin} for r in rows]
windowfile=out/"windows.json";windowfile.write_text(json.dumps(windows))
subprocess.run(["quran-word-align","file",str(clip),"2","--from-ayah","77","--timings",str(windowfile),"--margin","2","--format","json,csv","--out",str(out)],check=True)
candidate=json.loads((out/"002.json").read_text())
report=[]
for r in rows:
    old={int(i):(s,e) for i,s,e in r["word_timestamps"]}
    words=candidate.get(str(r["ayah"]),[])
    shifts=[]
    for i,s,e,confidence in words:
        if i in old: shifts.append({"word":i,"manifest_ms":r["source_offset_ms"]+old[i][0],"candidate_ms":origin+s,"delta_ms":origin+s-r["source_offset_ms"]-old[i][0],"confidence":confidence})
    report.append({"ayah":r["ayah"],"manifest_text":r["text"],"expected_words":len(old),"candidate_words":len(words),"median_onset_delta_ms":statistics.median(x["delta_ms"] for x in shifts) if shifts else None,"candidates":shifts})
result={"warning":"Candidate comparison by index only; check CSV token identity and listen before applying any correction. Model agreement is not human verification.","clip_origin_ms":origin,"ayahs":report}
(out/"comparison.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False))
