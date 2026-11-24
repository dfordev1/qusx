"""Compare decoded MP3/Opus clocks and export actual manifest word clips."""
import array, json, math, subprocess, pathlib, sys, urllib.request
out=pathlib.Path("word-audio-audit");out.mkdir(exist_ok=True)
base="https://archive.org/download/quran-al-hadr-recitation/juz/juz-01."
m=json.loads(pathlib.Path("local_alhadr/manifest.json").read_text())
r=next(x for x in m["surahs"]["2"]["ayahs"] if int(x["ayah"])==80)
start=float(r["source_offset_ms"])/1000
def cmd(*args):
    subprocess.run(args,check=True)
for ext in ("mp3","ogg"):
    p=out/("source."+ext)
    cmd("curl","-fL","--retry","2","--max-time","180",base+ext,"-o",str(p))
    cmd("ffmpeg","-v","error","-i",str(p),"-ss",str(start-3),"-t","17","-ac","1","-ar","8000","-f","s16le","-y",str(out/(ext+".pcm")))
    cmd("ffmpeg","-v","error","-i",str(p),"-ss",str(start),"-t",str(float(r["duration_ms"])/1000),"-c:a","libmp3lame","-y",str(out/("2-80-"+ext+".mp3")))
    if ext=="mp3":
        for n,s,e in r["word_timestamps"]:
            if e<=s: continue
            cmd("ffmpeg","-v","error","-i",str(p),"-ss",str(start+s/1000),"-t",str((e-s)/1000),"-c:a","libmp3lame","-y",str(out/("2-80-word-%02d.mp3"%n)))
    p.unlink()
def read(ext):
    a=array.array("h");a.frombytes((out/(ext+".pcm")).read_bytes())
    if sys.byteorder!="little": a.byteswap()
    return a
a,b=read("mp3"),read("ogg")
# Compare waveform in the middle of both 17-second excerpts. Coarse search
# at 2 ms resolution, then refine sample-by-sample near the best candidate.
def corr(lag,stride):
    x=a[24000:104000:stride];y=b[24000+lag:104000+lag:stride]
    dot=sum(i*j for i,j in zip(x,y))
    norm=math.sqrt(sum(i*i for i in x)*sum(j*j for j in y))
    return dot/norm if norm else 0
best=max(range(-16000,16001,16),key=lambda l:corr(l,32))
best=max(range(best-16,best+17),key=lambda l:corr(l,8))
report={"ayah":"2:80","opus_relative_to_mp3_ms":best/8,"waveform_correlation":corr(best,8),"manifest_word_timestamps":r["word_timestamps"],"manifest_text":r.get("text_uthmani",r["text"]),"note":"Waveform correlation compares formats only; listening to the word clips is required to validate spoken word identity."}
(out/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
for ext in ("mp3","ogg"): (out/(ext+".pcm")).unlink()
