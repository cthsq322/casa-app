"""Stop the server from overwriting work that never reached it.

The old loop replaced the local notes, statuses and visits with whatever the
server held. That is fine until a save fails - then the next poll quietly threw
away what you had just typed. Now anything changed locally is marked dirty,
survives every poll until it is confirmed sent, and is pushed again on its own.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")

# ---- what we changed and have not confirmed sent --------------------------
DIRTY = """let DIRTY=new Set(JSON.parse(localStorage.getItem('casa_dirty')||'[]'));
function soil(kind,id){ DIRTY.add(kind+':'+id); saveDirty(); }
function saveDirty(){ localStorage.setItem('casa_dirty',JSON.stringify([...DIRTY])); }
function dirtyHas(kind,id){ return DIRTY.has(kind+':'+id); }

// server value wins, except where we hold something not yet confirmed sent
function mergeMap(serverMap,localMap,kind){
  const out=Object.assign({},serverMap||{});
  Object.keys(localMap||{}).forEach(function(id){
    if(dirtyHas(kind,id)) out[id]=localMap[id];
  });
  Object.keys(out).forEach(function(id){
    if(out[id]==null) delete out[id];
  });
  return out;
}
function mergeNotes(fresh){
  const map=new Map((fresh||[]).map(function(n){return [key(n),n];}));
  let pending=false;
  Object.values(NOTES).flat().forEach(function(n){
    const srv=map.get(key(n));
    const ours=dirtyHas('n',n.house_id)&&n.author===me;
    if(!srv||(ours&&(n.updated_at||'')>=(srv.updated_at||''))){
      map.set(key(n),n);
      if(ours) pending=true;
    }
  });
  const out={};
  [...map.values()].forEach(function(n){(out[n.house_id]=out[n.house_id]||[]).push(n);});
  return {notes:out,pending:pending};
}
let SYNCED=false;"""
assert "let SYNCED=false;" in s
s = s.replace("let SYNCED=false;", DIRTY, 1)

# ---- pull must not clobber unsent local state -----------------------------
s = s.replace("    STATUS=d.status||{};\n    VISITS=d.visits||{};",
              "    STATUS=mergeMap(d.status,STATUS,'s');\n"
              "    VISITS=mergeMap(d.visits,VISITS,'v');")

# ---- a confirmed push clears the dirty marks ------------------------------
s = s.replace("    cacheSave();\n    return true;",
              "    cacheSave();\n    DIRTY.clear(); saveDirty();\n    return true;")

# ---- the poll merges instead of replacing ---------------------------------
OLD = """      const before=JSON.stringify(Object.values(NOTES).flat().map(key).sort());
      const map={}; fresh.forEach(n=>{(map[n.house_id]=map[n.house_id]||[]).push(n)});
      const after=JSON.stringify(fresh.map(key).sort());
      if(before!==after){ NOTES=map; cacheSave(); render(); }"""
NEW = """      const before=JSON.stringify(Object.values(NOTES).flat()
        .map(function(n){return key(n)+'|'+(n.text||'')+'|'+(n.tier||'');}).sort());
      const m=mergeNotes(fresh);
      NOTES=m.notes;
      const after=JSON.stringify(Object.values(NOTES).flat()
        .map(function(n){return key(n)+'|'+(n.text||'')+'|'+(n.tier||'');}).sort());
      if(before!==after){ cacheSave(); render(); }
      if(m.pending||DIRTY.size) scheduleRetry();   // we are ahead of the server"""
assert OLD in s, "poll merge block not found"
s = s.replace(OLD, NEW)

# ---- mark every local change ----------------------------------------------
s = s.replace(" NOTES[id]=rest; render();",
              " NOTES[id]=rest; soil('n',id); render();")
s = s.replace("   if(vi.value){ VISITS[id]=vi.value; STATUS[id]='visita'; } "
              "else { delete VISITS[id]; }",
              "   if(vi.value){ VISITS[id]=vi.value; STATUS[id]='visita'; } "
              "else { delete VISITS[id]; }\n"
              "   soil('v',id); soil('s',id);")
s = s.replace(" if(cl){ delete VISITS[cl.dataset.clr];",
              " if(cl){ delete VISITS[cl.dataset.clr]; soil('v',cl.dataset.clr);")
s = s.replace("   STATUS[id]=s.dataset.st; await push();",
              "   STATUS[id]=s.dataset.st; soil('s',id); await push();")

# ---- anything left over from a previous session goes out at startup -------
s = s.replace(" mark();\n document.getElementById('foot').innerHTML=",
              " mark();\n if(DIRTY.size){ push().then(mark); }\n"
              " document.getElementById('foot').innerHTML=")

p.write_text(s, encoding="utf-8")
print("merge + dirty tracking added")
