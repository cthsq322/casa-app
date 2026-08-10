"""Keep the search within reach, and warn before a visit day arrives.

Two things Serhii asked for after a day of real use. The search sat at the top
of a long page, so finding a house meant scrolling all the way up first - it
now stays put while the list moves under it.

And a visit booked on Monday is easy to lose by Wednesday. A static page
cannot send a push, so it does the two things it honestly can: it says on
screen when a visit is today or tomorrow, and it hands the phone a calendar
entry with an alarm the day before - that part the phone does send.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    assert old in s, "NOT FOUND: " + old[:110]
    s = s.replace(old, new, 1)


# ---- the search stays where the thumb expects it --------------------------
swap(""".bar{display:flex;flex-wrap:wrap;gap:7px;align-items:center;padding:12px 0;
 position:sticky;top:0;background:var(--paper);z-index:5;border-bottom:1px solid var(--line)}""",
     """.bar{display:flex;flex-wrap:wrap;gap:7px;align-items:center;padding:12px 0}""")

swap(""".find{display:flex;align-items:center;gap:8px;margin:11px 0 2px;""",
     """.find{position:sticky;top:0;z-index:6;display:flex;align-items:center;gap:8px;
 margin:0 0 2px;""")

swap("<div class=\"find\"><span class=\"mag\">🔍</span>",
     "<div class=\"findwrap\"><div class=\"find\"><span class=\"mag\">🔍</span>")
swap("<button id=\"qx\" title=\"очистить\">✕</button></div>",
     "<button id=\"qx\" title=\"очистить\">✕</button></div></div>")

swap(".find .mag{font-size:15px;opacity:.65}",
     """.findwrap{position:sticky;top:0;z-index:6;background:var(--paper);
 padding:8px 0 4px;margin:0 0 4px}
.find .mag{font-size:15px;opacity:.65}""")

# ---- what is coming up ----------------------------------------------------
swap("function renderMine(){",
     """function pad2(n){ return (n<10?'0':'')+n; }
function icsFor(h,t){
  // 90 minutes is a viewing plus the walk round the land
  const start=new Date(t), end=new Date(start.getTime()+90*60000);
  const z=d=>d.getUTCFullYear()+pad2(d.getUTCMonth()+1)+pad2(d.getUTCDate())+'T'+
    pad2(d.getUTCHours())+pad2(d.getUTCMinutes())+'00Z';
  const esc=x=>String(x||'').replace(/[\\\\;,]/g,m=>'\\\\'+m).replace(/\\n/g,'\\\\n');
  const where=[h.concelho,h.freguesia].filter(Boolean).join(', ');
  return ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//casa//RU','CALSCALE:GREGORIAN',
    'BEGIN:VEVENT','UID:casa-'+h.id+'@cthsq322.github.io','DTSTAMP:'+z(new Date()),
    'DTSTART:'+z(start),'DTEND:'+z(end),
    'SUMMARY:'+esc('Осмотр дома — '+where+' — '+eur(h.price_eur)),
    'LOCATION:'+esc(h.lat?h.lat+','+h.lon:where),
    'DESCRIPTION:'+esc((h.agent_phone||'')+'  '+h.url),
    'BEGIN:VALARM','TRIGGER:-P1D','ACTION:DISPLAY',
    'DESCRIPTION:'+esc('Завтра осмотр — '+where),'END:VALARM',
    'BEGIN:VALARM','TRIGGER:-PT2H','ACTION:DISPLAY',
    'DESCRIPTION:'+esc('Через 2 часа осмотр — '+where),'END:VALARM',
    'END:VEVENT','END:VCALENDAR'].join('\\r\\n');
}
function renderSoon(){
  const box=document.getElementById('soon');
  if(!box||!HOUSES.length) return;
  const now=new Date();
  const items=Object.keys(VISITS).map(function(id){
    const t=vTime(id); if(!t) return null;
    const h=HOUSES.filter(function(x){return String(x.id)===String(id);})[0];
    if(!h) return null;
    const when=new Date(t);
    const hours=(when-now)/3600000;
    return (hours>-3 && hours<48) ? {h:h,t:t,when:when,hours:hours} : null;
  }).filter(Boolean).sort(function(a,b){ return a.when-b.when; });
  if(!items.length){ box.innerHTML=''; box.className='soon'; return; }
  box.className='soon on';
  box.innerHTML=items.map(function(it){
    const d=it.when, today=d.toDateString()===now.toDateString();
    const word = it.hours<0 ? 'идёт сейчас'
      : today ? 'сегодня в '+pad2(d.getHours())+':'+pad2(d.getMinutes())
      : 'завтра в '+pad2(d.getHours())+':'+pad2(d.getMinutes());
    return '<div class="s1"><b>'+word+'</b> · '+(it.h.concelho||'?')+
      (it.by?' · '+it.by:'')+
      (it.h.agent_phone?' <a href="tel:'+telHref(it.h.agent_phone)+'">позвонить</a>':'')+
      (it.h.lat?' <a target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query='+
        it.h.lat+','+it.h.lon+'">маршрут</a>':'')+'</div>';
  }).join('');
}
function renderMine(){""")

swap("  renderPeople();\n  renderProgress();\n  renderMine();",
     "  renderPeople();\n  renderProgress();\n  renderMine();\n  renderSoon();")

swap('<div class="mine" id="mine"></div>',
     '<div class="soon" id="soon"></div>\n<div class="mine" id="mine"></div>')

# ---- one tap puts it in the phone's calendar ------------------------------
swap("""   (vBy(h.id)?'<span class="vby">'+vBy(h.id)+'</span>':'')+'</div>'+""",
     """   (vBy(h.id)?'<span class="vby">'+vBy(h.id)+'</span>':'')+
   (vTime(h.id)?'<button class="cal" data-cal="'+h.id+'">напомнить</button>':'')+
   '</div>'+""")

swap(" const lk=e.target.closest('[data-link]');",
     """ const cal=e.target.closest('[data-cal]');
 if(cal){
   const h=HOUSES.find(function(x){return String(x.id)===String(cal.dataset.cal);});
   const t=vTime(cal.dataset.cal);
   if(h&&t){
     const blob=new Blob([icsFor(h,t)],{type:'text/calendar;charset=utf-8'});
     const a=document.createElement('a');
     a.href=URL.createObjectURL(blob);
     a.download='osmotr-'+h.id+'.ics';
     document.body.appendChild(a); a.click(); document.body.removeChild(a);
     setTimeout(function(){URL.revokeObjectURL(a.href);},4000);
     toast('Добавь в календарь — напомнит за день');
   }
   return;
 }
 const lk=e.target.closest('[data-link]');""")

# ---- styles ---------------------------------------------------------------
swap(".mine{margin:11px 0 0;font-size:13.5px;color:var(--soft)}",
     """.soon{display:none}
.soon.on{display:block;margin:10px 0 0;background:var(--warn-s);
 border:1px solid var(--warn);border-radius:12px;padding:10px 13px;font-size:14px}
.soon .s1{padding:2px 0}
.soon b{color:var(--warn)}
.soon a{color:var(--accent);text-decoration:none;margin-left:8px;font-weight:600}
.cal{padding:5px 12px;font-size:12.5px;border-color:var(--accent);color:var(--accent)}
.mine{margin:11px 0 0;font-size:13.5px;color:var(--soft)}""")

p.write_text(s, encoding="utf-8")
print("sticky search + upcoming banner + calendar reminder")
