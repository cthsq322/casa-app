"""Four small things that cost time all day.

A button that opens the house where it stands, so you know what you are
driving to before you drive. Photos that show the house instead of a crop of
its wall. A score that does not shove the star sideways every time it changes
by a digit. And the day of the visit as its own copy button, because it goes
into every message he writes.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new, need=True):
    """Skip what is not there instead of dying halfway through a file."""
    global s
    if old not in s:
        if need:
            print("  пропущено (нет якоря):", old.strip().splitlines()[0][:60])
        return
    s = s.replace(old, new, 1)


# ---- where the house actually stands -------------------------------------
swap("""   '<a href="'+h.url+'" target="_blank" rel="noopener">Объявление</a>'+""",
     """   '<a href="'+h.url+'" target="_blank" rel="noopener">Объявление</a>'+
   ((h.lat||h.town_lat)
     ? '<a href="https://www.google.com/maps/search/?api=1&query='+
       (h.lat||h.town_lat)+','+(h.lon||h.town_lon)+'" target="_blank" '+
       'rel="noopener" title="где это">📍 Карта</a>'
     : '')+""")

# ---- the photo shows the house, not a crop of it -------------------------
swap(".shot img{width:100%;height:100%;object-fit:cover;display:block}",
     ".shot img{width:100%;height:100%;object-fit:cover;object-position:center 42%;\n"
     " display:block}")
swap(".shot{display:block;position:relative;margin:-15px -16px 0;height:clamp(96px,26vw,150px);",
     ".shot{display:block;position:relative;margin:-15px -16px 0;height:clamp(150px,42vw,220px);")

# ---- the score keeps its place -------------------------------------------
swap(".nota{margin-left:8px;font:600 12.5px/1 -apple-system,sans-serif;padding:4px 8px;"
     "border-radius:999px;background:var(--accent-s);color:var(--accent);"
     "font-variant-numeric:tabular-nums}",
     ".nota{margin-left:8px;font:600 12.5px/1 -apple-system,sans-serif;padding:4px 0;\n"
     " width:38px;text-align:center;border-radius:999px;background:var(--accent-s);\n"
     " color:var(--accent);font-variant-numeric:tabular-nums;flex:0 0 auto}")
swap(".fav{padding:2px 9px;font-size:15px;line-height:1.2;border-color:var(--line);",
     ".fav{padding:2px 0;width:34px;text-align:center;flex:0 0 auto;\n"
     " font-size:15px;line-height:1.4;border-color:var(--line);")

# ---- the date, ready to paste --------------------------------------------
swap("""          (DAYOF[h.id].swap&&DAYOF[h.id].swap.length
            ? ' · можно сдвинуть на '+DAYOF[h.id].swap.join(' или ') : '')""",
     """          '<button class="cpday" data-cpday="'+h.id+'">копировать дату</button>'+
          (DAYOF[h.id].swap&&DAYOF[h.id].swap.length
            ? '<span class="swapd">можно сдвинуть на '+
              DAYOF[h.id].swap.join(' или ')+'</span>' : '')""")

swap(" const sk=e.target.closest('[data-skip]');",
     """ const cd=e.target.closest('[data-cpday]');
 if(cd){
   const d=DAYOF[cd.dataset.cpday];
   if(d) copyText(d.when+', '+d.at).then(function(){
     toast('Скопировано: '+d.when+', '+d.at);
   },function(){ toast('Не получилось скопировать',true); });
   return;
 }
 const sk=e.target.closest('[data-skip]');""")

swap(".bday{font-size:12.5px;color:var(--accent);background:var(--accent-s);\n"
     " border-radius:8px;padding:4px 9px;align-self:flex-start}",
     ".bday{font-size:12.5px;color:var(--accent);background:var(--accent-s);\n"
     " border-radius:8px;padding:5px 9px;display:flex;align-items:center;gap:8px;\n"
     " flex-wrap:wrap}\n"
     ".cpday{padding:3px 10px;font-size:11.5px;border-color:var(--accent);\n"
     " color:var(--accent);background:transparent}\n"
     ".swapd{font-size:11.5px;color:var(--soft)}")

p.write_text(s, encoding="utf-8")
print("map button, bigger photos, steady score, copyable date")
