"""Make the search obvious, and show how much of the list is worked through.

The search box was sitting in the row of filter chips and read as one more
chip, so Serhii did not find it. It gets its own full-width line.

And the question he actually asks himself - how many of the 164 have I dealt
with, how many are left - had no answer on screen. A house counts as worked
once it carries any status at all.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    if old not in s:
        raise SystemExit("NOT FOUND: " + old[:100])
    s = s.replace(old, new, 1)


# ---- search on its own line ----------------------------------------------
swap('<input id="q" type="search" placeholder="город, адрес, №, цена…">\n</div>',
     '</div>\n'
     '<div class="find"><span class="mag">🔍</span>'
     '<input id="q" type="search" placeholder="Найти дом: город, адрес, № или цена">'
     '<button id="qx" title="очистить">✕</button></div>')

swap("input[type=search]{font:inherit;padding:7px 12px;border:1px solid var(--line);\n"
     " border-radius:999px;background:var(--card);color:var(--ink);flex:1;min-width:160px}",
     """.find{display:flex;align-items:center;gap:8px;margin:11px 0 2px;
 background:var(--card);border:1px solid var(--line);border-radius:999px;
 padding:3px 6px 3px 14px;box-shadow:var(--sh)}
.find .mag{font-size:15px;opacity:.65}
input[type=search]{font:inherit;font-size:16px;padding:9px 2px;border:0;outline:0;
 background:transparent;color:var(--ink);flex:1;min-width:60px;
 -webkit-appearance:none}
input[type=search]::-webkit-search-cancel-button{display:none}
#qx{border:0;background:transparent;color:var(--soft);font-size:15px;padding:7px 11px;
 visibility:hidden}
#qx.on{visibility:visible}""")

# ---- how far through the list we are --------------------------------------
swap('<div class="stbar" id="people"></div>',
     '<div class="prog" id="prog"></div>\n<div class="stbar" id="people"></div>')

swap("#people button{border-color:var(--gold)}",
     """.prog{margin:12px 0 2px;font-size:13.5px;color:var(--soft)}
.prog .row{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}
.prog b{color:var(--ink);font-variant-numeric:tabular-nums;font-size:15px}
.prog .rest{margin-left:auto}
.prog .bar{height:6px;border-radius:999px;background:var(--line);margin-top:6px;
 overflow:hidden}
.prog .bar i{display:block;height:100%;background:var(--accent);border-radius:999px;
 transition:width .3s}
@media(prefers-reduced-motion:reduce){.prog .bar i{transition:none}}
#people button{border-color:var(--gold)}""")

swap("function renderPeople(){",
     """function renderProgress(){
  const box=document.getElementById('prog');
  if(!box||!HOUSES.length) return;
  const done=HOUSES.filter(function(h){ return stVal(h.id); }).length;
  const marked=HOUSES.filter(function(h){ return stVal(h.id)==='marcado'; }).length;
  const seen=HOUSES.filter(function(h){ return stVal(h.id)==='visto'; }).length;
  const pct=Math.round(done/HOUSES.length*100);
  box.innerHTML='<div class="row">отработано <b>'+done+'</b> из <b>'+HOUSES.length+'</b>'+
    (marked?' · договорились <b>'+marked+'</b>':'')+
    (seen?' · посмотрели <b>'+seen+'</b>':'')+
    '<span class="rest">осталось <b>'+(HOUSES.length-done)+'</b></span></div>'+
    '<div class="bar"><i style="width:'+pct+'%"></i></div>';
}
function renderPeople(){""")

swap("  renderPeople();", "  renderPeople();\n  renderProgress();")

# ---- the clear button -----------------------------------------------------
swap("document.getElementById('q').addEventListener('input',e=>{q=e.target.value.trim().toLowerCase();render();});",
     """const qbox=document.getElementById('q'), qclr=document.getElementById('qx');
qbox.addEventListener('input',function(e){
  q=e.target.value.trim().toLowerCase();
  qclr.classList.toggle('on',!!q);
  render();
});
qclr.addEventListener('click',function(){
  qbox.value=''; q=''; qclr.classList.remove('on'); qbox.focus(); render();
});""")

p.write_text(s, encoding="utf-8")
print("search line + progress added")
