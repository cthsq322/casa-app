"""Show the trip: the loop, day by day, with who still has to be asked.

The plan is computed on the machine against real roads and shipped as a file -
this view just reads it. Each stop carries its own status, so the list doubles
as the call list: whoever is still grey has not been contacted, and the day
only happens if they answer.

Nights are spent along the route, so a day starts where the previous one
ended - that is why the first stop of each day has no drive time.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    assert old in s, "NOT FOUND: " + old[:110]
    s = s.replace(old, new, 1)


swap('<button data-f="gone">🚫 Снятые</button>',
     '<button data-f="gone">🚫 Снятые</button>\n'
     '  <button data-f="plan">🧭 Круг</button>')

swap('<div id="rota"></div>', '<div id="rota"></div><div id="planbox"></div>')

PLAN_JS = r"""
let PLAN=null, planAsked=false;
async function loadPlan(){
  if(planAsked) return PLAN;
  planAsked=true;
  try{
    const r=await fetch('plan.json?t='+Date.now(),{cache:'no-store'});
    if(r.ok) PLAN=await r.json();
  }catch(e){}
  return PLAN;
}
function planStop(st,weekly){
  const v=stVal(st.id), lab=v?(ST_SHORT[v]||v):'';
  const cls = v==='marcado'?'ok' : v==='recusa'?'no' : v?'mid':'todo';
  const mob = st.phone && telList(st.phone).some(isMobile);
  return '<div class="pstop '+cls+'">'+
    '<b>'+st.at+'</b>'+
    '<span class="pl">'+(st.concelho||'?')+'</span>'+
    '<span class="pr">'+eur(st.price_eur)+'</span>'+
    '<span class="nota'+(st.score<40?' thin':'')+'">'+st.score+'</span>'+
    (st.drive_min?'<span class="leg2">+'+st.drive_min+' мин</span>':'')+
    (lab?'<span class="stt">'+lab+(stBy(st.id)?' · '+stBy(st.id):'')+'</span>'
        :'<span class="stt todo">не писали</span>')+
    (st.phone?'<a href="tel:'+telHref(st.phone)+'">☎</a>':'')+
    (mob?'<a href="'+waLink(telList(st.phone).filter(isMobile)[0])+'" target="_blank" '+
      'rel="noopener">WA</a>':'')+
    '<a href="'+st.url+'" target="_blank" rel="noopener">дом</a>'+
  '</div>';
}
async function renderPlan(){
  const box=document.getElementById('planbox');
  if(!box) return;
  if(filt!=='plan'){ box.innerHTML=''; return; }
  const pl=await loadPlan();
  if(!pl){ box.innerHTML='<div class="day"><div class="dh">План не загрузился</div></div>';
    return; }
  const week=new Set(pl.week||[]);
  const todo=[];
  let html='<div class="planhead">Круг из Лиссабона · <b>'+pl.houses+'</b> домов · '+
    '<b>'+pl.total_drive_h+' ч</b> за рулём'+(pl.by_road?' по дорогам':' по прямой')+
    '<div class="m">В неделю берём дни '+(pl.week||[]).join(', ')+
    ' — <b>'+pl.week_houses+'</b> домов, <b>'+pl.week_drive_h+' ч</b> дороги. '+
    'Ночуем по пути, поэтому первый дом дня без переезда.</div></div>';
  (pl.days||[]).forEach(function(d){
    const inWeek=week.has(d.label);
    html+='<div class="day'+(inWeek?'':' later')+'"><div class="dh">День '+d.label+
      ' · '+d.stops.length+' домов · '+Math.floor(d.drive_min/60)+' ч '+
      (d.drive_min%60)+' мин за рулём'+
      (inWeek?'':' · <i>отложить, '+d.per_house+' мин на дом</i>')+
      '<a class="mapsbtn" target="_blank" rel="noopener" href="'+
        'https://www.google.com/maps/dir/'+
        d.stops.map(function(x){return x.lat+','+x.lon;}).join('/')+'">в Maps</a></div>';
    d.stops.forEach(function(st){
      html+=planStop(st,inWeek);
      if(inWeek&&!stVal(st.id)) todo.push(st);
    });
    html+='</div>';
  });
  if(todo.length){
    html='<div class="day todo"><div class="dh">Написать сегодня — '+todo.length+
      ' домов, без них круг не соберётся</div>'+
      todo.map(function(st){ return planStop(st,true); }).join('')+'</div>'+html;
  }
  box.innerHTML=html;
}
"""
swap("function renderStBar(){", PLAN_JS + "\nfunction renderStBar(){")

swap(" renderRota(); renderMapa(list); renderStBar();",
     " renderRota(); renderMapa(list); renderStBar(); renderPlan();")

# the plan is its own view - the card list steps aside
swap(" document.getElementById('grid').innerHTML=(filt==='mapa'?'':list.map(card).join(''));",
     " document.getElementById('grid').innerHTML="
     "((filt==='mapa'||filt==='plan')?'':list.map(card).join(''));")

swap(" if(filt==='gone'&&!isSold(h))return false;",
     " if(filt==='plan')return false;          // the plan draws itself\n"
     " if(filt==='gone'&&!isSold(h))return false;")

swap(".day{background:var(--card);border:1px solid var(--line);border-radius:13px;",
     """.planhead{background:var(--accent-s);border:1px solid var(--accent);
 border-radius:13px;padding:12px 14px;margin:10px 0;font-size:14.5px;color:var(--accent)}
.planhead .m{color:var(--soft);font-size:13px;margin-top:5px;font-weight:400}
.day.later{opacity:.6}
.day.todo{border-color:var(--warn)}
.day.todo .dh{background:var(--warn);color:var(--paper)}
.pstop{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;padding:9px 14px;
 border-top:1px solid var(--line);font-size:14px}
.pstop b{font-variant-numeric:tabular-nums}
.pstop .pl{font-weight:600}
.pstop .pr{color:var(--soft);font-variant-numeric:tabular-nums}
.pstop .leg2{color:var(--soft);font-size:12.5px}
.pstop .stt{font-size:12px;color:var(--soft)}
.pstop .stt.todo{color:var(--warn);font-weight:600}
.pstop a{margin-left:auto;text-decoration:none;color:var(--accent);font-size:13px;
 border:1px solid var(--line);border-radius:8px;padding:3px 9px}
.pstop a+a{margin-left:0}
.pstop.ok{background:var(--accent-s)}
.pstop.no{opacity:.5;text-decoration:line-through}
.day{background:var(--card);border:1px solid var(--line);border-radius:13px;""")

p.write_text(s, encoding="utf-8")
print("plan view added")
