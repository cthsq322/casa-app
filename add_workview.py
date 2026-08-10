"""Rebuild the filter row around the work, not around the houses.

Земля 3000+, На возвышенности, Без соседей answered questions about the
property - and the sort menu already answers those, better, with a number
instead of a yes/no. What the row could not answer was the question actually
asked all day: what have I touched, what has nobody touched yet.

The account button says выйти now, and next to it sits what that account has
done, so switching between people shows each one's own trail.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    if old not in s:
        raise SystemExit("NOT FOUND: " + old[:110])
    s = s.replace(old, new, 1)


# ---- the row -------------------------------------------------------------
swap("""  <button data-f="all" class="on">Все</button>
  <button data-f="big">Земля 3000+</button>
  <button data-f="high">На возвышенности</button>
  <button data-f="alone">Без соседей</button>
  <button data-f="mine">С заметками</button>
  <button data-f="flag">⚠ Проблемы</button><button data-f="rota">🗺 Маршрут</button><button data-f="mapa">📍 Карта</button>""",
     """  <button data-f="all" class="on">Все</button>
  <button data-f="work">🖐 Моя работа</button>
  <button data-f="fresh">Не тронутые</button>
  <button data-f="mine">С заметками</button>
  <button data-f="flag">⚠ Проблемы</button><button data-f="rota">🗺 Маршрут</button><button data-f="mapa">📍 Карта</button>""")

# the old three stay reachable by sorting, so the filters can go
swap(""" if(filt==='big'&&!(h.land_area_m2>=3000))return false;
 if(filt==='high'&&!(h.elevation_relative_m>30))return false;
 if(filt==='alone'&&!(h.nearest_building_m>=150))return false;
 if(filt==='mine'&&!(NOTES[h.id]||[]).length)return false;""",
     """ if(filt==='mine'&&!(NOTES[h.id]||[]).length)return false;
 if(filt==='work'&&!touchedBy(h.id,me))return false;
 if(filt==='fresh'&&(stVal(h.id)||(NOTES[h.id]||[]).length||vTime(h.id)))return false;""")

# ---- what counts as my work ----------------------------------------------
swap("function keep(h){",
     """function touchedBy(id,who){
  return stBy(id)===who
      || vBy(id)===who
      || (NOTES[id]||[]).some(function(n){ return n.author===who; })
      || isFav(id,who);
}
function myWork(who){
  return HOUSES.filter(function(h){ return touchedBy(h.id,who); });
}
function keep(h){""")

# ---- the account line -----------------------------------------------------
swap('<button id="swap">сменить</button>', '<button id="swap">выйти</button>')

swap("function renderProgress(){",
     """function renderMine(){
  const box=document.getElementById('mine');
  if(!box||!HOUSES.length) return;
  const mine=myWork(me);
  const notes=mine.filter(function(h){
    return (NOTES[h.id]||[]).some(function(n){return n.author===me;}); }).length;
  const st=mine.filter(function(h){ return stBy(h.id)===me; }).length;
  const vis=mine.filter(function(h){ return vBy(h.id)===me; }).length;
  const fav=favList(me).length;
  if(!mine.length){
    box.innerHTML='<span class="empty">'+me+': пока ничего не отмечено</span>';
    return;
  }
  box.innerHTML='<b>'+me+'</b> вёл <b>'+mine.length+'</b> '+
    (mine.length===1?'дом':'домов')+
    (st?' · статусов <b>'+st+'</b>':'')+
    (notes?' · заметок <b>'+notes+'</b>':'')+
    (vis?' · визитов <b>'+vis+'</b>':'')+
    (fav?' · в избранном <b>'+fav+'</b>':'');
}
function renderProgress(){""")

swap("  renderPeople();\n  renderProgress();",
     "  renderPeople();\n  renderProgress();\n  renderMine();")

swap('<div class="prog" id="prog"></div>',
     '<div class="mine" id="mine"></div>\n<div class="prog" id="prog"></div>')

# ---- styles ---------------------------------------------------------------
swap(".prog{margin:12px 0 2px;font-size:13.5px;color:var(--soft)}",
     """.mine{margin:11px 0 0;font-size:13.5px;color:var(--soft)}
.mine b{color:var(--ink);font-variant-numeric:tabular-nums}
.mine .empty{font-style:italic}
.prog{margin:8px 0 2px;font-size:13.5px;color:var(--soft)}""")

p.write_text(s, encoding="utf-8")
print("work-oriented filters + per-account trail")
