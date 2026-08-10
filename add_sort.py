"""Add sorting and the score badge to the app.

Serhii wants to reorder the same list by whatever he is thinking about at that
moment - price, land, rooms, how high it sits, or our own score. Missing values
always sink to the bottom instead of pretending to be zero.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")

# ---- control --------------------------------------------------------------
s = s.replace(
    '<input id="q" type="search" placeholder="concelho, agência…">',
    '<select id="sort" title="ordenar">'
    '<option value="score">Nota &darr;</option>'
    '<option value="tier">N&iacute;vel &starf; &darr;</option>'
    '<option value="land">Terreno &darr;</option>'
    '<option value="price">Pre&ccedil;o &uarr;</option>'
    '<option value="price_d">Pre&ccedil;o &darr;</option>'
    '<option value="ppm">&euro;/m&sup2; &uarr;</option>'
    '<option value="area">&Aacute;rea da casa &darr;</option>'
    '<option value="rooms">Quartos &darr;</option>'
    '<option value="wc">Casas de banho &darr;</option>'
    '<option value="alt">Altitude &darr;</option>'
    '<option value="alone">Longe de vizinhos &darr;</option>'
    '</select>'
    '<input id="q" type="search" placeholder="concelho, agência…">')

s = s.replace(
    "select{font:inherit;",
    "select{font:inherit;")  # no-op guard if a rule already exists
s = s.replace(
    "input[type=search]{font:inherit;",
    "select#sort{font:inherit;font-size:14px;padding:7px 11px;border:1px solid var(--line);"
    "border-radius:999px;background:var(--card);color:var(--ink);max-width:100%}\n"
    ".nota{margin-left:8px;font:600 12.5px/1 -apple-system,sans-serif;padding:4px 8px;"
    "border-radius:999px;background:var(--accent-s);color:var(--accent);"
    "font-variant-numeric:tabular-nums}\n"
    ".nota.thin{background:transparent;border:1px solid var(--line);color:var(--soft)}\n"
    "input[type=search]{font:inherit;")

# ---- state ----------------------------------------------------------------
s = s.replace("let HOUSES=[],NOTES={},STATUS={},VISITS={},filt='all'",
              "let HOUSES=[],NOTES={},STATUS={},VISITS={},"
              "sortBy=localStorage.getItem('casa_sort')||'score',filt='all'")

# ---- sorting --------------------------------------------------------------
SORT_JS = r"""
function myTier(h){
  var n=(NOTES[h.id]||[]).filter(function(x){return x.author===me;})[0];
  return n&&n.tier?n.tier:0;
}
var SORTS={
  score : [function(h){return h.auto_score;},        -1],
  tier  : [function(h){return myTier(h)||null;},     -1],
  land  : [function(h){return h.land_area_m2;},      -1],
  price : [function(h){return h.price_eur;},          1],
  price_d:[function(h){return h.price_eur;},         -1],
  ppm   : [function(h){return h.price_per_m2;},       1],
  area  : [function(h){return h.area_m2;},           -1],
  rooms : [function(h){return h.bedrooms;},          -1],
  wc    : [function(h){return h.bathrooms;},         -1],
  alt   : [function(h){return h.elevation_m;},       -1],
  alone : [function(h){return h.nearest_building_m;},-1]
};
function sortList(list){
  var s=SORTS[sortBy]||SORTS.score, get=s[0], dir=s[1];
  return list.slice().sort(function(a,b){
    var x=get(a), y=get(b);
    // anything we do not know goes to the bottom, whichever way we are sorting
    if(x==null&&y==null) return (b.auto_score||0)-(a.auto_score||0);
    if(x==null) return 1;
    if(y==null) return -1;
    if(x===y) return (b.auto_score||0)-(a.auto_score||0);
    return (x-y)*dir;
  });
}
"""
s = s.replace("function render(){", SORT_JS + "\nfunction render(){")

s = s.replace(" const list=HOUSES.filter(keep);",
              " const list=sortList(HOUSES.filter(keep));")

# ---- score badge on the card ---------------------------------------------
s = s.replace(
    """'<div class="top"><span class="price">'+eur(h.price_eur)+'</span><span class="ref">#'+h.id+'</span></div>'+""",
    """'<div class="top"><span class="price">'+eur(h.price_eur)+'</span>'+
   (h.auto_score!=null?'<span class="nota'+(h.score_parts<5?' thin':'')+
     '" title="'+h.score_parts+' de 7 critérios conhecidos">'+h.auto_score+'</span>':'')+
   '<span class="ref">#'+h.id+'</span></div>'+""")

# ---- handler --------------------------------------------------------------
s = s.replace(
    "document.getElementById('q').addEventListener('input'",
    "document.getElementById('sort').addEventListener('change',function(e){\n"
    " sortBy=e.target.value; localStorage.setItem('casa_sort',sortBy); render();\n"
    "});\n"
    "document.getElementById('sort').value="
    "localStorage.getItem('casa_sort')||'score';\n"
    "document.getElementById('q').addEventListener('input'")

p.write_text(s, encoding="utf-8")
print(f"sort added, {len(s)//1024} KB")
