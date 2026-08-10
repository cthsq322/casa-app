"""Show the phone number itself, and let it be copied.

Not every agent gets a call - some get a message, and for that the number has
to go into WhatsApp by hand. The card showed only a "Позвонить" button, so the
digits were never on screen. Now the number is visible, one tap copies it, and
calling and WhatsApp stay where they were.

Some listings carry several numbers; each becomes its own copy button.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    if old not in s:
        raise SystemExit("NOT FOUND: " + old[:110])
    s = s.replace(old, new, 1)


# ---- the numbers, spelled out ---------------------------------------------
swap("""  '<div class="acts">'+
   (h.agent_phone?'<a class="pri" href="tel:+351'+h.agent_phone+'">Позвонить</a>':'')+""",
     """  (h.agent_phone?'<div class="tels">'+
    String(h.agent_phone).split(';').map(function(t){ return t.trim(); })
      .filter(Boolean).slice(0,3).map(function(t){
        return '<button class="tel" data-tel="'+t+'">'+prettyTel(t)+
               '<span class="cp">копировать</span></button>';
      }).join('')+'</div>':'')+
  '<div class="acts">'+
   (h.agent_phone?'<a class="pri" href="tel:'+telHref(h.agent_phone)+'">Позвонить</a>':'')+""")

# ---- formatting and the clipboard -----------------------------------------
swap("function card(h){",
     """function telHref(raw){
  const first=String(raw).split(';')[0].trim().replace(/[^\\d+]/g,'');
  return first.startsWith('+')?first:'+351'+first;
}
function prettyTel(raw){
  const d=String(raw).replace(/[^\\d]/g,'');
  const nine=d.length>9?d.slice(-9):d;                 // drop the country code
  return '+351 '+nine.replace(/(\\d{3})(\\d{3})(\\d{3})/,'$1 $2 $3');
}
function copyText(text){
  if(navigator.clipboard&&window.isSecureContext) return navigator.clipboard.writeText(text);
  return new Promise(function(res,rej){
    const a=document.createElement('textarea');
    a.value=text; a.style.position='fixed'; a.style.opacity='0';
    document.body.appendChild(a); a.select();
    try{ document.execCommand('copy'); res(); }catch(e){ rej(e); }
    document.body.removeChild(a);
  });
}
function card(h){""")

# ---- tapping a number copies it -------------------------------------------
swap(" const fv=e.target.closest('[data-fav]');",
     """ const tl=e.target.closest('[data-tel]');
 if(tl){
   const num=prettyTel(tl.dataset.tel).replace(/\\s/g,'');
   copyText(num).then(function(){
     tl.classList.add('done');
     setTimeout(function(){ tl.classList.remove('done'); },1600);
     toast('Номер скопирован: '+num);
   },function(){ toast('Не получилось скопировать',true); });
   return;
 }
 const fv=e.target.closest('[data-fav]');""")

# ---- styles ---------------------------------------------------------------
swap(".acts{display:flex;gap:7px}",
     """.tels{display:flex;flex-wrap:wrap;gap:6px}
.tel{display:flex;align-items:center;gap:8px;padding:7px 12px;font-size:14.5px;
 font-variant-numeric:tabular-nums;border-radius:9px;border:1px dashed var(--line);
 background:transparent;color:var(--ink)}
.tel .cp{font-size:11px;letter-spacing:.04em;text-transform:uppercase;color:var(--soft)}
.tel.done{border-style:solid;border-color:var(--accent);color:var(--accent)}
.tel.done .cp{color:var(--accent)}
.tel.done .cp:after{content:' ✓'}
.acts{display:flex;gap:7px}""")

p.write_text(s, encoding="utf-8")
print("phone numbers are visible and copyable")
