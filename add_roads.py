"""Route by road, not by ruler.

A straight line between two villages in central Portugal is a lie - the road
goes round the hills and takes half again as long. OSRM's public router gives
the real distance, the real driving time and the shape of the road, all
without a key. The line on the map becomes the road you will actually drive.

What matters more than the distance is the answer to "do we make it": between
each pair of visits it now says how much time is left over after the drive,
and says so in red when there is none.

If the router cannot be reached the straight-line estimate is used, and the
card says that is what it is.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    assert old in s, "NOT FOUND: " + old[:110]
    s = s.replace(old, new, 1)


ROADS = r"""
// OSRM's demo router: no key, and it answers with the road itself
const ROADS={};                                  // "lat,lon;lat,lon" -> {km,min,line}
function roadKey(a,b){ return a.lat+','+a.lon+';'+b.lat+','+b.lon; }
async function roadBetween(a,b){
  if(!a.lat||!b.lat) return null;
  const k=roadKey(a,b);
  if(ROADS[k]!==undefined) return ROADS[k];
  ROADS[k]=null;                                 // do not ask twice while in flight
  try{
    const u='https://router.project-osrm.org/route/v1/driving/'+
      a.lon+','+a.lat+';'+b.lon+','+b.lat+'?overview=full&geometries=geojson';
    const r=await fetch(u,{cache:'no-store'});
    if(!r.ok) throw 0;
    const d=await r.json();
    const rt=d.routes&&d.routes[0];
    if(!rt) throw 0;
    ROADS[k]={km:rt.distance/1000, min:rt.duration/60,
              line:rt.geometry.coordinates.map(function(c){return [c[1],c[0]];})};
  }catch(e){ ROADS[k]=false; }                   // false = asked and failed
  return ROADS[k];
}
async function fillRoads(items){
  let got=false;
  for(let i=1;i<items.length;i++){
    const r=await roadBetween(items[i-1].h,items[i].h);
    if(r) got=true;
  }
  return got;
}
function gapWords(min){
  const h=Math.floor(min/60), m=Math.round(min%60);
  return (h?h+' ч ':'')+(m?m+' мин':(h?'':'0 мин'));
}
"""
swap("function fmtDay(v){", ROADS + "\nfunction fmtDay(v){")

# the day list: real road figures, and what is left over
swap("""      var prev=i?list[i-1].h:null;
      var dist=prev?kmBetween(prev,it.h):null;
      var drive=dist!=null?Math.round(dist):null;          // ~60 km/h rural = 1 min per km
      var gap=prev?(new Date(it.t)-new Date(list[i-1].t))/60000:null;
      var tight=(drive!=null&&gap!=null&&gap<drive+30);""",
     """      var prev=i?list[i-1].h:null;
      var road=prev?ROADS[roadKey(prev,it.h)]:null;
      var byRoad=!!road;
      var dist=prev?(byRoad?road.km:kmBetween(prev,it.h)):null;
      var drive=dist!=null?Math.round(byRoad?road.min:dist):null;
      var gap=prev?(new Date(it.t)-new Date(list[i-1].t))/60000:null;
      var spare=(drive!=null&&gap!=null)?gap-drive-45:null;   // 45 min to look round
      var tight=(spare!=null&&spare<0);""")

swap("""        (dist!=null?'<div class="leg">'+Math.round(dist)+' км &middot; ~'+drive+' мин на машине'+
           (tight?' &mdash; мало времени между визитами':'')+'</div>':'')+""",
     """        (dist!=null?'<div class="leg">'+Math.round(dist)+' км &middot; '+drive+
           ' мин за рулём'+(byRoad?' по дороге':' по прямой')+
           (spare!=null?(spare>=0?' &middot; в запасе '+gapWords(spare)
                                : ' &middot; не хватает '+gapWords(-spare)):'')+
           '</div>':'')+""")

# ask the router once the day is on screen, then redraw with real numbers
swap("  box.innerHTML=html;\n}",
     """  box.innerHTML=html;
  var need=[];
  Object.keys(days).forEach(function(d){ need=need.concat(days[d]); });
  fillRoads(need).then(function(got){ if(got&&filt==='rota') renderRota(); });
}""")

# the map draws the road, not a dashed guess
swap("""      if(line.length>1) routeBits.push(L.polyline(line,
        {color:col,weight:3,opacity:.85,dashArray:'7 6'}));""",
     """      for(var q=1;q<stops.length;q++){
        var rd=ROADS[roadKey(stops[q-1].h,stops[q].h)];
        routeBits.push(rd
          ? L.polyline(rd.line,{color:col,weight:4,opacity:.9})
          : L.polyline([[stops[q-1].h.lat,stops[q-1].h.lon],
                        [stops[q].h.lat,stops[q].h.lon]],
              {color:col,weight:3,opacity:.7,dashArray:'7 6'}));
      }""")

swap("""    ROUTE = routeBits.length ? L.layerGroup(routeBits).addTo(MAP) : null;""",
     """    ROUTE = routeBits.length ? L.layerGroup(routeBits).addTo(MAP) : null;
    days.forEach(function(d){
      fillRoads(byDay[d].sort(function(a,b){return a.t.localeCompare(b.t);}))
        .then(function(got){ if(got&&filt==='mapa') renderMapa(list); });
    });""")

swap(".stop.tight{background:var(--warn-s)}",
     ".stop.tight{background:var(--warn-s)}\n"
     ".stop .leg{font-variant-numeric:tabular-nums}")

p.write_text(s, encoding="utf-8")
print("real road routing wired in")
