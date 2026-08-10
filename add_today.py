"""Tomorrow on one screen: the hours, the road, the gaps, and who is silent.

Serhii asked for the whole day in one place - when each viewing is, how long
the drive between them takes, where the empty hours are, and which agents have
still not answered. Until now that lived in three places: the route tab, the
status chips and his own head.

The day is built from what is actually booked, so it changes the moment an
agent confirms. Houses he wrote to but who never answered sit underneath, so
the day and the chase are on the same screen.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    assert old in s, "NOT FOUND: " + old[:110]
    s = s.replace(old, new, 1)


swap('  <button data-f="starred">★ Со звёздами</button>',
     '  <button data-f="starred">★ Со звёздами</button>\n'
     '  <button data-f="day">📋 Мой день</button>')

swap('<div id="rota"></div>', '<div id="dayplan"></div><div id="rota"></div>')

DAY_JS = r"""
function dayKey(off){
  const d=new Date(); d.setDate(d.getDate()+off); d.setHours(0,0,0,0);
  return d.getFullYear()+'-'+pad2(d.getMonth()+1)+'-'+pad2(d.getDate());
}
function dayTitle(off){
  const d=new Date(); d.setDate(d.getDate()+off);
  const RU=['воскресенье','понедельник','вторник','среда','четверг','пятница','суббота'];
  return (off===0?'сегодня':off===1?'завтра':RU[d.getDay()])+', '+
    pad2(d.getDate())+'.'+pad2(d.getMonth()+1);
}
let dayOff = 1;                                  // tomorrow by default
async function renderDay(){
  const box=document.getElementById('dayplan');
  if(!box) return;
  if(filt!=='day'){ box.innerHTML=''; return; }
  const key=dayKey(dayOff);
  const stops=Object.keys(VISITS).map(function(id){
    const t=vTime(id); if(!t||t.slice(0,10)!==key) return null;
    let h=HOUSES.filter(function(x){return String(x.id)===String(id);})[0];
    if(!h) return null;
    const pp=pinPos(h); if(pp) h=Object.assign({},h,{lat:pp[0],lon:pp[1]});
    return {h:h,t:t,ok:vOk(id),before:vBefore(id)};
  }).filter(Boolean).sort(function(a,b){ return a.t.localeCompare(b.t); });

  let html='<div class="dayhead">'+
    '<button class="dnav" data-day="-1">&larr;</button>'+
    '<b>'+dayTitle(dayOff)+'</b>'+
    '<button class="dnav" data-day="1">&rarr;</button>'+
    '<span class="cnt2">'+stops.length+' '+
      (stops.length===1?'осмотр':stops.length<5?'осмотра':'осмотров')+'</span></div>';

  if(!stops.length){
    html+='<div class="dayempty">на этот день ничего не назначено</div>';
  } else {
    await fillRoads(stops);
    let total=0;
    stops.forEach(function(it,i){
      const prev=i?stops[i-1]:null;
      const road=prev?ROADS[roadKey(prev.h,it.h)]:null;
      if(prev){
        const mins=road?Math.round(road.min):null;
        const kms=road?Math.round(road.km):null;
        const gap=(new Date(it.t)-new Date(prev.t))/60000-40;
        if(mins!=null) total+=mins;
        html+='<div class="dleg'+(mins!=null&&gap<mins?' tight':'')+'">'+
          (mins!=null?'&darr; '+kms+' км · '+mins+' мин за рулём':'&darr; дорога')+
          (mins!=null&&gap>mins+20?' · свободно '+Math.round(gap-mins)+' мин':'')+
          (mins!=null&&gap<mins?' · НЕ УСПЕВАЕМ':'')+'</div>';
      }
      const t=bestTier(it.h.id);
      html+='<div class="dstop'+(it.ok?'':' pending')+'">'+
        '<b>'+it.t.slice(11,16)+'</b>'+
        '<span class="pl">'+(it.h.concelho||'?')+'</span>'+
        '<span class="pr">'+eur(it.h.price_eur)+'</span>'+
        (it.h.auto_score!=null?'<span class="nota">'+it.h.auto_score+'</span>':'')+
        (t?'<span class="stars">'+'★'.repeat(t)+'</span>':'')+
        (it.ok?'':'<span class="warn2">не подтверждён'+
          (it.before?' · ответить до '+it.before.slice(11,16):'')+'</span>')+
        (pinOf(it.h.id)?'<span class="haspin">точка есть</span>':'')+
        '<div class="dacts">'+
          (it.h.agent_phone?'<a href="tel:'+telHref(it.h.agent_phone)+'">позвонить</a>':'')+
          '<a target="_blank" rel="noopener" href="'+
            (pinOf(it.h.id)&&!pinOf(it.h.id).lat?pinOf(it.h.id).url
             :'https://www.google.com/maps/search/?api=1&query='+it.h.lat+','+it.h.lon)+
            '">карта</a>'+
          '<a target="_blank" rel="noopener" href="'+it.h.url+'">объявление</a>'+
        '</div></div>';
    });
    html+='<div class="daysum">за рулём между домами <b>'+
      Math.floor(total/60)+' ч '+(total%60)+' мин</b></div>';
  }

  // who was written to and never answered - the same screen, underneath
  const waiting=HOUSES.filter(function(h){
    const v=stVal(h.id);
    return (v==='escrito'||v==='ligado'||v==='espera'||v==='semresp')
      && !vTime(h.id) && !outOfLoop(h.id);
  });
  if(waiting.length){
    html+='<div class="dwait"><div class="dwh">ждём ответа — '+waiting.length+'</div>'+
      waiting.slice(0,12).map(function(h){
        return '<div class="dw">'+(h.concelho||'?')+' · '+eur(h.price_eur)+
          ' · нота '+(h.auto_score!=null?h.auto_score:'?')+
          '<span class="who3">'+(ST_SHORT[stVal(h.id)]||'')+
          (stBy(h.id)?' · '+stBy(h.id):'')+'</span>'+
          (h.agent_phone?'<a href="tel:'+telHref(h.agent_phone)+'">☎</a>':'')+
          '</div>';
      }).join('')+
      (waiting.length>12?'<div class="dw">…и ещё '+(waiting.length-12)+'</div>':'')+
      '</div>';
  }
  box.innerHTML=html;
}
"""
swap("function renderStBar(){", DAY_JS + "\nfunction renderStBar(){")

swap(" renderRota(); renderMapa(list); renderStBar(); renderPlan();",
     " renderRota(); renderMapa(list); renderStBar(); renderPlan(); renderDay();")

swap(" if(filt==='plan')return false;          // the plan draws itself",
     " if(filt==='plan')return false;          // the plan draws itself\n"
     " if(filt==='day')return false;           // so does the day")

swap(" document.getElementById('grid').innerHTML="
     "((filt==='mapa'||filt==='plan')?'':list.map(card).join(''));",
     " document.getElementById('grid').innerHTML="
     "((filt==='mapa'||filt==='plan'||filt==='day')?'':list.map(card).join(''));")

swap(" const ag=e.target.closest('[data-agent]');",
     """ const dn=e.target.closest('[data-day]');
 if(dn){ dayOff+=parseInt(dn.dataset.day,10); renderDay(); return; }
 const ag=e.target.closest('[data-agent]');""")

swap(".planhead{background:var(--accent-s);border:1px solid var(--accent);",
     """.dayhead{display:flex;align-items:center;gap:10px;background:var(--accent);
 color:var(--paper);border-radius:13px 13px 0 0;padding:11px 14px;font-size:16px;margin-top:10px}
.dayhead .cnt2{margin-left:auto;font-size:13px;opacity:.9}
.dnav{padding:2px 11px;background:rgba(255,255,255,.2);border-color:transparent;
 color:var(--paper);font-size:15px}
.dayempty{background:var(--card);border:1px solid var(--line);border-top:0;
 border-radius:0 0 13px 13px;padding:16px 14px;color:var(--soft);font-size:14px}
.dstop{background:var(--card);border:1px solid var(--line);border-top:0;
 padding:11px 14px;display:flex;align-items:baseline;gap:9px;flex-wrap:wrap;font-size:14.5px}
.dstop b{font-size:17px;font-variant-numeric:tabular-nums;color:var(--accent)}
.dstop .pl{font-weight:600}
.dstop .pr{color:var(--soft);font-variant-numeric:tabular-nums}
.dstop .stars{color:var(--gold)}
.dstop.pending{background:var(--warn-s)}
.dstop .warn2{font-size:11.5px;color:var(--warn);font-weight:600}
.dstop .haspin{font-size:11px;color:var(--accent)}
.dacts{flex:1 0 100%;display:flex;gap:7px;margin-top:6px}
.dacts a{text-decoration:none;font-size:13px;color:var(--accent);
 border:1px solid var(--line);border-radius:8px;padding:5px 11px}
.dleg{background:var(--paper);border-left:2px solid var(--line);margin-left:22px;
 padding:5px 12px;font-size:12.5px;color:var(--soft)}
.dleg.tight{border-color:var(--warn);color:var(--warn);font-weight:600}
.daysum{background:var(--card);border:1px solid var(--line);border-top:0;
 border-radius:0 0 13px 13px;padding:10px 14px;font-size:13px;color:var(--soft)}
.dwait{margin-top:12px;background:var(--card);border:1px solid var(--line);
 border-radius:13px;overflow:hidden}
.dwh{background:var(--warn-s);color:var(--warn);font-weight:600;padding:10px 14px;
 font-size:13.5px}
.dw{padding:9px 14px;border-top:1px solid var(--line);font-size:13.5px;
 display:flex;align-items:baseline;gap:8px}
.dw .who3{color:var(--soft);font-size:12px}
.dw a{margin-left:auto;text-decoration:none;color:var(--accent);font-size:16px}
.planhead{background:var(--accent-s);border:1px solid var(--accent);""")

p.write_text(s, encoding="utf-8")
print("«Мой день» готов")
