// Audit the shipped timing data, without treating metadata as acoustic ground truth.
const fs=require('node:fs');
const path=require('node:path');
const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'../local_alhadr/manifest.json'),'utf8'));
const rows=Object.values(manifest.surahs).flatMap(s=>s.ayahs);
let words=0,short=0,zero=0;const affected=[];
for(const row of rows){
  const invalid=[];
  for(const [id,start,end] of row.word_timestamps||[]){
    words++;
    if(end-start<=80)short++;
    if(end<=start){zero++;invalid.push(id);}
  }
  if(invalid.length)affected.push({surah:row.surah,ayah:row.ayah,wordIds:invalid});
}
console.log(JSON.stringify({ayahs:rows.length,words,wordsAtMost80ms:short,nonpositiveWordIntervals:zero,affectedAyahs:affected.length,sourceNote:manifest.note,affected},null,2));
