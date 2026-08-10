"""Show, and filter by, where each house stands.

Serhii marks a house escrito / resposta / visita / top / arquivo as he works
through the list, but until now there was no way to ask "who did I write to?".
A row of counters under the filters answers it at a glance and doubles as the
filter itself.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")

# ---- the row --------------------------------------------------------------
s = s.replace('<div class="links">',
              '<div class="stbar" id="stbar"></div>\n<div class="links">')

s = s.replace(
    ".links{display:flex;",
    ".stbar{display:flex;gap:7px;overflow-x:auto;padding:9px 0 3px;scrollbar-width:none}\n"
    ".stbar::-webkit-scrollbar{display:none}\n"
    ".stbar button{flex:0 0 auto;padding:6px 13px;font-size:13.5px;display:flex;"
    "align-items:center;gap:7px}\n"
    ".stbar button .n{font-variant-numeric:tabular-nums;font-weight:600;"
    "background:var(--accent-s);color:var(--accent);border-radius:999px;"
    "padding:1px 7px;font-size:12px}\n"
    ".stbar button.on .n{background:rgba(255,255,255,.25);color:inherit}\n"
    ".stbar button.zero{opacity:.45}\n"
    ".links{display:flex;")

# ---- counters + filter ----------------------------------------------------
STBAR_JS = r"""
const ST_LABELS={escrito:'✍ escrito',resposta:'↩ resposta',visita:'📅 visita',
                 top:'★ top',arquivo:'✕ arquivo'};
function renderStBar(){
  const box=document.getElementById('stbar');
  if(!box) return;
  const n={}; Object.keys(ST_LABELS).forEach(function(k){n[k]=0;});
  Object.keys(STATUS).forEach(function(id){
    if(n[STATUS[id]]!=null) n[STATUS[id]]++;
  });
  box.innerHTML=Object.keys(ST_LABELS).map(function(k){
    return '<button data-f="st:'+k+'"'+
      (filt==='st:'+k?' class="on"':(n[k]?'':' class="zero"'))+'>'+
      ST_LABELS[k]+'<span class="n">'+n[k]+'</span></button>';
  }).join('');
}
"""
s = s.replace("function render(){", STBAR_JS + "\nfunction render(){")

s = s.replace(" renderRota(); renderMapa(list);",
              " renderRota(); renderMapa(list); renderStBar();")

s = s.replace(" if(filt==='mapa'&&!h.lat)return false;",
              " if(filt==='mapa'&&!h.lat)return false;\n"
              " if(filt.indexOf('st:')===0&&STATUS[h.id]!==filt.slice(3))return false;")

# the status chips live outside .bar, so clear the old highlight by hand
s = s.replace(
    " const f=e.target.closest('[data-f]'); if(f){filt=f.dataset.f;\n"
    "   document.querySelectorAll('[data-f]').forEach(x=>x.classList.toggle('on',x===f));render();return;}",
    " const f=e.target.closest('[data-f]');\n"
    " if(f){ filt=(filt===f.dataset.f&&filt.indexOf('st:')===0)?'all':f.dataset.f;\n"
    "   document.querySelectorAll('[data-f]').forEach(x=>\n"
    "     x.classList.toggle('on',x.dataset.f===filt));\n"
    "   render(); return;}")

p.write_text(s, encoding="utf-8")
print("status bar added")
