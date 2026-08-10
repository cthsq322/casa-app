"""The same house, wherever you are looking at it.

Route and My Day were showing summary rows: a time, a town, a price. Fine to
read, useless to work with - no photo, no note, no way to change the number or
the hour without going back to the list. Every view now carries the full card
under its line, exactly as the main list does, so anything can be changed
where it is seen.

The upcoming banner also folds away: it is loud on purpose, but once you have
read it three times it is only in the way.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    assert old in s, "NOT FOUND: " + old[:110]
    s = s.replace(old, new, 1)


# ---- the banner can be folded --------------------------------------------
swap("""  box.className='soon on';""",
     """  box.className='soon on'+(localStorage.getItem('casa_soon_off')==='1'?' folded':'');""")

swap("""  box.innerHTML=items.map(function(it){""",
     """  box.innerHTML='<button class="soonx" id="soonx">'+
    (localStorage.getItem('casa_soon_off')==='1'?'показать':'свернуть')+'</button>'+
    items.map(function(it){""")

swap(" const dn=e.target.closest('[data-day]');",
     """ if(e.target.id==='soonx'){
   const off=localStorage.getItem('casa_soon_off')==='1';
   localStorage.setItem('casa_soon_off', off?'0':'1');
   renderSoon(); return;
 }
 const dn=e.target.closest('[data-day]');""")

# ---- the route carries the house, not a summary of it --------------------
swap("""      html+='<div class="stop'+(tight?' tight':'')+'">'+""",
     """      var full=HOUSES.filter(function(x){return String(x.id)===String(it.h.id);})[0];
      html+='<div class="stop'+(tight?' tight':'')+'">'+""")

swap("""        '</div>';
    });
    html+='</div>';
  });
  box.innerHTML=html;""",
     """        '</div>';
      if(full) html+='<div class="incard">'+card(full)+'</div>';
    });
    html+='</div>';
  });
  box.innerHTML=html;""")

# ---- and so does the day -------------------------------------------------
swap("""        '</div></div>';
    });
    html+='<div class="daysum">за рулём между домами <b>'+""",
     """        '</div></div>';
      const fullh=HOUSES.filter(function(x){return String(x.id)===String(it.h.id);})[0];
      if(fullh) html+='<div class="incard">'+card(fullh)+'</div>';
    });
    html+='<div class="daysum">за рулём между домами <b>'+""")

# ---- and the waiting list, so it can be worked from there ---------------
swap("""      waiting.slice(0,12).map(function(h){
        return '<div class="dw">'+(h.concelho||'?')+' · '+eur(h.price_eur)+""",
     """      waiting.slice(0,8).map(function(h){
        return '<div class="dw">'+(h.concelho||'?')+' · '+eur(h.price_eur)+""")

swap("""          '</div>';
      }).join('')+
      (waiting.length>12?'<div class="dw">…и ещё '+(waiting.length-12)+'</div>':'')+""",
     """          '</div>'+'<div class="incard">'+card(h)+'</div>';
      }).join('')+
      (waiting.length>8?'<div class="dw">…и ещё '+(waiting.length-8)+'</div>':'')+""")

swap(".soon .s1{padding:2px 0}",
     """.soon .s1{padding:2px 0}
.soon.folded .s1{display:none}
.soonx{float:right;margin:-4px -4px 0 8px;padding:3px 10px;font-size:11.5px;
 background:transparent;border-color:var(--warn);color:var(--warn)}
.incard{margin:0 0 4px}
.incard .card{border-radius:0;border-left:0;border-right:0;box-shadow:none;margin:0}
.incard .shot{border-radius:0}""")

p.write_text(s, encoding="utf-8")
print("карточки во всех вкладках, баннер сворачивается")
