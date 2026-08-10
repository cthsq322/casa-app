"""Where there is no photo, show the place instead of an apology.

26 listings have no picture - supercasa blocks the scrape until the proxy
credits come back. But we know exactly where those houses stand, and a map
answers most of what the photo was for: is it alone, is it in the trees, how
far is the nearest road.

One OpenStreetMap tile, with the house marked at its real position inside it.
No key, no service, the same tiles the map view already loads.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    assert old in s, "NOT FOUND: " + old[:100]
    s = s.replace(old, new, 1)


# ---- one tile, and the house's place inside it ---------------------------
swap("function card(h){",
     """// slippy-map maths: which tile holds this point, and where inside it
function tileFor(lat,lon,z){
  const n=Math.pow(2,z);
  const x=(lon+180)/360*n;
  const r=lat*Math.PI/180;
  const y=(1-Math.log(Math.tan(r)+1/Math.cos(r))/Math.PI)/2*n;
  return {x:Math.floor(x), y:Math.floor(y), z:z,
          dx:(x-Math.floor(x))*100, dy:(y-Math.floor(y))*100};
}
function mapThumb(h){
  if(!h.lat) return '<div class="shot none">нет фото и нет координат</div>';
  const t=tileFor(h.lat,h.lon,14);
  return '<a class="shot tile" href="https://www.google.com/maps/search/?api=1&query='+
    h.lat+','+h.lon+'" target="_blank" rel="noopener">'+
    '<img src="https://tile.openstreetmap.org/'+t.z+'/'+t.x+'/'+t.y+'.png" '+
      'alt="" loading="lazy" decoding="async">'+
    '<span class="pin" style="left:'+t.dx.toFixed(1)+'%;top:'+t.dy.toFixed(1)+'%"></span>'+
    '<span class="cnt">фото нет — вот место</span></a>';
}
function card(h){""")

swap("""    : '<div class="shot none">нет фото — открой объявление</div>')+""",
     """    : mapThumb(h))+""")

# ---- styles ---------------------------------------------------------------
swap(".shot.none,.shot.broken{",
     """.shot.tile{background:#e8e4dc}
.shot.tile img{image-rendering:auto;filter:saturate(.85)}
.shot .pin{position:absolute;width:14px;height:14px;margin:-7px 0 0 -7px;
 border-radius:50%;background:var(--warn);border:2px solid #fff;
 box-shadow:0 1px 4px rgba(0,0,0,.45)}
.shot.none,.shot.broken{""")

p.write_text(s, encoding="utf-8")
print("map tile stands in for a missing photo")
