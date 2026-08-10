"""Make the sync survive a throttled or offline server.

jsonblob answers 429 when it is hit too often, and a phone on the road drops
the network entirely. Neither should cost a note. The poll now backs off
instead of hammering, a failed save retries itself, and the header says plainly
whether what you typed has already reached the other person.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")

# ---- honest status in the header ------------------------------------------
MARK = """function mark(){
  const el=document.getElementById('sub');
  if(!el||!HOUSES.length) return;
  const c=Object.keys(NOTES).filter(function(k){return (NOTES[k]||[]).length;}).length;
  el.textContent=HOUSES.length+' imóveis · '+c+' com notas · '+
    (SYNCED?'sincronizado':(retryTimer?'por enviar…':'offline'));
}
async function push(mine){"""
assert "async function push(mine){" in s
s = s.replace("async function push(mine){", MARK, 1)

# a save that did not land is retried on its own
s = s.replace("  }catch(e){ SYNCED=false; return false; }",
              "  }catch(e){ SYNCED=false; scheduleRetry(); return false; }")

# ---- polling that backs off -----------------------------------------------
OLD_POLL = """setInterval(async()=>{
  if(document.hidden) return;
  const fresh=await pull();
  if(!SYNCED) return;
  const before=JSON.stringify(Object.values(NOTES).flat().map(key).sort());
  const map={}; fresh.forEach(n=>{(map[n.house_id]=map[n.house_id]||[]).push(n)});
  const after=JSON.stringify(fresh.map(key).sort());
  if(before!==after){ NOTES=map; cacheSave(); render(); }
}, 20000);"""

NEW_POLL = """const POLL_MIN=20000, POLL_MAX=150000;
let pollWait=POLL_MIN, pollTimer=null, retryTimer=null;

function scheduleRetry(){
  if(retryTimer) return;                        // one pending retry is enough
  retryTimer=setTimeout(async()=>{ retryTimer=null; await push(); mark(); }, 15000);
}

async function tick(){
  if(!document.hidden){
    const fresh=await pull();
    if(SYNCED){
      pollWait=POLL_MIN;                        // the server is answering again
      const before=JSON.stringify(Object.values(NOTES).flat().map(key).sort());
      const map={}; fresh.forEach(n=>{(map[n.house_id]=map[n.house_id]||[]).push(n)});
      const after=JSON.stringify(fresh.map(key).sort());
      if(before!==after){ NOTES=map; cacheSave(); render(); }
    } else {
      pollWait=Math.min(pollWait*2, POLL_MAX);  // throttled or offline - ease off
    }
    mark();
  }
  pollTimer=setTimeout(tick, pollWait);
}
pollTimer=setTimeout(tick, POLL_MIN);

// coming back to the tab, or back online, is worth an immediate look
document.addEventListener('visibilitychange',function(){
  if(!document.hidden){ clearTimeout(pollTimer); pollWait=POLL_MIN; tick(); }
});
addEventListener('online',function(){ clearTimeout(pollTimer); pollWait=POLL_MIN; tick(); });"""

assert OLD_POLL in s, "poll loop not found"
s = s.replace(OLD_POLL, NEW_POLL)

# ---- one place decides what the header says --------------------------------
OLD_SUB = """ const s={houses:HOUSES.length,commented:Object.keys(NOTES).length};
 document.getElementById('sub').textContent=s.houses+' imóveis · '+s.commented+
   ' com notas'+(SYNCED?' · sincronizado':' · offline');"""
assert OLD_SUB in s, "header line not found"
s = s.replace(OLD_SUB, " mark();")

# keep it current after every save
s = s.replace("   const okd=await push(); render();\n"
              "   toast(okd?'Visita marcada':'Guardado no telemovel',!okd); return; }",
              "   const okd=await push(); render(); mark();\n"
              "   toast(okd?'Visita marcada':'Guardado no telemóvel',!okd); return; }")
s = s.replace(" const okd=await push();\n"
              " toast(okd?'Guardado ✓':'Guardado no telemóvel (sem rede)',!okd);",
              " const okd=await push(); mark();\n"
              " toast(okd?'Guardado ✓':'Guardado no telemóvel — envio depois',!okd);")

p.write_text(s, encoding="utf-8")
print("backoff + honest status added")
