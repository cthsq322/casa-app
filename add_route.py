"""Add visit scheduling and a day route to the static app.

Serhii sets a date+time on a house; the Rota view groups the visits by day,
orders them by time, shows the drive between stops and flags pairs that are
too close together to make. One tap opens the whole day in Google Maps.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")

# ---- visit input inside each card ----------------------------------------
s = s.replace(
    """  '<div class="st">'+['escrito','resposta','visita','top','arquivo']""",
    """  '<div class="visit"><span class="vl">visita</span>'+
   '<input type="datetime-local" data-visit="'+h.id+'" value="'+(VISITS[h.id]||'')+'">'+
   (VISITS[h.id]?'<button class="clr" data-clr="'+h.id+'">x</button>':'')+'</div>'+
  '<div class="st">'+['escrito','resposta','visita','top','arquivo']""")

# ---- state ----------------------------------------------------------------
s = s.replace(
    "let HOUSES=[],NOTES={},STATUS={},filt='all',q='',me=localStorage.getItem('casa_user');",
    "let HOUSES=[],NOTES={},STATUS={},VISITS={},filt='all',q='',me=localStorage.getItem('casa_user');")

s = s.replace(
    """  localStorage.setItem('casa_status',JSON.stringify(STATUS));
}""",
    """  localStorage.setItem('casa_status',JSON.stringify(STATUS));
  localStorage.setItem('casa_visits',JSON.stringify(VISITS));
}""", 1)

s = s.replace(
    """    STATUS=JSON.parse(localStorage.getItem('casa_status')||'{}');
    return JSON.parse(localStorage.getItem('casa_notes')||'[]');""",
    """    STATUS=JSON.parse(localStorage.getItem('casa_status')||'{}');
    VISITS=JSON.parse(localStorage.getItem('casa_visits')||'{}');
    return JSON.parse(localStorage.getItem('casa_notes')||'[]');""")

s = s.replace(
    """    STATUS=d.status||{};
    return d.notes||[];""",
    """    STATUS=d.status||{};
    VISITS=d.visits||{};
    return d.notes||[];""")

s = s.replace(
    """    const body={notes:[...map.values()],status:Object.assign({},cur.status||{},STATUS),v:1};""",
    """    const body={notes:[...map.values()],
                status:Object.assign({},cur.status||{},STATUS),
                visits:Object.assign({},cur.visits||{},VISITS),v:1};""")

s = s.replace(
    """    STATUS=body.status;
    cacheSave();""",
    """    STATUS=body.status; VISITS=body.visits||{};
    cacheSave();""")

# ---- filter chip ----------------------------------------------------------
s = s.replace('<button data-f="flag">&#9888; Alerta</button>',
              '<button data-f="flag">&#9888; Alerta</button><button data-f="rota">Rota</button>')
s = s.replace('<button data-f="flag">⚠ Alerta</button>',
              '<button data-f="flag">⚠ Alerta</button><button data-f="rota">🗺 Rota</button>')

s = s.replace(" if(filt==='flag'&&!h.desc_blockers)return false;",
              " if(filt==='flag'&&!h.desc_blockers)return false;\n"
              " if(filt==='rota'&&!VISITS[h.id])return false;")

s = s.replace('<div class="count" id="count"></div>',
              '<div id="rota"></div><div class="count" id="count"></div>')

# ---- route builder --------------------------------------------------------
ROUTE_JS = r"""
function fmtDay(v){
  var d=new Date(v+'T00:00'); if(isNaN(d)) return v;
  return d.toLocaleDateString('pt-PT',{weekday:'long',day:'2-digit',month:'2-digit'});
}
function fmtTime(v){ return (v||'').slice(11,16); }
function kmBetween(a,b){
  if(!a.lat||!b.lat) return null;
  var R=6371, r=function(x){return x*Math.PI/180;};
  var dp=r(b.lat-a.lat), dl=r(b.lon-a.lon);
  var q=Math.pow(Math.sin(dp/2),2)+Math.cos(r(a.lat))*Math.cos(r(b.lat))*Math.pow(Math.sin(dl/2),2);
  return 2*R*Math.asin(Math.sqrt(q));
}
function renderRota(){
  var box=document.getElementById('rota');
  var ids=Object.keys(VISITS).filter(function(k){return VISITS[k];});
  if(filt!=='rota'||!ids.length){ box.innerHTML=''; return; }
  var items=ids.map(function(id){
      return {h:HOUSES.filter(function(x){return String(x.id)===String(id);})[0], t:VISITS[id]};
    }).filter(function(x){return x.h;})
      .sort(function(a,b){return a.t.localeCompare(b.t);});
  var days={};
  items.forEach(function(it){ var d=it.t.slice(0,10); (days[d]=days[d]||[]).push(it); });
  var html='';
  Object.keys(days).sort().forEach(function(d){
    var list=days[d];
    var pts=list.filter(function(x){return x.h.lat;})
                .map(function(x){return x.h.lat+','+x.h.lon;});
    var maps=pts.length?'https://www.google.com/maps/dir/'+pts.join('/'):'';
    html+='<div class="day"><div class="dh">'+fmtDay(d)+' &middot; '+list.length+
          ' visita'+(list.length>1?'s':'')+
          (maps?'<a class="mapsbtn" target="_blank" rel="noopener" href="'+maps+'">abrir no Maps</a>':'')+
          '</div>';
    list.forEach(function(it,i){
      var prev=i?list[i-1].h:null;
      var dist=prev?kmBetween(prev,it.h):null;
      var drive=dist!=null?Math.round(dist):null;          // ~60 km/h rural = 1 min per km
      var gap=prev?(new Date(it.t)-new Date(list[i-1].t))/60000:null;
      var tight=(drive!=null&&gap!=null&&gap<drive+30);
      html+='<div class="stop'+(tight?' tight':'')+'">'+
        '<b>'+fmtTime(it.t)+'</b>'+
        '<span class="pl">'+(it.h.concelho||'?')+'</span>'+
        '<span class="pr">'+(it.h.price_eur?new Intl.NumberFormat('pt-PT').format(it.h.price_eur)+' &euro;':'')+'</span>'+
        (it.h.agent_phone?'<a href="tel:+351'+it.h.agent_phone+'">&#9742;</a>':'')+
        (dist!=null?'<div class="leg">'+Math.round(dist)+' km &middot; ~'+drive+' min de carro'+
           (tight?' &mdash; pouco tempo entre visitas':'')+'</div>':'')+
        '</div>';
    });
    html+='</div>';
  });
  box.innerHTML=html;
}
"""
s = s.replace("function render(){", ROUTE_JS + "\nfunction render(){")
s = s.replace(" document.getElementById('grid').innerHTML=list.map(card).join('');",
              " document.getElementById('grid').innerHTML=list.map(card).join('');\n renderRota();")

# ---- handlers -------------------------------------------------------------
s = s.replace("document.addEventListener('change',e=>{",
"""document.addEventListener('change',async e=>{
 const vi=e.target.closest('[data-visit]');
 if(vi){ const id=vi.dataset.visit;
   if(vi.value){ VISITS[id]=vi.value; STATUS[id]='visita'; } else { delete VISITS[id]; }
   const okd=await push(); render();
   toast(okd?'Visita marcada':'Guardado no telemovel',!okd); return; }""")

s = s.replace("document.addEventListener('click',async e=>{",
"""document.addEventListener('click',async e=>{
 const cl=e.target.closest('[data-clr]');
 if(cl){ delete VISITS[cl.dataset.clr]; await push(); render(); toast('Visita removida'); return; }""")

# ---- styles ---------------------------------------------------------------
CSS = """.st button{padding:4px 10px;font-size:12.5px}
.visit{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.visit .vl{font-size:12px;color:var(--soft)}
.visit input{font:inherit;font-size:13.5px;padding:6px 8px;border-radius:8px;
 border:1px solid var(--line);background:var(--paper);color:var(--ink);flex:1;min-width:150px}
.visit .clr{padding:5px 11px;font-size:13px}
#rota{margin:10px 0 0}
.day{background:var(--card);border:1px solid var(--line);border-radius:13px;
 box-shadow:var(--sh);margin-bottom:12px;overflow:hidden}
.dh{background:var(--accent-s);color:var(--accent);font-weight:600;padding:11px 14px;
 font-size:14px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.mapsbtn{margin-left:auto;font-size:13px;text-decoration:none;background:var(--accent);
 color:var(--paper);padding:6px 13px;border-radius:999px}
.stop{padding:11px 14px;border-top:1px solid var(--line);font-size:14.5px}
.stop b{font-variant-numeric:tabular-nums;margin-right:8px}
.stop .pl{font-weight:600}
.stop .pr{color:var(--soft);font-size:13.5px;margin-left:8px}
.stop a{text-decoration:none;color:var(--accent);font-size:18px;margin-left:8px}
.stop .leg{font-size:12.5px;color:var(--soft);margin-top:4px}
.stop.tight{background:var(--warn-s)}
.stop.tight .leg{color:var(--warn);font-weight:600}"""
s = s.replace(".st button{padding:4px 10px;font-size:12.5px}", CSS)

p.write_text(s, encoding="utf-8")
print(f"route added, {len(s)//1024} KB")
