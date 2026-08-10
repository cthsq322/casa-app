"""Put a picture on the card, and let the link be copied.

Serhii looks at a list of 164 towns and prices and cannot tell which house is
which - a single photo does more for that than any number on the card. Where
we have no photo, the card says so plainly instead of leaving a grey hole.

The listing link also gets a copy button: he forwards these to people all day,
and opening the ad just to copy the address from the browser bar is silly.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    if old not in s:
        raise SystemExit("NOT FOUND: " + old[:110])
    s = s.replace(old, new, 1)


# ---- the photo ------------------------------------------------------------
swap("""  '<div class="place">""",
     """  (h.first_photo_url
    ? '<a class="shot" href="'+h.url+'" target="_blank" rel="noopener">'+
        '<img src="'+h.first_photo_url+'" alt="" loading="lazy" decoding="async" '+
        'onerror="this.closest(\\'.shot\\').classList.add(\\'broken\\')">'+
        (h.photo_count?'<span class="cnt">'+h.photo_count+' фото</span>':'')+
      '</a>'
    : '<div class="shot none">нет фото — открой объявление</div>')+
  '<div class="place">""")

# ---- copy the link --------------------------------------------------------
swap("""   '<a href="'+h.url+'" target="_blank" rel="noopener">Объявление</a></div>'+""",
     """   '<a href="'+h.url+'" target="_blank" rel="noopener">Объявление</a>'+
   '<button class="lnk" data-link="'+h.id+'" title="скопировать ссылку">🔗</button></div>'+""")

swap(" const tl=e.target.closest('[data-tel]');",
     """ const lk=e.target.closest('[data-link]');
 if(lk){
   const h=HOUSES.find(function(x){return String(x.id)===String(lk.dataset.link);});
   if(h) copyText(h.url).then(function(){
     lk.classList.add('done');
     setTimeout(function(){ lk.classList.remove('done'); },1600);
     toast('Ссылка скопирована');
   },function(){ toast('Не получилось скопировать',true); });
   return;
 }
 const tl=e.target.closest('[data-tel]');""")

# ---- styles ---------------------------------------------------------------
swap(".top{display:flex;align-items:baseline;gap:9px}",
     """.shot{display:block;position:relative;margin:-15px -16px 0;aspect-ratio:16/10;
 background:var(--accent-s);overflow:hidden;border-radius:14px 14px 0 0}
.shot img{width:100%;height:100%;object-fit:cover;display:block}
.shot .cnt{position:absolute;right:9px;bottom:9px;background:rgba(0,0,0,.55);
 color:#fff;font-size:11.5px;padding:3px 9px;border-radius:999px;
 backdrop-filter:blur(3px)}
.shot.none,.shot.broken{display:flex;align-items:center;justify-content:center;
 aspect-ratio:auto;padding:14px;font-size:12.5px;color:var(--soft);
 background:var(--accent-s);text-align:center}
.shot.broken img,.shot.broken .cnt{display:none}
.shot.broken:before{content:'фото не открылось — смотри объявление'}
.lnk{flex:0 0 auto;padding:8px 13px;border-radius:9px;border:1px solid var(--line);
 background:transparent;font-size:15px;line-height:1.2}
.lnk.done{border-color:var(--accent);color:var(--accent)}
.top{display:flex;align-items:baseline;gap:9px}""")

p.write_text(s, encoding="utf-8")
print("photo + copy link added")
