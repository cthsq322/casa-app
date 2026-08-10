"""Say which numbers can take a WhatsApp message.

Milena wrote "нету номера чтобы писать ватсап" against a listing showing
+351 221 140 347 - a Porto landline. The card gave no way to know that, and
80 of the 143 listings with a phone have only landlines. That is half the
list where writing is not an option at all, and the app was letting people
find that out the slow way.

Portuguese mobiles start with 9; anything else is fixed. Mobiles come first,
each is labelled, and WhatsApp is offered only where it can actually arrive.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    assert old in s, "NOT FOUND: " + old[:110]
    s = s.replace(old, new, 1)


# ---- knowing one from the other -------------------------------------------
swap("function telHref(raw){",
     """function digits9(raw){
  const d=String(raw).replace(/[^0-9]/g,'');
  return d.length>9?d.slice(-9):d;
}
function isMobile(raw){ return digits9(raw).startsWith('9'); }
function telList(raw){
  // mobiles first - they are the ones you can write to
  return String(raw).split(';').map(function(t){return t.trim();}).filter(Boolean)
    .sort(function(a,b){ return (isMobile(b)?1:0)-(isMobile(a)?1:0); });
}
function waLink(raw){ return 'https://wa.me/351'+digits9(raw); }
function telHref(raw){""")

# ---- the chips ------------------------------------------------------------
swap("""  (h.agent_phone?'<div class="tels">'+
    String(h.agent_phone).split(';').map(function(t){ return t.trim(); })
      .filter(Boolean).slice(0,3).map(function(t){
        return '<button class="tel" data-tel="'+t+'">'+prettyTel(t)+
               '<span class="cp">копировать</span></button>';
      }).join('')+'</div>':'')+""",
     """  (h.agent_phone?'<div class="tels">'+
    telList(h.agent_phone).slice(0,3).map(function(t){
      const m=isMobile(t);
      return '<div class="telrow">'+
        '<button class="tel'+(m?'':' fixed')+'" data-tel="'+t+'">'+prettyTel(t)+
          '<span class="cp">'+(m?'моб':'стац')+'</span></button>'+
        (m?'<a class="wa" href="'+waLink(t)+'" target="_blank" rel="noopener">WhatsApp</a>':'')+
        '</div>';
    }).join('')+
    (telList(h.agent_phone).every(function(t){return !isMobile(t);})
      ? '<div class="onlyfix">только стационарный — WhatsApp не дойдёт, звонить</div>'
      : '')+
    '</div>':'')+""")

# the old WhatsApp button duplicated what the chips now do
swap("""   (h.whatsapp?'<a href="'+h.whatsapp+'" target="_blank" rel="noopener">WhatsApp</a>':'')+""",
     "")

# ---- a place to see them all ----------------------------------------------
swap(" if(filt==='planned'&&!vTime(h.id))return false;",
     " if(filt==='planned'&&!vTime(h.id))return false;\n"
     " if(filt==='wa'&&!(h.agent_phone&&telList(h.agent_phone).some(isMobile)))return false;")

swap('  <button data-f="planned">📅 С датой</button>',
     '  <button data-f="planned">📅 С датой</button>\n'
     '  <button data-f="wa">💬 Можно писать</button>')

# ---- styles ---------------------------------------------------------------
swap(".tels{display:flex;flex-wrap:wrap;gap:6px}",
     """.tels{display:flex;flex-direction:column;gap:6px}
.telrow{display:flex;gap:6px;align-items:stretch}
.telrow .tel{flex:1}
.wa{display:flex;align-items:center;text-decoration:none;font-size:13.5px;
 padding:0 14px;border-radius:9px;border:1px solid var(--accent);
 background:var(--accent);color:var(--paper);font-weight:600;white-space:nowrap}
.tel.fixed{border-style:dashed;border-color:var(--line);background:transparent;
 color:var(--ink);font-weight:400}
.tel.fixed .cp{color:var(--soft)}
.onlyfix{font-size:12px;color:var(--warn)}""")

p.write_text(s, encoding="utf-8")
print("mobile vs landline, WhatsApp only where it lands")
