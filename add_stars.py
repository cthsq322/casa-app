"""Let the stars drive the trip.

Three stars means both of them liked it, two means one did, one means it is
worth the detour. A house with no stars is a side quest - call in if the day
allows, skip it without regret if it does not.

So the map sizes and colours its pins by the highest star anyone gave, the
plan shows them, and a day that runs late drops the starless houses first.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    assert old in s, "NOT FOUND: " + old[:110]
    s = s.replace(old, new, 1)


# ---- the highest star anyone gave ----------------------------------------
swap("function myTier(h){",
     """// three stars means both of them liked it, so the best star wins
function bestTier(id){
  return (NOTES[id]||[]).reduce(function(a,n){
    return Math.max(a, n.tier || 0); }, 0);
}
function tierOwners(id){
  return (NOTES[id]||[]).filter(function(n){ return n.tier; })
    .map(function(n){ return n.author+' '+'★'.repeat(n.tier); });
}
function myTier(h){""")

# ---- the map: a starred house is not the same dot ------------------------
swap("""      var booked=!!vTime(h.id);
      var m=L.circleMarker([h.lat,h.lon],{radius:booked?4:8,weight:booked?1:2,
        color:'#fff',fillColor:pinColour(h),fillOpacity:booked?.35:.95});""",
     """      var booked=!!vTime(h.id);
      var t=bestTier(h.id);
      var r = booked ? 4 : (t===3?13 : t===2?11 : t===1?9 : 6);
      var m=L.circleMarker([h.lat,h.lon],{radius:r,weight:booked?1:(t?3:2),
        color:t?'#fff':'#ffffffcc',fillColor:pinColour(h),
        fillOpacity:booked?.35:(t?1:.6)});""")

swap("""  if(stVal(h.id)==='top') return '#c25a2b';
  if(isFav(h.id)) return '#c9a227';""",
     """  var t=bestTier(h.id);
  if(t===3) return '#b8860b';          // both of us
  if(t===2) return '#c9a227';
  if(t===1) return '#d9c26a';
  if(stVal(h.id)==='top') return '#c25a2b';
  if(isFav(h.id)) return '#c9a227';""")

swap("""      var det=[];
      if(h.bedrooms) det.push('T'+h.bedrooms);""",
     """      var det=[];
      if(bestTier(h.id)) det.push('★'.repeat(bestTier(h.id))+' '+
        tierOwners(h.id).join(', '));
      if(h.bedrooms) det.push('T'+h.bedrooms);""")

# ---- the plan: stars first, starless as a side quest ---------------------
swap("""  const mob = st.phone && telList(st.phone).some(isMobile);
  return '<div class="pstop '+cls+'">'+
    '<b>'+st.at+'</b>'+""",
     """  const mob = st.phone && telList(st.phone).some(isMobile);
  const t = bestTier(st.id);
  return '<div class="pstop '+cls+(t?' star'+t:' nostar')+'">'+
    '<b>'+st.at+'</b>'+
    (t?'<span class="st'+t+'">'+'★'.repeat(t)+'</span>':'')+""")

swap("""    const live=d.stops.filter(function(st){ return !outOfLoop(st.id); });""",
     """    const live=d.stops.filter(function(st){ return !outOfLoop(st.id); });
    const starred=live.filter(function(st){ return bestTier(st.id); }).length;""")

swap("""      ' · '+live.length+' домов'+""",
     """      ' · '+live.length+' домов'+
      (starred?' · <b>'+starred+' со звёздами</b>':'')+""")

# ---- a way to see only what matters --------------------------------------
swap('  <button data-f="skipped">🙅 Вне круга</button>',
     '  <button data-f="skipped">🙅 Вне круга</button>\n'
     '  <button data-f="starred">★ Со звёздами</button>')

swap(" if(filt==='skipped'&&!isSkipped(h.id))return false;",
     " if(filt==='skipped'&&!isSkipped(h.id))return false;\n"
     " if(filt==='starred'&&!bestTier(h.id))return false;")

# ---- the star that someone else gave, on the card ------------------------
swap("""  others.map(n=>'<div class="note other"><b>'+n.author+'</b>""",
     """  (tierOwners(h.id).length>1
    ? '<div class="tiero">'+tierOwners(h.id).join(' · ')+'</div>' : '')+
  others.map(n=>'<div class="note other"><b>'+n.author+'</b>""")

swap(".pstop.ok{background:var(--accent-s)}",
     """.pstop .st1,.pstop .st2,.pstop .st3{color:var(--gold);font-size:12.5px}
.pstop.star3{background:linear-gradient(90deg,rgba(184,134,11,.14),transparent 60%)}
.pstop.star3 b{color:var(--gold)}
.pstop.nostar{opacity:.72}
.tiero{font-size:12px;color:var(--gold)}
.pstop.ok{background:var(--accent-s)}""")

p.write_text(s, encoding="utf-8")
print("stars drive the map and the plan")
