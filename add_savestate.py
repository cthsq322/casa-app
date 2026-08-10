"""Say plainly whether a note is saved, and let one actually be deleted.

Two things were wrong. Clearing the text did nothing - the old note came back,
because an empty string was read as "no change", so there was no way to take
back what you wrote. And nothing on screen ever said the note had been saved,
which on a phone means you retype it just in case.

Now the note saves while you type, the line under it says what state it is in,
and emptying it deletes it for real. Removing a visit also drops the "marcado"
status instead of leaving it lying.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    if old not in s:
        raise SystemExit("NOT FOUND: " + old[:100])
    s = s.replace(old, new, 1)


# ---- saving a note, and deleting one --------------------------------------
swap("""async function saveNote(id,text,tier){
 const prev=(NOTES[id]||[]).find(n=>n.author===me)||{};
 const rest=(NOTES[id]||[]).filter(n=>n.author!==me);
 rest.push({house_id:id,author:me,
   text: text!=='' ? text : (prev.text||''),
   tier: tier!=null ? tier : (prev.tier??null),
   updated_at:new Date().toISOString().slice(0,16).replace('T',' ')});
 NOTES[id]=rest; soil('n',id); render();
 const okd=await push(); mark();
 toast(okd?'Сохранено ✓':'Сохранено в телефоне — отправлю позже',!okd);
}""",
"""const SAVEMSG={};                     // id -> what the line under the note says
function noteState(id,state,txt){
  SAVEMSG[id]={state:state,txt:txt};
  const el=document.querySelector('[data-nsave="'+id+'"]');
  if(el){ el.textContent=txt; el.className='nsave '+state; }
}
async function saveNote(id,text,tier,quiet){
 const prev=(NOTES[id]||[]).find(n=>n.author===me)||{};
 const rest=(NOTES[id]||[]).filter(n=>n.author!==me);
 const t = tier!=null ? tier : (prev.tier??null);
 const now=new Date().toISOString().slice(0,16).replace('T',' ');

 if(!text && t==null){                // nothing left worth keeping - delete it
   if(!prev.author){ noteState(id,'idle',''); return; }
   NOTES[id]=rest; soil('n',id);
   if(!quiet) render();
   const gone=await push(); mark();
   noteState(id,'idle','заметка удалена');
   toast(gone?'Заметка удалена':'Удалено в телефоне — отправлю позже',!gone);
   return;
 }

 rest.push({house_id:id,author:me,text:text,tier:t,updated_at:now});
 NOTES[id]=rest; soil('n',id);
 if(!quiet) render();
 const okd=await push(); mark();
 noteState(id, okd?'ok':'wait',
   okd?'сохранено '+now.slice(11):'не отправлено — сохранено в телефоне');
 if(!quiet) toast(okd?'Сохранено ✓':'Сохранено в телефоне — отправлю позже',!okd);
}""")

# ---- the line under the note ----------------------------------------------
swap("""  '<textarea data-note="'+h.id+'" placeholder="'+(me||'')+': твоя заметка…">'+
    esc(mine?mine.text:'')+'</textarea>'+""",
     """  '<textarea data-note="'+h.id+'" placeholder="'+(me||'')+': твоя заметка…">'+
    esc(mine?mine.text:'')+'</textarea>'+
  '<div class="nsave '+((SAVEMSG[h.id]||{}).state||'idle')+'" data-nsave="'+h.id+'">'+
    ((SAVEMSG[h.id]||{}).txt || (mine&&mine.text?'сохранено '+
      (mine.updated_at||'').slice(11):''))+'</div>'+""")

# ---- save while typing, without stealing the cursor -----------------------
swap(" const ta=e.target.closest('[data-note]');\n if(ta)saveNote(+ta.dataset.note,ta.value,null);",
     " const ta=e.target.closest('[data-note]');\n"
     " if(ta) saveNote(+ta.dataset.note,ta.value.trim(),null);")

swap("document.getElementById('q').addEventListener('input'",
     """const typeTimers={};
document.addEventListener('input',function(e){
  const ta=e.target.closest('[data-note]');
  if(!ta) return;
  const id=+ta.dataset.note;
  noteState(id,'typing','печатаешь…');
  clearTimeout(typeTimers[id]);
  typeTimers[id]=setTimeout(function(){
    saveNote(id,ta.value.trim(),null,true);      // quiet: no re-render mid-typing
  },1200);
});
document.getElementById('q').addEventListener('input'""")

# ---- taking the visit away takes the status with it -----------------------
swap(" if(cl){ delete VISITS[cl.dataset.clr]; soil('v',cl.dataset.clr); await push(); render(); toast('Визит убран'); return; }",
     " if(cl){ const id=cl.dataset.clr;\n"
     "   delete VISITS[id]; soil('v',id);\n"
     "   if(stVal(id)==='marcado'){ setStatus(id,'resposta'); }   // agreed, then unagreed\n"
     "   await push(); render(); mark(); toast('Визит убран'); return; }")

swap("   else { delete VISITS[id]; soil('v',id); }",
     "   else { delete VISITS[id]; soil('v',id);\n"
     "     if(stVal(id)==='marcado'){ setStatus(id,'resposta'); } }")

# ---- styles ---------------------------------------------------------------
swap(".vby{font-size:11.5px;color:var(--soft)}",
     """.vby{font-size:11.5px;color:var(--soft)}
.nsave{font-size:11.5px;min-height:15px;margin-top:-3px}
.nsave.idle{color:var(--soft)}
.nsave.typing{color:var(--soft)}
.nsave.ok{color:var(--accent)}
.nsave.wait{color:var(--warn);font-weight:600}""")

p.write_text(s, encoding="utf-8")
print("save state + real delete + visit/status consistency")
