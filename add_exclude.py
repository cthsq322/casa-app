"""Take a house out of the loop without deleting it.

Two ways a house stops being worth the drive: you look at the photos again and
it is not for you, or nobody ever answers. Neither means the listing is dead -
it means this trip goes past it. So it drops out of the circle, the day gets
its time back, and one tap puts it back if the agent finally calls.

Refused and sold houses drop out on their own; there is no sense in asking
twice.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new, need=True):
    """Skip what is not there instead of dying halfway through a file."""
    global s
    if old not in s:
        if need:
            print("  пропущено (нет якоря):", old.strip().splitlines()[0][:60])
        return
    s = s.replace(old, new, 1)


# ---- state, shared like the rest ------------------------------------------
swap("let FAVS={}, REMIND={};",
     """let FAVS={}, REMIND={}, SKIP={};
function isSkipped(id){ return !!SKIP[id]; }
function skipBy(id){ const x=SKIP[id]; return x&&x.by; }
function skipWhy(id){ const x=SKIP[id]; return x&&x.why; }
function toggleSkip(id,why){
  if(SKIP[id]) delete SKIP[id];
  else SKIP[id]={by:me, at:stamp(), why:why||'не подходит'};
  soil('k',id);
}
// out of the circle for a reason of its own: refused, or sold
function outOfLoop(id){
  return isSkipped(id) || stVal(id)==='recusa';
}""")

swap("    FAVS=mergeMap(d.favs,FAVS,'f');\n    REMIND=mergeMap(d.remind,REMIND,'r');",
     "    FAVS=mergeMap(d.favs,FAVS,'f');\n    REMIND=mergeMap(d.remind,REMIND,'r');\n"
     "    SKIP=mergeMap(d.skip,SKIP,'k');")
swap("                remind:dropDeleted(cur.remind,REMIND,'r'),v:1};",
     "                remind:dropDeleted(cur.remind,REMIND,'r'),\n"
     "                skip:dropDeleted(cur.skip,SKIP,'k'),v:1};")
swap("FAVS=body.favs||{}; REMIND=body.remind||{};",
     "FAVS=body.favs||{}; REMIND=body.remind||{}; SKIP=body.skip||{};")
swap("  localStorage.setItem('casa_remind',JSON.stringify(REMIND));",
     "  localStorage.setItem('casa_remind',JSON.stringify(REMIND));\n"
     "  localStorage.setItem('casa_skip',JSON.stringify(SKIP));")
swap("    REMIND=JSON.parse(localStorage.getItem('casa_remind')||'{}');",
     "    REMIND=JSON.parse(localStorage.getItem('casa_remind')||'{}');\n"
     "    SKIP=JSON.parse(localStorage.getItem('casa_skip')||'{}');")

# ---- the button, on the card ----------------------------------------------
swap("""   (vTime(h.id)?'<button class="cal" data-cal="'+h.id+'">в календарь</button>':'')+""",
     """   (vTime(h.id)?'<button class="cal" data-cal="'+h.id+'">в календарь</button>':'')+
   '<button class="skip'+(isSkipped(h.id)?' on':'')+'" data-skip="'+h.id+'">'+
     (isSkipped(h.id)?'вернуть в круг':'убрать из круга')+'</button>'+""")

swap(" const cal=e.target.closest('[data-cal]');",
     """ const sk=e.target.closest('[data-skip]');
 if(sk){ const id=sk.dataset.skip, was=isSkipped(id);
   toggleSkip(id);
   const oks=await push(); renderCard(id); renderPlan(); mark();
   toast(oks?(was?'Вернул в круг':'Убрал из круга'):'Сохранено в телефоне',!oks);
   return; }
 const cal=e.target.closest('[data-cal]');""")

# ---- the plan closes over the gap -----------------------------------------
swap("""  (pl.days||[]).forEach(function(d){
    const inWeek=week.has(d.label);""",
     """  let freedTotal=0, droppedTotal=0;
  (pl.days||[]).forEach(function(d){
    const inWeek=week.has(d.label);
    const live=d.stops.filter(function(st){ return !outOfLoop(st.id); });
    const dropped=d.stops.filter(function(st){ return outOfLoop(st.id); });
    const freed=dropped.reduce(function(a,st){ return a+40+st.drive_min; },0);
    freedTotal+=freed; droppedTotal+=dropped.length;""")

swap("""      ' · '+d.stops.length+' домов · '+Math.floor(d.drive_min/60)+' ч '+""",
     """      ' · '+live.length+' домов'+
      (dropped.length?' <s>'+d.stops.length+'</s>':'')+' · '+
      Math.floor(d.drive_min/60)+' ч '+""")

swap("""        d.stops.map(function(x){return x.lat+','+x.lon;}).join('/')+'">в Maps</a></div>';
    d.stops.forEach(function(st){
      html+=planStop(st,inWeek);
      if(inWeek&&!stVal(st.id)) todo.push(st);
    });""",
     """        live.map(function(x){return x.lat+','+x.lon;}).join('/')+'">в Maps</a></div>';
    live.forEach(function(st){
      html+=planStop(st,inWeek);
      if(inWeek&&!stVal(st.id)) todo.push(st);
    });
    if(dropped.length) html+='<div class="pdrop">вне круга: '+
      dropped.map(function(st){ return (st.concelho||'?')+
        (skipWhy(st.id)?' ('+skipWhy(st.id)+')':' (отказ)'); }).join(', ')+
      ' · освободилось '+Math.floor(freed/60)+' ч '+(freed%60)+' мин</div>';""")

swap("""    'Ночуем по пути, поэтому первый дом дня без переезда.</div></div>';""",
     """    'Ночуем по пути, поэтому первый дом дня без переезда.'+
    (droppedTotal?'<br>Вне круга <b>'+droppedTotal+'</b> домов — освободилось <b>'+
      Math.floor(freedTotal/60)+' ч '+(freedTotal%60)+' мин</b>.':'')+
    '</div></div>';""")

# excluded houses lose the "call them" badge
swap("""  (DAYOF[h.id]
    ? '<div class="bday'""",
     """  (DAYOF[h.id]&&!outOfLoop(h.id)
    ? '<div class="bday'""")

swap(" if(filt==='thisweek'&&!(DAYOF[h.id]&&DAYOF[h.id].week))return false;",
     " if(filt==='thisweek'&&(!(DAYOF[h.id]&&DAYOF[h.id].week)||outOfLoop(h.id)))"
     "return false;\n"
     " if(filt==='skipped'&&!isSkipped(h.id))return false;")

swap('  <button data-f="thisweek">📆 Эта неделя</button>',
     '  <button data-f="thisweek">📆 Эта неделя</button>\n'
     '  <button data-f="skipped">🙅 Вне круга</button>')

swap(".pnight{padding:9px 14px;border-top:1px solid var(--line);font-size:13px;",
     """.skip{padding:5px 12px;font-size:12.5px;border-color:var(--line);color:var(--soft)}
.skip.on{border-color:var(--warn);color:var(--warn);font-weight:600}
.pdrop{padding:9px 14px;border-top:1px solid var(--line);font-size:12.5px;
 color:var(--soft);font-style:italic}
.pnight{padding:9px 14px;border-top:1px solid var(--line);font-size:13px;""")

p.write_text(s, encoding="utf-8")
print("houses can leave the circle and come back")
