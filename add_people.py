"""Make the board show who is doing what, and give each person their own list.

Three people work the same 164 houses, so a status without a name is useless -
"позвонил" has to say who called and when. Each person also keeps their own
favourites: Milena picks her ten, works them, drops the ones that fall through
and adds new ones, without touching anyone else's picks.

Statuses and visits were plain values; they become small records carrying the
author. Anything saved in the old shape still reads.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new, required=True):
    global s
    if old not in s:
        if required:
            raise SystemExit("NOT FOUND: " + old[:90])
        return
    s = s.replace(old, new, 1)


# ---- accessors that read both the old and the new shape -------------------
HELPERS = """let FAVS={};
function stVal(id){ const x=STATUS[id]; return x&&typeof x==='object'?x.v:x; }
function stBy(id){ const x=STATUS[id]; return x&&typeof x==='object'?x.by:null; }
function stAt(id){ const x=STATUS[id]; return x&&typeof x==='object'?x.at:null; }
function vTime(id){ const x=VISITS[id]; return x&&typeof x==='object'?x.t:x; }
function vBy(id){ const x=VISITS[id]; return x&&typeof x==='object'?x.by:null; }
function stamp(){ return new Date().toISOString().slice(0,16).replace('T',' '); }
function setStatus(id,v){ STATUS[id]={v:v,by:me,at:stamp()}; soil('s',id); }
function setVisit(id,t){ VISITS[id]={t:t,by:me}; soil('v',id); }

function favList(who){ return FAVS[who||me]||[]; }
function isFav(id,who){ return favList(who).indexOf(String(id))>=0; }
function toggleFav(id){
  const l=favList().slice(), i=l.indexOf(String(id));
  if(i>=0) l.splice(i,1); else l.push(String(id));
  FAVS[me]=l; soil('f',me);
}
function favOwners(id){
  return Object.keys(FAVS).filter(function(u){ return isFav(id,u); });
}
let SYNCED=false;"""
swap("let SYNCED=false;", HELPERS)

# ---- keep favourites in the shared payload --------------------------------
swap("    STATUS=mergeMap(d.status,STATUS,'s');\n"
     "    VISITS=mergeMap(d.visits,VISITS,'v');",
     "    STATUS=mergeMap(d.status,STATUS,'s');\n"
     "    VISITS=mergeMap(d.visits,VISITS,'v');\n"
     "    FAVS=mergeMap(d.favs,FAVS,'f');")
swap("                visits:Object.assign({},cur.visits||{},VISITS),v:1};",
     "                visits:Object.assign({},cur.visits||{},VISITS),\n"
     "                favs:Object.assign({},cur.favs||{},FAVS),v:1};")
swap("    STATUS=body.status; VISITS=body.visits||{};",
     "    STATUS=body.status; VISITS=body.visits||{}; FAVS=body.favs||{};")
swap("  localStorage.setItem('casa_visits',JSON.stringify(VISITS));",
     "  localStorage.setItem('casa_visits',JSON.stringify(VISITS));\n"
     "  localStorage.setItem('casa_favs',JSON.stringify(FAVS));")
swap("    VISITS=JSON.parse(localStorage.getItem('casa_visits')||'{}');",
     "    VISITS=JSON.parse(localStorage.getItem('casa_visits')||'{}');\n"
     "    FAVS=JSON.parse(localStorage.getItem('casa_favs')||'{}');")

# ---- every read of a status or visit goes through the accessors -----------
swap("    if(STATUS[id]==='visita'){ STATUS[id]='marcado'; moved=true; }",
     "    if(stVal(id)==='visita'){ STATUS[id]={v:'marcado',by:stBy(id),at:stAt(id)};"
     " moved=true; }")
swap("    if(n[STATUS[id]]!=null) n[STATUS[id]]++;",
     "    const v=stVal(id); if(n[v]!=null) n[v]++;")
swap(" if(filt.indexOf('st:')===0&&STATUS[h.id]!==filt.slice(3))return false;",
     " if(filt.indexOf('st:')===0&&stVal(h.id)!==filt.slice(3))return false;\n"
     " if(filt==='fav'&&!isFav(h.id))return false;\n"
     " if(filt==='favall'&&!favOwners(h.id).length)return false;\n"
     " if(filt.indexOf('by:')===0&&stBy(h.id)!==filt.slice(3))return false;")
swap(" if(filt==='rota'&&!VISITS[h.id])return false;",
     " if(filt==='rota'&&!vTime(h.id))return false;")
swap("((STATUS[h.id]||h.status)===s?' class=\"on\"':'')",
     "((stVal(h.id)||h.status)===s?' class=\"on\"':'')")
swap("  if(STATUS[h.id]==='top') return '#c25a2b';\n"
     "  if(VISITS[h.id]) return '#7b3fb5';",
     "  if(stVal(h.id)==='top') return '#c25a2b';\n"
     "  if(isFav(h.id)) return '#c9a227';\n"
     "  if(vTime(h.id)) return '#7b3fb5';")
swap("      return {h:HOUSES.filter(function(x){return String(x.id)===String(id);})[0], t:VISITS[id]};",
     "      return {h:HOUSES.filter(function(x){return String(x.id)===String(id);})[0],"
     " t:vTime(id), by:vBy(id)};")
swap("  var ids=Object.keys(VISITS).filter(function(k){return VISITS[k];});",
     "  var ids=Object.keys(VISITS).filter(function(k){return vTime(k);});")
swap("""        (it.h.agent_phone?'<a href="tel:+351'+it.h.agent_phone+'">&#9742;</a>':'')+""",
     """        (it.by?'<span class="who2">'+it.by+'</span>':'')+
        (it.h.agent_phone?'<a href="tel:+351'+it.h.agent_phone+'">&#9742;</a>':'')+""")
swap("""(VISITS[h.id]?'<div class="m">визит '+VISITS[h.id].replace('T',' ')+'</div>':'')+""",
     """(vTime(h.id)?'<div class="m">визит '+vTime(h.id).replace('T',' ')+
          (vBy(h.id)?' · '+vBy(h.id):'')+'</div>':'')+""")
swap("""   '<input type="datetime-local" data-visit="'+h.id+'" value="'+(VISITS[h.id]||'')+'">'+
   (VISITS[h.id]?'<button class="clr" data-clr="'+h.id+'">x</button>':'')+'</div>'+""",
     """   '<input type="datetime-local" data-visit="'+h.id+'" value="'+(vTime(h.id)||'')+'">'+
   (vTime(h.id)?'<button class="clr" data-clr="'+h.id+'">x</button>':'')+
   (vBy(h.id)?'<span class="vby">'+vBy(h.id)+'</span>':'')+'</div>'+""")

# ---- writing a status or a visit records the author -----------------------
swap("   if(vi.value){ VISITS[id]=vi.value; STATUS[id]='marcado'; } else { delete VISITS[id]; }\n"
     "   soil('v',id); soil('s',id);",
     "   if(vi.value){ setVisit(id,vi.value); setStatus(id,'marcado'); }\n"
     "   else { delete VISITS[id]; soil('v',id); }")
swap("   STATUS[id]=s.dataset.st; soil('s',id); await push();",
     "   setStatus(id,s.dataset.st); await push();")
swap("   const h=HOUSES.find(x=>x.id===id); if(h)h.status=s.dataset.st;",
     "   const h=HOUSES.find(x=>x.id===id); if(h)h.status=s.dataset.st;")

# ---- who set it, on the card ----------------------------------------------
swap("""  '<div class="st">'+['escrito','ligado','espera','resposta','marcado','visto','top','arquivo']""",
     """  (stBy(h.id)?'<div class="stby">'+(ST_SHORT[stVal(h.id)]||stVal(h.id))+
     ' · <b>'+stBy(h.id)+'</b>'+(stAt(h.id)?' · '+stAt(h.id).slice(5,10):'')+'</div>':'')+
  '<div class="st">'+['escrito','ligado','espera','resposta','marcado','visto','top','arquivo']""")

# ---- a star of your own ---------------------------------------------------
swap("""   '<span class="ref">#'+h.id+'</span></div>'+""",
     """   '<button class="fav'+(isFav(h.id)?' on':'')+'" data-fav="'+h.id+'" '+
     'title="моё избранное">★</button>'+
   (favOwners(h.id).filter(function(u){return u!==me;}).length?
     '<span class="favo">'+favOwners(h.id).filter(function(u){return u!==me;})
       .join(', ')+'</span>':'')+
   '<span class="ref">#'+h.id+'</span></div>'+""")

# ---- who is working on what ----------------------------------------------
swap("function renderStBar(){\n  migrateStatus();",
     """function renderPeople(){
  const box=document.getElementById('people');
  if(!box) return;
  const n={};
  Object.keys(STATUS).forEach(function(id){
    const by=stBy(id); if(by) n[by]=(n[by]||0)+1;
  });
  const mine=favList().length;
  let html='<button data-f="fav"'+(filt==='fav'?' class="on"':'')+'>★ мои'+
    '<span class="n">'+mine+'</span></button>';
  const others=Object.keys(FAVS).filter(function(u){return u!==me&&favList(u).length;});
  if(others.length) html+='<button data-f="favall"'+(filt==='favall'?' class="on"':'')+
    '>★ все избранные<span class="n">'+
    new Set(Object.keys(FAVS).flatMap(function(u){return favList(u);})).size+'</span></button>';
  Object.keys(n).sort().forEach(function(u){
    html+='<button data-f="by:'+u+'"'+(filt==='by:'+u?' class="on"':'')+'>'+u+
      '<span class="n">'+n[u]+'</span></button>';
  });
  box.innerHTML=html;
}
function renderStBar(){
  migrateStatus();
  renderPeople();""")

swap('<div class="stbar" id="stbar"></div>',
     '<div class="stbar" id="people"></div>\n<div class="stbar" id="stbar"></div>')

# ---- search that also takes a number or an address ------------------------
swap(""" if(q){const hay=[h.concelho,h.freguesia,h.district,h.agency_name].filter(Boolean).join(' ');
  if(!matches(hay,q))return false;}""",
     """ if(q){
  const num=q.replace(/[^\\d]/g,'');
  if(num.length>=3){
    const hit=String(h.id)===num||String(Math.round(h.price_eur||0)).startsWith(num)||
      (h.url||'').includes(num);
    if(hit) return true;
  }
  const hay=[h.concelho,h.freguesia,h.district,h.agency_name,h.address,h.url]
    .filter(Boolean).join(' ');
  if(!matches(hay,q))return false;}""")
swap('placeholder="город, агентство…"', 'placeholder="город, адрес, №, цена…"')

# ---- click handlers -------------------------------------------------------
swap(" const cl=e.target.closest('[data-clr]');",
     " const fv=e.target.closest('[data-fav]');\n"
     " if(fv){ toggleFav(fv.dataset.fav); render(); await push(); mark();\n"
     "   toast(isFav(fv.dataset.fav)?'В избранном':'Убрано из избранного'); return; }\n"
     " const cl=e.target.closest('[data-clr]');")

# ---- styles ---------------------------------------------------------------
swap(".stbar button.zero{opacity:.45}",
     """.stbar button.zero{opacity:.45}
#people button{border-color:var(--gold)}
#people button.on{background:var(--gold);border-color:var(--gold);color:#fff}
.fav{padding:2px 9px;font-size:15px;line-height:1.2;border-color:var(--line);
 color:var(--soft);background:transparent}
.fav.on{background:var(--gold);border-color:var(--gold);color:#fff}
.favo{font-size:11px;color:var(--gold)}
.stby{font-size:12px;color:var(--soft)}
.stby b{color:var(--accent)}
.vby{font-size:11.5px;color:var(--soft)}
.who2{font-size:12px;color:var(--soft);margin-left:6px}""")

p.write_text(s, encoding="utf-8")
print("people, favourites and richer search added")
