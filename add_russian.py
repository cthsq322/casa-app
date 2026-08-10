"""Put the interface into Russian, let the search take Cyrillic, drop the clutter.

Serhii and Violeta read the screen in Russian; only the data stays Portuguese,
because that is what the listings and the agents say. The search now also
accepts a Russian spelling - typing "Лейрия" or "Помбал" finds Leiria and
Pombal - by transliterating the query and matching loosely, since nobody spells
a foreign place the same way twice.

The export and import buttons go: they existed before the notes were shared,
and now they are just two more things on a small screen.
"""
import pathlib
import re

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new, count=1, required=True):
    global s
    if old not in s:
        if required:
            raise SystemExit(f"not found: {old[:70]}")
        return
    s = s.replace(old, new, count)


# ---- header ---------------------------------------------------------------
swap("<title>Casa</title>", "<title>Дома</title>")
swap('<h1>Casa</h1><span class="sub" id="sub">', '<h1>Дома</h1><span class="sub" id="sub">')
swap('<button id="swap">trocar</button><button id="exp">↓ notas</button>'
     '<button id="imp">↑ juntar</button>'
     '<input id="impf" type="file" accept="application/json" style="display:none">'
     '<button id="theme">◐</button>',
     '<button id="swap">сменить</button><button id="theme">◐</button>')
swap('  <h2>Casa</h2><p>Quem és?</p>', '  <h2>Дома</h2><p>Кто заходит?</p>')

# the import/export block goes with the buttons
s = re.sub(r"<script>\nfunction dl\(name,txt\).*?</script>", "", s, flags=re.S)

# ---- filters and sorting --------------------------------------------------
for a, b in [
    ('<button data-f="all" class="on">Todos</button>', '<button data-f="all" class="on">Все</button>'),
    ('<button data-f="big">Terreno 3000+</button>', '<button data-f="big">Земля 3000+</button>'),
    ('<button data-f="high">Em altura</button>', '<button data-f="high">На возвышенности</button>'),
    ('<button data-f="alone">Sem vizinhos</button>', '<button data-f="alone">Без соседей</button>'),
    ('<button data-f="mine">Com notas</button>', '<button data-f="mine">С заметками</button>'),
    ('<button data-f="flag">⚠ Alerta</button>', '<button data-f="flag">⚠ Проблемы</button>'),
    ('<button data-f="rota">🗺 Rota</button>', '<button data-f="rota">🗺 Маршрут</button>'),
    ('<button data-f="mapa">📍 Mapa</button>', '<button data-f="mapa">📍 Карта</button>'),
]:
    swap(a, b)

SORT_RU = {
    "Nota &darr;": "Оценка &darr;", "N&iacute;vel &starf; &darr;": "Уровень &starf; &darr;",
    "Terreno &darr;": "Земля &darr;", "Pre&ccedil;o &uarr;": "Цена &uarr;",
    "Pre&ccedil;o &darr;": "Цена &darr;", "&euro;/m&sup2; &uarr;": "&euro;/м&sup2; &uarr;",
    "&Aacute;rea da casa &darr;": "Площадь дома &darr;", "Quartos &darr;": "Комнаты &darr;",
    "Casas de banho &darr;": "Туалеты &darr;", "Altitude &darr;": "Высота &darr;",
    "Longe de vizinhos &darr;": "Дальше от соседей &darr;",
}
for a, b in SORT_RU.items():
    swap(">" + a + "<", ">" + b + "<")

swap('placeholder="concelho, agência…"', 'placeholder="город, агентство…"')
swap('<a href="frases.html">✍ O que escrever</a>', '<a href="frases.html">✍ Что писать</a>')
swap('<a href="lista.html">🔗 Links por site</a>', '<a href="lista.html">🔗 Ссылки по сайтам</a>')

# ---- statuses -------------------------------------------------------------
swap("""const ST_LABELS={escrito:'✍ escrevi',ligado:'☎ liguei',
  espera:'⏳ à espera',resposta:'↩ responderam',marcado:'📅 marcado',
  visto:'👁 já vimos',top:'★ favorita',arquivo:'✕ fora'};
const ST_SHORT={escrito:'escrevi',ligado:'liguei',espera:'à espera',
  resposta:'responderam',marcado:'marcado',visto:'já vimos',
  top:'favorita',arquivo:'fora'};""",
     """const ST_LABELS={escrito:'✍ написал',ligado:'☎ позвонил',
  espera:'⏳ жду',resposta:'↩ ответили',marcado:'📅 договорились',
  visto:'👁 посмотрели',top:'★ фаворит',arquivo:'✕ отпал'};
const ST_SHORT={escrito:'написал',ligado:'позвонил',espera:'жду',
  resposta:'ответили',marcado:'договорились',visto:'посмотрели',
  top:'фаворит',arquivo:'отпал'};""")

# ---- the card -------------------------------------------------------------
swap("""'" title="'+h.score_parts+' de 7 critérios conhecidos">'""",
     """'" title="известно '+h.score_parts+' из 7 критериев">'""")
for a, b in [('<div class="k">terreno m²</div>', '<div class="k">земля м²</div>'),
             ('<div class="k">casa m²</div>', '<div class="k">дом м²</div>'),
             ('<div class="k">quartos</div>', '<div class="k">комнаты</div>'),
             ('<div class="k">wc</div>', '<div class="k">туалеты</div>'),
             ('<div class="k">км Lisboa</div>', '<div class="k">км до Лиссабона</div>')]:
    swap(a, b)
swap(""">Ligar</a>'""", """>Позвонить</a>'""")
swap(""">Anúncio</a></div>'""", """>Объявление</a></div>'""")
swap("""color:var(--soft)">nível</span>'""", """color:var(--soft)">уровень</span>'""")
swap("""placeholder="'+(me||'')+': a tua nota…"'""",
     """placeholder="'+(me||'')+': твоя заметка…"'""", required=False)
swap("""placeholder="'+(me||'')+': a tua nota…">'""",
     """placeholder="'+(me||'')+': твоя заметка…">'""")
swap("""<span class="vl">visita</span>'""", """<span class="vl">визит</span>'""")

# ---- route ----------------------------------------------------------------
swap("""  return d.toLocaleDateString('pt-PT',{weekday:'long',day:'2-digit',month:'2-digit'});""",
     """  return d.toLocaleDateString('ru-RU',{weekday:'long',day:'2-digit',month:'2-digit'});""")
swap("""' visita'+(list.length>1?'s':'')+""", """' '+visitWord(list.length)+""")
swap("""'">abrir no Maps</a>':'')+""", """'">открыть в Maps</a>':'')+""")
swap("""'<div class="leg">'+Math.round(dist)+' km &middot; ~'+drive+' min de carro'+
           (tight?' &mdash; pouco tempo entre visitas':'')+'</div>':'')+""",
     """'<div class="leg">'+Math.round(dist)+' км &middot; ~'+drive+' мин на машине'+
           (tight?' &mdash; мало времени между визитами':'')+'</div>':'')+""")
swap("function fmtDay(v){",
     """function visitWord(n){
  const t=n%10, h=n%100;
  if(t===1&&h!==11) return 'визит';
  if(t>=2&&t<=4&&(h<12||h>14)) return 'визита';
  return 'визитов';
}
function fmtDay(v){""")

# ---- map popup ------------------------------------------------------------
swap("""det.push('terreno '+new Intl.NumberFormat('pt-PT').format(h.land_area_m2)+' m²');""",
     """det.push('земля '+new Intl.NumberFormat('pt-PT').format(h.land_area_m2)+' м²');""")
swap("""det.push(Math.round(h.elevation_m)+' m alt.');""",
     """det.push(Math.round(h.elevation_m)+' м высота');""")
swap("""(VISITS[h.id]?'<div class="m">visita '+VISITS[h.id].replace('T',' ')+'</div>':'')+""",
     """(VISITS[h.id]?'<div class="m">визит '+VISITS[h.id].replace('T',' ')+'</div>':'')+""")
swap("""'" target="_blank" rel="noopener">ver anúncio</a>'+""",
     """'" target="_blank" rel="noopener">объявление</a>'+""")
swap("""' &nbsp; <a href="tel:+351'+h.agent_phone+'">ligar</a>':'')+""",
     """' &nbsp; <a href="tel:+351'+h.agent_phone+'">позвонить</a>':'')+""")
swap("""'" target="_blank" rel="noopener">rota</a></div>');""",
     """'" target="_blank" rel="noopener">маршрут</a></div>');""")
swap("""js.onerror=function(){toast('Mapa nao carregou',true);};""",
     """js.onerror=function(){toast('Карта не загрузилась',true);};""")

# ---- header line and toasts ----------------------------------------------
swap("""  el.textContent=HOUSES.length+' imóveis · '+c+' com notas · '+
    (SYNCED?'sincronizado':(retryTimer?'по enviar…':'offline'));""",
     "", required=False)
swap("""    (SYNCED?'sincronizado':(retryTimer?'por enviar…':'offline'));""",
     """    (SYNCED?'синхронизировано':(retryTimer?'не отправлено…':'офлайн'));""")
swap("""  el.textContent=HOUSES.length+' imóveis · '+c+' com notas · '+""",
     """  el.textContent=HOUSES.length+' домов · '+c+' с заметками · '+""")
swap("""document.getElementById('count').textContent=list.length+' de '+HOUSES.length+' imóveis';""",
     """document.getElementById('count').textContent=list.length+' из '+HOUSES.length+' домов';""")
swap(""" toast(okd?'Guardado ✓':'Guardado no telemóvel — envio depois',!okd);""",
     """ toast(okd?'Сохранено ✓':'Сохранено в телефоне — отправлю позже',!okd);""")
swap("""   toast(okd?'Visita marcada':'Guardado no telemóvel',!okd); return; }""",
     """   toast(okd?'Визит назначен':'Сохранено в телефоне',!okd); return; }""")
swap("""toast('Visita removida'); return; }""", """toast('Визит убран'); return; }""")
swap("""   toast('Estado: '+s.dataset.st); render(); return;}""",
     """   toast('Статус: '+(ST_SHORT[s.dataset.st]||s.dataset.st)); render(); return;}""")

# ---- footer ---------------------------------------------------------------
swap("""  '«выше округи» — насколько дом выше среднего рельефа в радиусе 15 км. '+
  '«до соседа» — до ближайшей постройки по карте. Notas partilhadas entre Serhii, Violeta e Milena.';""",
     """  '«выше округи» — насколько дом выше среднего рельефа в радиусе 15 км. '+
  '«до соседа» — до ближайшей постройки по карте. '+
  'Оценка: земля 30, комнаты 15, высота 15, без соседей 15, туалеты 10, лес 10, площадь 5. '+
  'Заметки общие — Serhii, Violeta, Milena.';""")

# ---- Cyrillic search ------------------------------------------------------
SEARCH = r"""
// "Лейрия" should find Leiria. Nobody spells a foreign name the same way twice,
// so transliterate and then match loosely rather than demanding an exact hit.
const RU_LAT={а:'a',б:'b',в:'v',г:'g',д:'d',е:'e',ё:'e',ж:'j',з:'z',и:'i',й:'i',
  к:'c',л:'l',м:'m',н:'n',о:'o',п:'p',р:'r',с:'s',т:'t',у:'u',ф:'f',х:'h',
  ц:'c',ч:'ch',ш:'sh',щ:'sh',ъ:'',ы:'i',ь:'',э:'e',ю:'iu',я:'ia'};
function deaccent(t){ return t.normalize('NFD').replace(/[̀-ͯ]/g,''); }
function translit(t){
  t=t.replace(/ия\b/g,'ia').replace(/ий\b/g,'i').replace(/ья/g,'ia');
  return t.replace(/[а-яё]/g,function(c){ return RU_LAT[c]!==undefined?RU_LAT[c]:c; });
}
function matches(hay,query){
  hay=deaccent(hay.toLowerCase());
  const q=deaccent(query.toLowerCase());
  if(hay.includes(q)) return true;
  if(!/[а-яё]/.test(q)) return false;
  const t=translit(q);
  if(hay.includes(t)) return true;
  // the tail of a transliteration is the least reliable part - drop it
  const stem=t.slice(0,Math.max(3,t.length-2));
  return hay.split(/[\s,·]+/).some(function(w){ return w.startsWith(stem); });
}
"""
swap("function keep(h){", SEARCH + "\nfunction keep(h){")
swap(""" if(q){const hay=[h.concelho,h.freguesia,h.district,h.agency_name].filter(Boolean).join(' ').toLowerCase();
  if(!hay.includes(q))return false;}""",
     """ if(q){const hay=[h.concelho,h.freguesia,h.district,h.agency_name].filter(Boolean).join(' ');
  if(!matches(hay,q))return false;}""")

p.write_text(s, encoding="utf-8")
print(f"russian ui + cyrillic search, {len(s)//1024} KB")
