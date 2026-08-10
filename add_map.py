"""Add a real map view to the app.

Every house with coordinates gets a pin coloured by what we already decided
about it - tier, status, or a description blocker. Tapping a pin gives the
price, the phone and the link, so the map alone is enough to plan a day.

Leaflet is pulled from a CDN on first open only; the list stays usable if the
map never loads.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")

# ---- chip + container -----------------------------------------------------
s = s.replace('<button data-f="rota">🗺 Rota</button>',
              '<button data-f="rota">🗺 Rota</button><button data-f="mapa">📍 Mapa</button>')

s = s.replace('<div id="rota"></div>',
              '<div id="rota"></div><div id="mapbox"></div>')

s = s.replace(
    ".links{display:flex;",
    "#mapbox{display:none;height:68vh;min-height:340px;border:1px solid var(--line);"
    "border-radius:14px;overflow:hidden;margin:10px 0 4px;background:var(--card)}\n"
    "#mapbox.on{display:block}\n"
    ".leaflet-popup-content{margin:11px 13px;font:14px/1.45 -apple-system,sans-serif}\n"
    ".pp b{font-size:15px}\n"
    ".pp a{color:var(--accent);text-decoration:none;display:inline-block;margin-top:5px}\n"
    ".pp .m{color:#666;font-size:12.5px}\n"
    ".links{display:flex;")

# ---- map code -------------------------------------------------------------
MAP_JS = r"""
var MAP=null, LAYER=null, LEAFLET=false;
function loadLeaflet(cb){
  if(LEAFLET) return cb();
  var css=document.createElement('link');
  css.rel='stylesheet'; css.href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
  document.head.appendChild(css);
  var js=document.createElement('script');
  js.src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
  js.onload=function(){LEAFLET=true;cb();};
  js.onerror=function(){toast('Mapa nao carregou',true);};
  document.head.appendChild(js);
}
function pinColour(h){
  if(STATUS[h.id]==='top') return '#c25a2b';
  if(VISITS[h.id]) return '#7b3fb5';
  if(h.desc_blockers) return '#b03a3a';
  var t=(NOTES[h.id]||[]).filter(function(n){return n.author===me&&n.tier;})[0];
  if(t&&t.tier>=3) return '#2e6b4f';
  return '#5a7f9c';
}
function renderMapa(list){
  var box=document.getElementById('mapbox');
  if(filt!=='mapa'){ box.classList.remove('on'); return; }
  box.classList.add('on');
  loadLeaflet(function(){
    if(!MAP){
      MAP=L.map(box,{scrollWheelZoom:true}).setView([39.9,-8.4],8);
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        {maxZoom:18,attribution:'&copy; OpenStreetMap'}).addTo(MAP);
    }
    if(LAYER) MAP.removeLayer(LAYER);
    var pts=[];
    LAYER=L.layerGroup(list.filter(function(h){return h.lat;}).map(function(h){
      pts.push([h.lat,h.lon]);
      var m=L.circleMarker([h.lat,h.lon],{radius:8,weight:2,color:'#fff',
        fillColor:pinColour(h),fillOpacity:.95});
      var det=[];
      if(h.bedrooms) det.push('T'+h.bedrooms);
      if(h.land_area_m2) det.push('terreno '+new Intl.NumberFormat('pt-PT').format(h.land_area_m2)+' m²');
      if(h.elevation_m) det.push(Math.round(h.elevation_m)+' m alt.');
      m.bindPopup('<div class="pp"><b>'+(h.concelho||'?')+'</b> &middot; '+eur(h.price_eur)+
        '<div class="m">'+det.join(' &middot; ')+'</div>'+
        (VISITS[h.id]?'<div class="m">visita '+VISITS[h.id].replace('T',' ')+'</div>':'')+
        '<a href="'+h.url+'" target="_blank" rel="noopener">ver anúncio</a>'+
        (h.agent_phone?' &nbsp; <a href="tel:+351'+h.agent_phone+'">ligar</a>':'')+
        ' &nbsp; <a href="https://www.google.com/maps/search/?api=1&query='+h.lat+','+h.lon+
        '" target="_blank" rel="noopener">rota</a></div>');
      return m;
    })).addTo(MAP);
    if(pts.length){ MAP.fitBounds(pts,{padding:[30,30],maxZoom:12}); }
    setTimeout(function(){MAP.invalidateSize();},80);
  });
}
"""
s = s.replace("function render(){", MAP_JS + "\nfunction render(){")

# map mode shows pins instead of cards
s = s.replace(" document.getElementById('grid').innerHTML=list.map(card).join('');\n renderRota();",
              " document.getElementById('grid').innerHTML="
              "(filt==='mapa'?'':list.map(card).join(''));\n"
              " renderRota(); renderMapa(list);")

# 'mapa' keeps every house that has a coordinate
s = s.replace(" if(filt==='rota'&&!VISITS[h.id])return false;",
              " if(filt==='rota'&&!VISITS[h.id])return false;\n"
              " if(filt==='mapa'&&!h.lat)return false;")

p.write_text(s, encoding="utf-8")
print(f"map added, {len(s)//1024} KB")
