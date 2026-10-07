#!/usr/bin/env python3
"""Generate the searchable prepositional-verbs reference and practice game."""

import json
import sys
from collections import Counter
from html import escape
from pathlib import Path


GEN = Path(__file__).parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else GEN
entries = json.loads((GEN / "praepositionsverben.json").read_text(encoding="utf-8"))

PREP_ORDER = ["an", "bei", "mit", "auf", "vor", "aus", "in", "von",
              "über", "unter", "zu", "für", "gegen", "um"]
counts = Counter(entry["preposition"] for entry in entries)
filter_options = "\n".join(
    f'<option value="{escape(prep)}">{escape(prep)} ({counts[prep]})</option>'
    for prep in PREP_ORDER if counts[prep]
)
prep_answers = list(dict.fromkeys(entry["prep"] for entry in entries))
payload = json.dumps(entries, ensure_ascii=False, separators=(",", ":"))

# The nine translation languages use the same shared "dg-lang" localStorage
# key as woerterbuch.html and the lesson vocab tables. This page additionally
# offers German learner definitions. Other pages safely ignore that page-only
# "de" choice and retain their own default. Missing translations fall back to
# English until the remaining languages are filled (see PROMPTS.md).
LANGS = [
    ("de", "Deutsch (Deutsch–Deutsch)", 0),
    ("en", "English", 0),
    ("tr", "Türkçe", 0),
    ("sq", "Shqip", 0),
    ("uk", "Українська", 0),
    ("ar", "العربية", 1),
    ("fa", "فارسی", 1),
    ("es", "Español", 0),
    ("fr", "Français", 0),
    ("it", "Italiano", 0),
]
lang_options = "\n".join(
    f'<option value="{code}"{" selected" if code == "en" else ""}>{native}</option>'
    for code, native, _ in LANGS
)
rtl_langs = json.dumps([code for code, _, rtl in LANGS if rtl])

template = r'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Verben mit Präpositionen — Deutsch täglich</title>
<style>
  :root{color-scheme:light;
    --page-bg:#fff;--card-bg:#edf5f8;--card-strong:#dcecf2;
    --blue:#315d70;--blue-soft:#6e95a5;--heading:#1c1c1c;
    --body:#2c2c2a;--muted:#77736b;--border:#d7e5ea;
    --cream:#f6f2e9;--good:#3f6b3f;--good-bg:#e6f0e1;
    --bad:#8b3e32;--bad-bg:#f6e7e3;}
  *{box-sizing:border-box;}
  html{font-size:14px;}
  body{font-family:"Segoe UI",Helvetica,Arial,sans-serif;background:var(--page-bg);
    color:var(--body);margin:0;padding:26px 24px 80px;}
  button,input,select{font:inherit;}
  .wrap{max-width:980px;margin:0 auto;}
  .back{font-size:.85rem;margin:0 0 16px;display:flex;gap:8px;align-items:center;}
  .back a{color:#8c8778;text-decoration:none;}
  .back span{color:#cfc8b4;}
  .meta-row{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:18px;}
  .badge{display:inline-block;padding:8px 16px;border-radius:999px;
    font-size:.85rem;font-weight:600;background:var(--card-strong);color:var(--blue);}
  h1{font-size:1.65rem;line-height:1.25;color:var(--heading);margin:0 0 8px;}
  .intro{font-size:.98rem;line-height:1.7;color:#55514a;margin:0 0 20px;max-width:790px;}

  .mode-tabs{display:flex;gap:8px;margin:0 0 18px;}
  .mode-tabs button,.primary,.next-game{border:1px solid var(--border);border-radius:999px;
    padding:10px 17px;background:#fff;color:var(--blue);font-weight:700;cursor:pointer;}
  .mode-tabs button.active,.primary,.next-game{background:var(--blue);border-color:var(--blue);color:#fff;}
  .mode-tabs button:focus-visible,.primary:focus-visible,.next-game:focus-visible,
  .answer:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #b9d8e4;outline-offset:2px;}
  .view{display:none;}.view.active{display:block;}

  .controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:7px;}
  .controls input,.controls select{background:#fff;border:1px solid var(--border);
    color:var(--body);border-radius:999px;padding:10px 16px;outline:none;}
  .controls input{flex:1 1 280px;min-width:0;}
  .controls select{cursor:pointer;font-weight:600;}
  .count{font-size:.8rem;color:var(--muted);margin:0 0 18px;}
  .group{margin:0 0 28px;}
  .group-head{display:flex;align-items:baseline;gap:9px;margin:0 0 10px;padding:0 4px;}
  .group-head h2{font-size:1.2rem;color:var(--blue);margin:0;}
  .group-head span{font-size:.78rem;color:var(--muted);}
  .verb-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;}
  .verb-card{background:var(--card-bg);border:1px solid var(--border);border-radius:18px;
    padding:19px 20px;min-width:0;}
  .verb-top{display:flex;gap:10px;align-items:flex-start;justify-content:space-between;margin-bottom:12px;}
  .verb-name{font-size:1.12rem;font-weight:750;color:var(--heading);line-height:1.35;}
  .prep-pill{flex:0 0 auto;background:#fff;border:1px solid #c9dce3;color:var(--blue);
    border-radius:999px;padding:5px 9px;font-size:.75rem;font-weight:750;white-space:nowrap;}
  .meaning{font-size:.9rem;color:var(--blue);font-weight:650;margin:0 0 12px;}
  .meaning[dir="rtl"],.explanation[dir="rtl"],.question-meaning[dir="rtl"]{text-align:right;}
  .forms{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px;}
  .form{background:rgba(255,255,255,.64);border-radius:10px;padding:8px 10px;min-width:0;}
  .form small{display:block;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);
    font-size:.62rem;font-weight:700;margin-bottom:3px;}
  .form span{display:block;font-size:.84rem;overflow-wrap:anywhere;}
  details{border-top:1px solid #d5e4e9;padding-top:10px;}
  summary{color:var(--blue);font-size:.84rem;font-weight:700;cursor:pointer;}
  .explanation{font-size:.82rem;line-height:1.55;color:#5e5a53;margin:10px 0 7px;}
  .examples{padding-left:19px;margin:0;color:#55514a;font-size:.86rem;line-height:1.55;}
  .examples li{margin:0 0 6px;}.examples li:last-child{margin-bottom:0;}
  .empty{background:var(--card-bg);border-radius:18px;padding:30px;text-align:center;color:var(--muted);}

  .game-shell{background:var(--card-bg);border:1px solid var(--border);border-radius:22px;
    padding:26px 28px;max-width:720px;}
  .game-shell h2{font-size:1.3rem;margin:0 0 8px;color:var(--heading);}
  .game-shell p{line-height:1.65;color:#55514a;}
  .game-stats{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px;}
  .stat{background:#fff;border:1px solid var(--border);border-radius:999px;
    padding:7px 11px;color:var(--blue);font-size:.78rem;font-weight:700;}
  .question-label{text-transform:uppercase;letter-spacing:.1em;color:var(--blue-soft);
    font-size:.7rem;font-weight:800;margin:0 0 7px;}
  .question-verb{font-size:1.45rem;color:var(--heading);font-weight:800;margin:0 0 4px;}
  .question-meaning{color:var(--blue);font-weight:650;margin:0 0 18px;}
  .answers{display:grid;grid-template-columns:1fr 1fr;gap:9px;}
  .answer{border:1px solid var(--border);border-radius:13px;padding:12px 14px;background:#fff;
    color:var(--body);font-weight:700;cursor:pointer;text-align:left;}
  .answer:hover:not(:disabled){border-color:var(--blue-soft);}
  .answer.correct{background:var(--good-bg);border-color:#a9c5a4;color:var(--good);}
  .answer.wrong{background:var(--bad-bg);border-color:#d9aaa1;color:var(--bad);}
  .answer:disabled{cursor:default;}
  .feedback{margin-top:16px;border-top:1px solid var(--border);padding-top:15px;}
  .feedback strong.good{color:var(--good);}.feedback strong.bad{color:var(--bad);}
  .feedback .examples{margin:10px 0 14px;}
  .result-score{font-size:2.2rem;font-weight:800;color:var(--blue);margin:14px 0 2px;}
  .note{margin-top:24px;font-size:.8rem;color:#8b877f;font-style:italic;line-height:1.7;}

  @media(max-width:720px){
    body{padding:20px 12px 70px;}
    .verb-grid{grid-template-columns:1fr;}
    .game-shell{padding:22px 18px;border-radius:18px;}
    .answers{grid-template-columns:1fr;}
  }
</style>
</head>
<body>
<main class="wrap">
  <p class="back"><a href="index.html">&larr; Alle Lektionen</a><span>&middot;</span><a href="woerterbuch.html">Wörterbuch</a></p>
  <div class="meta-row"><span class="badge">__COUNT__ Verbindungen</span><span class="badge">__PREP_COUNT__ Präpositionen</span></div>
  <h1>Verben mit Präpositionen</h1>
  <p class="intro">Schlage feste Verbindungen nach, vergleiche Präteritum und Perfekt und öffne zu jedem Verb drei Beispiele. Im 10er-Spiel wählst du die passende Präposition und den richtigen Kasus.</p>

  <nav class="mode-tabs" aria-label="Bereich wählen">
    <button type="button" class="active" data-view="reference">Nachschlagen</button>
    <button type="button" data-view="game">10er-Spiel</button>
  </nav>

  <section id="reference" class="view active">
    <div class="controls">
      <input id="search" type="search" placeholder="Verb oder Bedeutung suchen …" autocomplete="off">
      <select id="prepFilter" aria-label="Nach Präposition filtern">
        <option value="">Alle Präpositionen</option>
__FILTER_OPTIONS__
      </select>
      <select id="langSelect" aria-label="Sprache der Bedeutung">
__LANG_OPTIONS__
      </select>
    </div>
    <p class="count" id="count"></p>
    <div id="groups"></div>
  </section>

  <section id="game" class="view">
    <div class="game-shell" id="gameBox"></div>
  </section>

  <p class="note">Grundlage: „Preposition mit Verben.xlsx“. Die Beispielsätze wurden auf genau drei pro Verbindung vereinheitlicht und teilweise sprachlich bereinigt. Bedeutung und Erklärung gibt es auf Deutsch und Englisch vollständig; weitere Sprachen werden ergänzt — ohne Übersetzung wird automatisch Englisch angezeigt.</p>
</main>

<script>
const DATA = __DATA__;
const PREP_ANSWERS = __PREP_ANSWERS__;
const PREP_ORDER = __PREP_ORDER__;
const RTL_LANGS = __RTL_LANGS__;
const BEST_KEY = "dg-prep-best";
const LANG_KEY = "dg-lang";
const groupsEl = document.getElementById("groups");
const searchEl = document.getElementById("search");
const prepFilterEl = document.getElementById("prepFilter");
const langSelectEl = document.getElementById("langSelect");
const countEl = document.getElementById("count");
const gameBox = document.getElementById("gameBox");

function esc(value){return String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c]);}
function shuffle(items){const a=[...items];for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function currentLang(){return langSelectEl.value||"en";}
// Translations are filled in gradually (see PROMPTS.md) — fall back to
// English for any entry that doesn't have the selected language yet.
function localized(entry,field){const lang=currentLang();return entry[field][lang]||entry[field].en;}
function rtlAttr(){return RTL_LANGS.includes(currentLang())?' dir="rtl"':"";}

try{const saved=localStorage.getItem(LANG_KEY);if(saved)langSelectEl.value=saved;}catch(e){}
document.querySelectorAll("[data-view]").forEach(button => button.addEventListener("click", () => {
  document.querySelectorAll("[data-view]").forEach(b => b.classList.toggle("active", b===button));
  document.querySelectorAll(".view").forEach(view => view.classList.toggle("active", view.id===button.dataset.view));
}));

function card(entry){
  return `<article class="verb-card">
    <div class="verb-top"><div class="verb-name">${esc(entry.verb)}</div><span class="prep-pill">${esc(entry.prep)}</span></div>
    <p class="meaning"${rtlAttr()}>${esc(localized(entry,"meaning"))}</p>
    <div class="forms"><div class="form"><small>Präteritum</small><span>${esc(entry.praeteritum)}</span></div><div class="form"><small>Perfekt</small><span>${esc(entry.perfekt)}</span></div></div>
    <details><summary>Erklärung und 3 Beispiele</summary><p class="explanation"${rtlAttr()}>${esc(localized(entry,"explanation"))}</p><ol class="examples">${entry.examples.map(x=>`<li>${esc(x)}</li>`).join("")}</ol></details>
  </article>`;
}

function renderReference(){
  const term=searchEl.value.trim().toLocaleLowerCase("de");
  const prep=prepFilterEl.value;
  const hits=DATA.filter(entry => (!prep || entry.preposition===prep) && (!term || [entry.verb,entry.prep,localized(entry,"meaning"),localized(entry,"explanation"),...entry.examples].some(value=>value.toLocaleLowerCase("de").includes(term))));
  countEl.textContent=term||prep ? `${hits.length} von ${DATA.length} Verbindungen` : `${DATA.length} Verbindungen insgesamt`;
  const sections=PREP_ORDER.map(name=>[name,hits.filter(entry=>entry.preposition===name)]).filter(([,items])=>items.length);
  groupsEl.innerHTML=sections.length ? sections.map(([name,items])=>`<section class="group"><div class="group-head"><h2>${esc(name)}</h2><span>${items.length} Verbindungen</span></div><div class="verb-grid">${items.map(card).join("")}</div></section>`).join("") : `<div class="empty">Keine Treffer.</div>`;
}
langSelectEl.addEventListener("change",()=>{try{localStorage.setItem(LANG_KEY,langSelectEl.value);}catch(e){}renderReference();});
searchEl.addEventListener("input",renderReference);
prepFilterEl.addEventListener("change",renderReference);
renderReference();

const STREAK_KEY="dg-prep-best-streak";
const MISTAKES_KEY="dg-prep-mistakes";
let questions=[];let questionIndex=0;let score=0;let streak=0;let peakStreak=0;let answered=false;
function getBest(){try{return Number(localStorage.getItem(BEST_KEY)||0);}catch(e){return 0;}}
function saveBest(value){try{localStorage.setItem(BEST_KEY,String(value));}catch(e){}}
function getBestStreak(){try{return Number(localStorage.getItem(STREAK_KEY)||0);}catch(e){return 0;}}
function saveBestStreak(value){try{localStorage.setItem(STREAK_KEY,String(value));}catch(e){}}
function entryKey(entry){return entry.verb+"|"+entry.prep;}
function loadMistakes(){try{return JSON.parse(localStorage.getItem(MISTAKES_KEY)||"{}");}catch(e){return {};}}
function saveMistakes(map){try{localStorage.setItem(MISTAKES_KEY,JSON.stringify(map));}catch(e){}}
function recordAnswer(entry,wasCorrect){
  const mistakes=loadMistakes();const key=entryKey(entry);
  const current=mistakes[key]||0;
  mistakes[key]=wasCorrect?Math.max(0,Math.floor(current/2)):current+1;
  saveMistakes(mistakes);
}
// Verben mit mehr vergangenen Fehlern erscheinen häufiger (einfache Spaced Repetition).
function weightedSample(items,weights,count){
  const pool=items.map((item,i)=>({item,weight:weights[i]}));
  const picked=[];
  for(let n=0;n<count&&pool.length;n++){
    const total=pool.reduce((s,p)=>s+p.weight,0);
    let r=Math.random()*total;let idx=0;
    for(;idx<pool.length-1;idx++){r-=pool[idx].weight;if(r<=0)break;}
    picked.push(pool[idx].item);pool.splice(idx,1);
  }
  return picked;
}
function gameStartScreen(){
  gameBox.innerHTML=`<h2>Präpositionen trainieren</h2><p>Du bekommst zehn Verben — Wörter, bei denen du bisher öfter danebenlagst, kommen etwas häufiger dran. Wähle jeweils die passende Präposition mit Kasus. Nach jeder Antwort siehst du sofort die Lösung und drei Beispielsätze.</p><div class="game-stats"><span class="stat">10 Fragen</span><span class="stat">Bestwert: ${getBest()}/10</span><span class="stat">Beste Serie: ${getBestStreak()}</span></div><button class="primary" type="button" id="startGame">Spiel starten</button>`;
  document.getElementById("startGame").addEventListener("click",startGame);
}
function startGame(){
  const mistakes=loadMistakes();
  const weights=DATA.map(e=>1+(mistakes[entryKey(e)]||0)*2);
  questions=weightedSample(DATA,weights,10);
  questionIndex=0;score=0;streak=0;peakStreak=0;showQuestion();
}
function optionSet(correct){return shuffle([correct,...shuffle(PREP_ANSWERS.filter(x=>x!==correct)).slice(0,3)]);}
function showQuestion(){
  answered=false;
  const q=questions[questionIndex];
  gameBox.innerHTML=`<div class="game-stats"><span class="stat">Frage ${questionIndex+1}/10</span><span class="stat" id="scoreStat">Punkte: ${score}</span><span class="stat" id="streakStat">Serie: ${streak}</span><span class="stat">Bestwert: ${getBest()}/10</span><span class="stat">Beste Serie: ${getBestStreak()}</span></div><p class="question-label">Welche Präposition + welcher Kasus?</p><div class="question-verb">${esc(q.verb)}</div><p class="question-meaning"${rtlAttr()}>${esc(localized(q,"meaning"))}</p><div class="answers">${optionSet(q.prep).map(option=>`<button type="button" class="answer" data-answer="${esc(option)}">${esc(option)}</button>`).join("")}</div><div id="feedback" aria-live="polite"></div>`;
  gameBox.querySelectorAll(".answer").forEach(button=>button.addEventListener("click",()=>answerQuestion(button,q)));
}
function answerQuestion(button,q){
  if(answered)return;answered=true;
  const chosen=button.dataset.answer;const correct=chosen===q.prep;
  if(correct){score++;streak++;if(streak>peakStreak)peakStreak=streak;}else{streak=0;}
  recordAnswer(q,correct);
  document.getElementById("scoreStat").textContent=`Punkte: ${score}`;
  document.getElementById("streakStat").textContent=`Serie: ${streak}`;
  gameBox.querySelectorAll(".answer").forEach(b=>{b.disabled=true;if(b.dataset.answer===q.prep)b.classList.add("correct");});
  if(!correct)button.classList.add("wrong");
  document.getElementById("feedback").innerHTML=`<div class="feedback"><strong class="${correct?"good":"bad"}">${correct?"Richtig!":"Noch nicht."}</strong> Die Lösung ist <b>${esc(q.prep)}</b>.<ol class="examples">${q.examples.map(x=>`<li>${esc(x)}</li>`).join("")}</ol><button type="button" class="next-game" id="nextQuestion">${questionIndex===9?"Ergebnis anzeigen":"Nächste Frage"}</button></div>`;
  document.getElementById("nextQuestion").addEventListener("click",()=>{questionIndex++;questionIndex<10?showQuestion():showResult();});
}
function showResult(){
  const best=Math.max(getBest(),score);saveBest(best);
  const bestStreak=Math.max(getBestStreak(),peakStreak);saveBestStreak(bestStreak);
  const text=score>=9?"Sehr stark!":score>=7?"Gut gemacht!":score>=5?"Guter Anfang — noch eine Runde hilft.":"Übe zuerst einige Gruppen und versuche es dann erneut.";
  gameBox.innerHTML=`<h2>Runde beendet</h2><div class="result-score">${score}/10</div><p>${text}</p><div class="game-stats"><span class="stat">Bestwert: ${best}/10</span><span class="stat">Beste Serie: ${bestStreak}</span></div><button class="primary" type="button" id="restartGame">Neue 10 Fragen</button>`;
  document.getElementById("restartGame").addEventListener("click",startGame);
}
gameStartScreen();
</script>
</body>
</html>
'''

html = (template
        .replace("__COUNT__", str(len(entries)))
        .replace("__PREP_COUNT__", str(len(counts)))
        .replace("__FILTER_OPTIONS__", filter_options)
        .replace("__LANG_OPTIONS__", lang_options)
        .replace("__DATA__", payload)
        .replace("__PREP_ANSWERS__", json.dumps(prep_answers, ensure_ascii=False))
        .replace("__PREP_ORDER__", json.dumps(PREP_ORDER, ensure_ascii=False))
        .replace("__RTL_LANGS__", rtl_langs))

(OUT / "verben-mit-praepositionen.html").write_text(html, encoding="utf-8")
print(f"verben-mit-praepositionen.html -> {OUT}  ({len(entries)} entries)")
