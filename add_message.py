"""The message, with the date already in it.

Serhii sends the listing link first, then the text - so the text starts with
the situation, not with "bom dia". It says the route is already planned, names
the slot the loop gives this house, and asks the two questions that decide
whether the drive is worth it at all: does it pass the credit, is it ready for
the bank's valuation.

Everything else he can say on the phone. A long list of questions in a first
message reads as a survey and gets no answer.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    if old not in s:
        print("  пропущено:", old.strip().splitlines()[0][:60])
        return
    s = s.replace(old, new, 1)


MSG = r"""
// The link goes first, then this - so no greeting, straight to the point.
function msgFor(h){
  const d=DAYOF[h.id];
  const when = d && d.when ? d.when+' por volta das '+d.at : null;
  const pt = [
    'Estamos a ver casas nesta zona e já temos a rota da semana montada.',
    when
      ? 'Esta casa fica-nos a jeito ' + ptDay(d) + ' — conseguimos passar por lá?'
      : 'Gostávamos de ver esta casa esta semana — que dias tem disponíveis?',
    when
      ? 'Se essa hora não servir, diga qual serve nesse mesmo dia: a rota está feita e é mais fácil trocar a hora do que o dia.'
      : '',
    'Antes de avançarmos, duas coisas: a casa passa no crédito e está pronta para a avaliação do banco?',
    'Temos aprovação do banco e vamos à avaliação, por isso conseguimos fechar depressa.'
  ].filter(Boolean).join('\n\n');
  return pt;
}
function ptDay(d){
  // "суббота 15.08" -> "no sábado, dia 15/08, por volta das 09:00"
  const RU2PT={'понедельник':'segunda-feira','вторник':'terça-feira',
    'среда':'quarta-feira','четверг':'quinta-feira','пятница':'sexta-feira',
    'суббота':'sábado','воскресenье':'domingo','воскресенье':'domingo'};
  const parts=(d.when||'').split(' ');
  const dia=RU2PT[parts[0]]||parts[0];
  const data=(parts[1]||'').replace('.','/');
  return 'na '+dia+(data?', dia '+data:'')+', por volta das '+d.at;
}
"""
swap("function card(h){", MSG + "\nfunction card(h){")

swap("""   '<button class="skip'""",
     """   '<button class="msg" data-msg="'+h.id+'">✍ текст агенту</button>'+
   '<button class="skip'""")

swap(" const cd=e.target.closest('[data-cpday]');",
     """ const mg=e.target.closest('[data-msg]');
 if(mg){
   const h=HOUSES.filter(function(x){return String(x.id)===String(mg.dataset.msg);})[0];
   if(h) copyText(msgFor(h)).then(function(){
     mg.classList.add('done');
     setTimeout(function(){ mg.classList.remove('done'); },1800);
     toast(DAYOF[h.id]?'Текст с датой скопирован':'Текст скопирован (дата не задана)');
   },function(){ toast('Не получилось скопировать',true); });
   return;
 }
 const cd=e.target.closest('[data-cpday]');""")

swap(".skip{padding:5px 12px;font-size:12.5px;border-color:var(--line);color:var(--soft)}",
     ".msg{padding:5px 12px;font-size:12.5px;border-color:var(--accent);\n"
     " color:var(--accent);font-weight:600}\n"
     ".msg.done{background:var(--accent);color:var(--paper)}\n"
     ".skip{padding:5px 12px;font-size:12.5px;border-color:var(--line);color:var(--soft)}")

p.write_text(s, encoding="utf-8")
print("ready-to-send message with the date")
