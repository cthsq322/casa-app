"""Give the statuses the shape of the actual chase.

The old ladder assumed every call gets answered. It does not: sometimes the
listing has no number, sometimes nobody picks up, and sometimes the answer is
no - and the reason for that no is the useful part. "Отказ" alone tells you
nothing next week; "отказ - не под кредит" tells you not to bother with the
other listing from the same agent.

The buttons split in two rows because they are two different moments: what I
did to reach them, and what came back.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    if old not in s:
        raise SystemExit("NOT FOUND: " + old[:110])
    s = s.replace(old, new, 1)


# ---- the two halves of the funnel ----------------------------------------
swap("""const ST_LABELS={escrito:'✍ написал',ligado:'☎ позвонил',
  espera:'⏳ жду',resposta:'↩ ответили',marcado:'📅 договорились',
  visto:'👁 посмотрели',top:'★ фаворит',arquivo:'✕ отпал'};
const ST_SHORT={escrito:'написал',ligado:'позвонил',espera:'жду',
  resposta:'ответили',marcado:'договорились',visto:'посмотрели',
  top:'фаворит',arquivo:'отпал'};""",
     """const ST_REACH=['escrito','ligado','semresp','semtel'];
const ST_BACK=['espera','resposta','marcado','visto','top','recusa'];
const ST_LABELS={escrito:'✍ написал',ligado:'☎ позвонил',
  semresp:'📵 не дозвонился',semtel:'🚫 нет номера',
  espera:'⏳ жду',resposta:'↩ ответили',marcado:'📅 договорились',
  visto:'👁 посмотрели',top:'★ фаворит',recusa:'✕ отказ'};
const ST_SHORT={escrito:'написал',ligado:'позвонил',semresp:'не дозвонился',
  semtel:'нет номера',espera:'жду',resposta:'ответили',marcado:'договорились',
  visto:'посмотрели',top:'фаворит',recusa:'отказ'};
// why a no is a no - the part worth remembering
const WHY={credito:'не под кредит',vendido:'уже продан',caro:'дорого',
  docs:'проблемы с документами',naoserve:'не подходит',outro:'другое'};
function stWhy(id){ const x=STATUS[id]; return x&&typeof x==='object'?x.why:null; }
function setWhy(id,w){
  const x=STATUS[id];
  STATUS[id]={v:(x&&x.v)||'recusa',by:me,at:stamp(),why:w};
  soil('s',id);
}""")

# ---- the buttons on the card ---------------------------------------------
swap("""  '<div class="st">'+['escrito','ligado','espera','resposta','marcado','visto','top','arquivo']
    .map(s=>'<button data-st="'+s+'" data-h="'+h.id+'"'+((stVal(h.id)||h.status)===s?' class="on"':'')+'>'+ST_SHORT[s]+'</button>').join('')+
  '</div></div>';""",
     """  '<div class="stg"><span class="gl">что сделал</span><div class="st">'+
    ST_REACH.map(s=>'<button data-st="'+s+'" data-h="'+h.id+'"'+
      ((stVal(h.id)||h.status)===s?' class="on"':'')+'>'+ST_SHORT[s]+'</button>').join('')+
  '</div></div>'+
  '<div class="stg"><span class="gl">что в ответ</span><div class="st">'+
    ST_BACK.map(s=>'<button data-st="'+s+'" data-h="'+h.id+'"'+
      ((stVal(h.id)||h.status)===s?' class="on"':'')+'>'+ST_SHORT[s]+'</button>').join('')+
  '</div></div>'+
  (stVal(h.id)==='recusa'
    ? '<div class="stg why"><span class="gl">почему отказ</span><div class="st">'+
      Object.keys(WHY).map(w=>'<button data-why="'+w+'" data-h="'+h.id+'"'+
        (stWhy(h.id)===w?' class="on"':'')+'>'+WHY[w]+'</button>').join('')+
      '</div></div>'
    : '')+
  '</div>';""")

# ---- the reason travels with the status ----------------------------------
swap("""  (stBy(h.id)?'<div class="stby">'+(ST_SHORT[stVal(h.id)]||stVal(h.id))+
     ' · <b>'+stBy(h.id)+'</b>'+(stAt(h.id)?' · '+stAt(h.id).slice(5,10):'')+'</div>':'')+""",
     """  (stBy(h.id)?'<div class="stby">'+(ST_SHORT[stVal(h.id)]||stVal(h.id))+
     (stWhy(h.id)?' · '+(WHY[stWhy(h.id)]||stWhy(h.id)):'')+
     ' · <b>'+stBy(h.id)+'</b>'+(stAt(h.id)?' · '+stAt(h.id).slice(5,10):'')+'</div>':'')+""")

swap(" const tl=e.target.closest('[data-tel]');",
     """ const wy=e.target.closest('[data-why]');
 if(wy){ setWhy(wy.dataset.h,wy.dataset.why); render();
   const okw=await push(); mark();
   toast(okw?'Причина: '+WHY[wy.dataset.why]:'Сохранено в телефоне',!okw); return; }
 const tl=e.target.closest('[data-tel]');""")

# setting any other status clears a reason that no longer applies
swap("function setStatus(id,v){ STATUS[id]={v:v,by:me,at:stamp()}; soil('s',id); }",
     """function setStatus(id,v){
  const keep = v==='recusa' ? stWhy(id) : null;
  STATUS[id]={v:v,by:me,at:stamp(),why:keep};
  soil('s',id);
}""")

# ---- anything saved under the old names keeps working --------------------
swap("    if(stVal(id)==='visita'){ STATUS[id]={v:'marcado',by:stBy(id),at:stAt(id)}; moved=true; }",
     """    const v=stVal(id);
    const to = v==='visita' ? 'marcado' : (v==='arquivo' ? 'recusa' : null);
    if(to){ STATUS[id]={v:to,by:stBy(id),at:stAt(id),why:stWhy(id)}; moved=true; }""")

# ---- styles ---------------------------------------------------------------
swap(".st{display:flex;flex-wrap:wrap;gap:5px}",
     """.stg{display:flex;flex-direction:column;gap:4px}
.stg .gl{font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;
 color:var(--soft)}
.stg.why .gl{color:var(--warn)}
.stg.why .st button.on{background:var(--warn);border-color:var(--warn);color:#fff}
.st{display:flex;flex-wrap:wrap;gap:5px}""")

p.write_text(s, encoding="utf-8")
print("funnel: reach / response / reason")
