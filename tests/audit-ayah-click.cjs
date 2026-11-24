// Diagnose actual manifest near the reported 2:80 / 12:43 click.
const fs=require('node:fs');
const assert=require('node:assert/strict');
const m=JSON.parse(fs.readFileSync('local_alhadr/manifest.json','utf8'));
const rows=m.surahs['2'].ayahs;
const byAyah=new Map(rows.map(r=>[Number(r.ayah),r]));
const ms=763000;
const span=r=>({ayah:r.ayah,juz:r.juz,audio:r.audio,offset:Number(r.source_offset_ms),end:Number(r.source_offset_ms)+Number(r.duration_ms),text:r.text_uthmani||r.text});
for(let n=77;n<=84;n++){
 const r=byAyah.get(n);
 if(!r){console.log(JSON.stringify({missing:n}));continue;}
 console.log(JSON.stringify({...span(r),word_timestamps:r.word_timestamps}));
}
console.log('At 12:43:',JSON.stringify(rows.filter(r=>Number(r.juz)===1&&ms>=Number(r.source_offset_ms)&&ms<Number(r.source_offset_ms)+Number(r.duration_ms)).map(span)));
const src=fs.readFileSync('build_app.py','utf8');
const chunks=[['function readerWordMapping(','function readerOnlineVerse('],['function normalizeArabicLocal(','// Canonical Uthmani alignments']];
const code=chunks.map(([x,y])=>src.slice(src.indexOf(x),src.indexOf(y,src.indexOf(x)))).join('\n');
const map=new Function(code+';return readerWordMapping;')();
const xml=fs.readFileSync(process.argv[2],'utf8');
const canon={};let n;
for(const hit of xml.matchAll(/<ayah\b[^>]*\bnumber="(\d+)"[^>]*>|<word\b([^>]*)>([^<]*)<\/word>/g)){
 if(hit[1]){n=Number(hit[1]);canon[n]??=[];}
 else if(n&&!/\btype="number"/.test(hit[2]))canon[n].push(hit[3]);
}
assert.equal(Object.keys(canon).length,286,'Expected complete canonical Al-Baqarah XML');
const matches=(n,r)=>!!(canon[n]?.length&&r&&map(canon[n],r.text_uthmani||r.text,n===1));
const mismatch=[],shifted=[];
for(let n=1;n<=286;n++){
 const r=byAyah.get(n);
 if(!r){mismatch.push({ayah:n,missing:true});continue;}
 if(!matches(n,r)){
  mismatch.push({ayah:n,text:span(r).text});
  if(matches(n-1,r)||matches(n+1,r))shifted.push({row:n,matchingAyah:matches(n-1,r)?n-1:n+1});
 }
}
const overlaps=[];
for(let n=1;n<286;n++){const r=byAyah.get(n),next=byAyah.get(n+1);if(r&&next&&r.audio===next.audio&&span(r).end>span(next).offset)overlaps.push({ayah:n,next:n+1,overlapMs:span(r).end-span(next).offset});}
console.log('Text mismatch count:',mismatch.length,'neighbor matches:',JSON.stringify(shifted),'overlaps:',JSON.stringify(overlaps));
console.log('Focused canonical text:',JSON.stringify(Object.fromEntries([79,80,81].map(n=>[n,canon[n].join(' ')]))));
