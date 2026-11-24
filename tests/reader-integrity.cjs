// Run: node tests/reader-integrity.cjs
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const chunks=[["function readerWordMapping(","function readerOnlineVerse("],["function normalizeArabicLocal(","// Canonical Uthmani alignments"],["function repairWordTimestamps(","function buildLocalVerse("],["function readerVerseAtTime(","function verseAtMs("]];
const tests="\nconst v={source_offset_ms:1000,duration_ms:500};\nconst cases=[\n['inside verse',readerPositionInVerse(v,1250),true],\n['before verse',readerPositionInVerse(v,999),false],\n['exclusive end',readerPositionInVerse(v,1500),false],\n['invalid offset',readerPositionInVerse({source_offset_ms:null,duration_ms:500},0),false],\n['near seek',readerConfirmedSeek(v,1100,1140),true],\n['stale seek 200ms',readerConfirmedSeek(v,1100,1300),false],\n['seek across boundary',readerConfirmedSeek(v,1490,1501),false],\n['seek just before ayah',readerConfirmedSeek(v,1000,999),false],\n['complete basmalah',readerCompleteBasmalah([[1,0,100,'بسم'],[2,100,200,'الله'],[3,200,300,'الرحمن'],[4,300,400,'الرحيم']]),true],\n['partial basmalah',readerCompleteBasmalah([[1,0,100,'بسم']]),false],\n['wrong basmalah text',readerCompleteBasmalah([[1,0,100,'بسم'],[2,100,200,'الله'],[3,200,300,'الرحمن'],[4,300,400,'الله']]),false],\n['missing local ayah preserved',readerLocalRows([{surah:2,ayah:2,audio:'x'}],2,3).map(r=>r.ayah).join(','),'1,2,3'],\n['duplicate local audio rejected',readerLocalRows([{surah:2,ayah:1,audio:'a'},{surah:2,ayah:1,audio:'b'}],2,1)[0].audio,undefined],\n['wrong surah audio rejected',readerLocalRows([{surah:3,ayah:1,audio:'a'}],2,1)[0].audio,undefined],\n['canonical text retained',readerCanonicalMeta({1:{words:['بسم']}},1,1).words[0],'بسم']\n];\nlet threw=false;try{readerCanonicalMeta({},1,1)}catch(e){threw=true}cases.push(['missing canonical text fails safely',threw,true]);\nreturn cases.map(([name,actual,expected])=>({name,actual,expected,pass:actual===expected}));";
for(const filename of ['build_app.py','index.html']){
  const f=fs.readFileSync(path.join(__dirname,'..',filename),'utf8');
  const code=chunks.map(([x,y])=>{const a=f.indexOf(x),b=f.indexOf(y,a+x.length);assert.ok(a>=0&&b>a);return f.slice(a,b)}).join('\n');
  const results=new Function(code+tests)();
  for(const r of results)assert.equal(r.actual,r.expected,filename+': '+r.name);
  console.log(filename+': '+results.length+' integrity checks passed');
}
