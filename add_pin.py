"""Keep the exact spot the agent sent.

Our coordinate comes from the listing and is often the village, not the gate.
When an agent sends a Google Maps pin, that is the real place - so it can be
pasted onto the house and from then on the map button, the route and the day
plan all use it.

A long Maps link carries the coordinates inside it and they are read out at
once. A short goo.gl link does not - it only redirects - so the link is kept
as it is and opens correctly, and the coordinates get filled in on the next
rebuild, when the machine can follow the redirect.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    assert old in s, "NOT FOUND: " + old[:110]
    s = s.replace(old, new, 1)


# ---- state ---------------------------------------------------------------
swap("let FAVS={}, REMIND={}, SKIP={};",
     """let FAVS={}, REMIND={}, SKIP={}, PINS={};
function pinOf(id){ return PINS[id]||null; }
function pinPos(h){
  const p=PINS[h.id];
  if(p&&p.lat) return [p.lat,p.lon];
  if(h.lat) return [h.lat,h.lon];
  if(h.town_lat) return [h.town_lat,h.town_lon];
  return null;
}
// a long Maps link carries the point; a short one only redirects
function coordsFrom(text){
  const t=String(text||'');
  let m=t.match(/@(-?\\d+\\.\\d+),(-?\\d+\\.\\d+)/)
     || t.match(/[?&](?:q|ll|daddr|destination)=(-?\\d+\\.\\d+),(-?\\d+\\.\\d+)/)
     || t.match(/!3d(-?\\d+\\.\\d+)!4d(-?\\d+\\.\\d+)/)
     || t.match(/^\\s*(-?\\d+\\.\\d+)\\s*,\\s*(-?\\d+\\.\\d+)\\s*$/);
  if(!m) return null;
  const la=parseFloat(m[1]), lo=parseFloat(m[2]);
  // it has to be in mainland Portugal, or it is not a house of ours
  if(la<36.9||la>42.2||lo<-9.7||lo>-6.0) return null;
  return [la,lo];
}
function setPin(id,text){
  const c=coordsFrom(text);
  if(!text.trim()){ delete PINS[id]; }
  else PINS[id]={url:text.trim(), lat:c?c[0]:null, lon:c?c[1]:null,
                 by:me, at:stamp()};
  soil('p',id);
}""")

swap("    SKIP=mergeMap(d.skip,SKIP,'k');",
     "    SKIP=mergeMap(d.skip,SKIP,'k');\n    PINS=mergeMap(d.pins,PINS,'p');")
swap("                skip:dropDeleted(cur.skip,SKIP,'k'),v:1};",
     "                skip:dropDeleted(cur.skip,SKIP,'k'),\n"
     "                pins:dropDeleted(cur.pins,PINS,'p'),v:1};")
swap("FAVS=body.favs||{}; REMIND=body.remind||{}; SKIP=body.skip||{};",
     "FAVS=body.favs||{}; REMIND=body.remind||{}; SKIP=body.skip||{}; PINS=body.pins||{};")
swap("  localStorage.setItem('casa_skip',JSON.stringify(SKIP));",
     "  localStorage.setItem('casa_skip',JSON.stringify(SKIP));\n"
     "  localStorage.setItem('casa_pins',JSON.stringify(PINS));")
swap("    SKIP=JSON.parse(localStorage.getItem('casa_skip')||'{}');",
     "    SKIP=JSON.parse(localStorage.getItem('casa_skip')||'{}');\n"
     "    PINS=JSON.parse(localStorage.getItem('casa_pins')||'{}');")

# ---- the field, under the visit ------------------------------------------
swap("""  '<div class="visit"><span class="vl">напомнить</span>'+""",
     """  '<div class="visit pinrow"><span class="vl">место</span>'+
   '<input type="text" inputmode="url" data-pin="'+h.id+'" '+
     'placeholder="вставь ссылку с карты от агента" value="'+
     esc((pinOf(h.id)||{}).url||'')+'">'+
   (pinOf(h.id)
     ? '<a class="pinopen" target="_blank" rel="noopener" href="'+
       esc(pinOf(h.id).url)+'">открыть</a>'
     : '')+'</div>'+
  (pinOf(h.id)
    ? '<div class="pinnote'+(pinOf(h.id).lat?' ok':'')+'">'+
      (pinOf(h.id).lat
        ? 'точка от агента · ' + pinOf(h.id).lat.toFixed(5)+', '+pinOf(h.id).lon.toFixed(5)+
          ' · ' + (pinOf(h.id).by||'')
        : 'короткая ссылка — откроется правильно, координаты подставлю при сборке')+
      '</div>'
    : '')+
  '<div class="visit"><span class="vl">напомнить</span>'+""")

swap(" const rm=e.target.closest('[data-remind]');",
     """ const pn=e.target.closest('[data-pin]');
 if(pn){ const id=pn.dataset.pin;
   setPin(id,pn.value);
   const okp=await push(); renderCard(id); mark();
   const c=pinOf(id);
   toast(okp?(c?(c.lat?'Точка сохранена':'Ссылка сохранена'):'Точка убрана')
           :'Сохранено в телефоне',!okp);
   return; }
 const rm=e.target.closest('[data-remind]');""")

# ---- the pin wins wherever a position is used ----------------------------
swap("""   ((h.lat||h.town_lat)
     ? '<a href="https://www.google.com/maps/search/?api=1&query='+
       (h.lat||h.town_lat)+','+(h.lon||h.town_lon)+'" target="_blank" '+
       'rel="noopener" title="где это">📍 Карта</a>'
     : '')+""",
     """   (pinOf(h.id)&&!pinOf(h.id).lat
     ? '<a href="'+esc(pinOf(h.id).url)+'" target="_blank" rel="noopener" '+
       'title="точка от агента">📍 Карта</a>'
     : pinPos(h)
     ? '<a href="https://www.google.com/maps/search/?api=1&query='+
       pinPos(h)[0]+','+pinPos(h)[1]+'" target="_blank" '+
       'rel="noopener" title="где это">📍 Карта</a>'
     : '')+""")

# route pin wiring applied separately

# ---- styles ---------------------------------------------------------------
swap(".visit .clr{padding:5px 11px;font-size:13px}",
     """.visit .clr{padding:5px 11px;font-size:13px}
.pinrow input{font-size:13px}
.pinopen{font-size:12.5px;text-decoration:none;color:var(--accent);
 border:1px solid var(--line);border-radius:8px;padding:6px 11px}
.pinnote{font-size:11.5px;color:var(--warn);margin-top:-3px}
.pinnote.ok{color:var(--accent)}""")

p.write_text(s, encoding="utf-8")
print("agent pins can be pasted and are used everywhere")
