"""Build share/lista.html - the forwardable version of the shortlist.

Same data as lista_casas.txt, but a page: pick a site, copy all its links at
once, or tap one row to copy just that link. Serhii sends these from his phone,
so it has to work with a thumb and survive being opened in WhatsApp's browser.
"""
import json
import sqlite3
import pathlib
from collections import defaultdict

DB = pathlib.Path(r"E:\MY\casa\data\casa.db")
OUT = pathlib.Path(r"E:\MY\casa\share\lista.html")

SITE_NAMES = {
    "imovirtual.com": "Imovirtual",
    "iadportugal.pt": "IAD Portugal",
    "supercasa.pt": "SuperCasa",
    "era.pt": "ERA",
    "idealista.pt": "Idealista",
    "casa.sapo.pt": "Casa SAPO",
    "kwportugal.pt": "KW Portugal",
    "remax.pt": "RE/MAX",
    "century21.pt": "Century 21",
}

CSS = """
:root{
  --ink:#16201b; --soft:#6b7a6f; --paper:#f7f8f5; --card:#fff;
  --line:#dde2da; --accent:#2e6b4f; --accent-s:#e8efe9; --mark:#c25a2b;
  --sh:0 1px 2px rgba(22,32,27,.06),0 8px 20px -12px rgba(22,32,27,.18);
}
@media (prefers-color-scheme:dark){
  :root{--ink:#e6eae5;--soft:#93a396;--paper:#101511;--card:#171d18;
        --line:#2a332c;--accent:#6fb58e;--accent-s:#1c2b22;--mark:#e08a5c;
        --sh:0 1px 2px rgba(0,0,0,.4),0 8px 20px -12px rgba(0,0,0,.6);}
}
:root[data-theme=dark]{--ink:#e6eae5;--soft:#93a396;--paper:#101511;--card:#171d18;
  --line:#2a332c;--accent:#6fb58e;--accent-s:#1c2b22;--mark:#e08a5c;
  --sh:0 1px 2px rgba(0,0,0,.4),0 8px 20px -12px rgba(0,0,0,.6);}
:root[data-theme=light]{--ink:#16201b;--soft:#6b7a6f;--paper:#f7f8f5;--card:#fff;
  --line:#dde2da;--accent:#2e6b4f;--accent-s:#e8efe9;--mark:#c25a2b;
  --sh:0 1px 2px rgba(22,32,27,.06),0 8px 20px -12px rgba(22,32,27,.18);}

*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font:400 16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  -webkit-text-size-adjust:100%}
.wrap{max-width:760px;margin:0 auto;padding:20px 16px 64px}

header{margin-bottom:20px}
h1{font:600 27px/1.15 ui-serif,Georgia,"Times New Roman",serif;margin:0 0 6px;
  letter-spacing:-.01em;text-wrap:balance}
.sub{color:var(--soft);font-size:14.5px;margin:0}
.sub b{color:var(--ink);font-variant-numeric:tabular-nums}

nav{display:flex;gap:7px;overflow-x:auto;padding:14px 0 4px;margin-bottom:6px;
  scrollbar-width:none}
nav::-webkit-scrollbar{display:none}
nav a{flex:0 0 auto;text-decoration:none;color:var(--ink);background:var(--card);
  border:1px solid var(--line);border-radius:999px;padding:7px 13px;font-size:13.5px;
  white-space:nowrap}
nav a b{color:var(--soft);font-weight:400;font-variant-numeric:tabular-nums}

section{background:var(--card);border:1px solid var(--line);border-radius:14px;
  box-shadow:var(--sh);margin:16px 0;overflow:hidden;scroll-margin-top:12px}
.sh{display:flex;align-items:center;gap:10px;flex-wrap:wrap;
  padding:13px 15px;background:var(--accent-s);border-bottom:1px solid var(--line)}
.sh h2{font:600 17px/1.2 ui-serif,Georgia,serif;margin:0;color:var(--accent)}
.sh .n{color:var(--soft);font-size:13.5px;font-variant-numeric:tabular-nums}
.copyall{margin-left:auto;border:0;border-radius:999px;background:var(--accent);
  color:var(--paper);font:inherit;font-size:13.5px;padding:7px 15px;cursor:pointer}
.copyall.done{background:var(--mark)}

.row{display:block;padding:12px 15px;border-top:1px solid var(--line);
  text-decoration:none;color:inherit;cursor:pointer}
.row:first-of-type{border-top:0}
.row:active{background:var(--accent-s)}
.meta{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap;font-size:14.5px}
.pl{font-weight:600}
.pr{font-variant-numeric:tabular-nums;color:var(--accent);font-weight:600}
.tag{color:var(--soft);font-size:13px}
.u{display:block;margin-top:4px;font:400 12px/1.45 ui-monospace,SFMono-Regular,
  Menlo,Consolas,monospace;color:var(--soft);word-break:break-all}
.row.done .u{color:var(--mark)}

.toast{position:fixed;left:50%;bottom:22px;transform:translateX(-50%) translateY(90px);
  background:var(--ink);color:var(--paper);padding:11px 20px;border-radius:999px;
  font-size:14px;transition:transform .22s ease;z-index:9}
.toast.on{transform:translateX(-50%) translateY(0)}
@media (prefers-reduced-motion:reduce){.toast{transition:none}}
a:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
footer{color:var(--soft);font-size:13px;margin-top:26px;text-align:center}
"""

JS = """
function money(v){return v?new Intl.NumberFormat('pt-PT').format(v)+' \\u20ac':'sob consulta';}
function tags(h){
  var t=[];
  if(h.bedrooms) t.push('T'+h.bedrooms);
  if(h.bathrooms) t.push(h.bathrooms+' wc');
  if(h.area_m2) t.push(h.area_m2+' m\\u00b2');
  if(h.land_area_m2) t.push('terreno '+new Intl.NumberFormat('pt-PT').format(h.land_area_m2)+' m\\u00b2');
  return t.join(' \\u00b7 ');
}
var T=document.getElementById('toast'),tt;
function toast(m){T.textContent=m;T.classList.add('on');clearTimeout(tt);
  tt=setTimeout(function(){T.classList.remove('on');},1700);}
function copy(text,cb){
  if(navigator.clipboard&&window.isSecureContext){
    navigator.clipboard.writeText(text).then(cb,function(){fallback(text,cb);});
  } else fallback(text,cb);
}
function fallback(text,cb){
  var a=document.createElement('textarea');a.value=text;a.style.position='fixed';
  a.style.opacity='0';document.body.appendChild(a);a.select();
  try{document.execCommand('copy');cb();}catch(e){toast('N\\u00e3o deu para copiar');}
  document.body.removeChild(a);
}
function build(){
  var nav=document.getElementById('nav'),main=document.getElementById('main'),html='',navh='';
  DATA.forEach(function(g,gi){
    navh+='<a href="#s'+gi+'">'+g.name+' <b>'+g.items.length+'</b></a>';
    html+='<section id="s'+gi+'"><div class="sh"><h2>'+g.name+'</h2>'+
      '<span class="n">'+g.items.length+' casas</span>'+
      '<button class="copyall" data-g="'+gi+'">copiar links</button></div>';
    g.items.forEach(function(h){
      html+='<a class="row" href="'+h.url+'" target="_blank" rel="noopener" data-u="'+h.url+'">'+
        '<span class="meta"><span class="pl">'+(h.concelho||h.district||'?')+'</span>'+
        '<span class="pr">'+money(h.price_eur)+'</span>'+
        '<span class="tag">'+tags(h)+'</span></span>'+
        '<span class="u">'+h.url+'</span></a>';
    });
    html+='</section>';
  });
  nav.innerHTML=navh; main.innerHTML=html;
}
build();
document.addEventListener('click',function(e){
  var b=e.target.closest('.copyall');
  if(b){
    var g=DATA[+b.dataset.g];
    copy(g.items.map(function(h){return h.url;}).join('\\n'),function(){
      b.classList.add('done'); b.textContent='copiado';
      toast(g.items.length+' links de '+g.name);
      setTimeout(function(){b.classList.remove('done');b.textContent='copiar links';},2200);
    });
    return;
  }
  var r=e.target.closest('.row');
  if(r && !e.metaKey && !e.ctrlKey){
    e.preventDefault();
    copy(r.dataset.u,function(){
      r.classList.add('done'); toast('Link copiado');
      setTimeout(function(){r.classList.remove('done');},1600);
    });
  }
});
"""


def main():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT domain,url,price_eur,area_m2,land_area_m2,bedrooms,bathrooms,"
        "concelho,district FROM listings WHERE url IS NOT NULL "
        "ORDER BY domain, district IS NULL, district, price_eur IS NULL, price_eur"
    ).fetchall()

    by = defaultdict(list)
    for r in rows:
        d = {k: r[k] for k in r.keys() if r[k] not in (None, "")}
        for k in ("bedrooms", "bathrooms", "area_m2", "land_area_m2", "price_eur"):
            if k in d:
                d[k] = int(d[k])
        by[r["domain"]].append(d)

    data = [{"name": SITE_NAMES.get(k, k), "items": v}
            for k, v in sorted(by.items(), key=lambda kv: -len(kv[1]))]

    doc = f"""<title>Casas para ver &middot; lista</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>{CSS}</style>
<div class="wrap">
<header>
  <h1>Casas para ver</h1>
  <p class="sub"><b>{len(rows)}</b> an&uacute;ncios em <b>{len(data)}</b> sites &middot;
     zona centro de Portugal &middot; toque num link para copiar</p>
</header>
<nav id="nav"></nav>
<main id="main"></main>
<footer>Lista de trabalho &mdash; falta ver no local</footer>
</div>
<div class="toast" id="toast"></div>
<script>const DATA={json.dumps(data, ensure_ascii=False, separators=(',', ':'))};
{JS}</script>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc, encoding="utf-8")
    print(f"{OUT} - {len(rows)} links, {OUT.stat().st_size//1024} KB")


if __name__ == "__main__":
    main()
