"""Give the statuses the shape of the work Serhii actually does.

Five labels were not enough: writing and phoning are different acts, waiting
for a call back is its own state, and "we agreed on a day" is not the same as
"we have already been". The ladder now runs from first contact to decision, and
setting a visit time moves the house to `marcado` on its own.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")

STEPS = "['escrito','ligado','espera','resposta','marcado','visto','top','arquivo']"

# ---- the buttons on the card ----------------------------------------------
OLD = ("  '<div class=\"st\">'+['escrito','resposta','visita','top','arquivo']\n"
       "    .map(s=>'<button data-st=\"'+s+'\" data-h=\"'+h.id+'\"'+"
       "((STATUS[h.id]||h.status)===s?' class=\"on\"':'')+'>'+s+'</button>').join('')+")
NEW = ("  '<div class=\"st\">'+" + STEPS + "\n"
       "    .map(s=>'<button data-st=\"'+s+'\" data-h=\"'+h.id+'\"'+"
       "((STATUS[h.id]||h.status)===s?' class=\"on\"':'')+'>'+ST_SHORT[s]+'</button>').join('')+")
assert OLD in s, "status buttons not found"
s = s.replace(OLD, NEW)

# ---- labels, in both places ----------------------------------------------
OLD_LABELS = """const ST_LABELS={escrito:'✍ escrito',resposta:'↩ resposta',visita:'📅 visita',
                 top:'★ top',arquivo:'✕ arquivo'};"""
NEW_LABELS = """const ST_LABELS={escrito:'✍ escrevi',ligado:'☎ liguei',
  espera:'⏳ à espera',resposta:'↩ responderam',marcado:'📅 marcado',
  visto:'👁 já vimos',top:'★ favorita',arquivo:'✕ fora'};
const ST_SHORT={escrito:'escrevi',ligado:'liguei',espera:'à espera',
  resposta:'responderam',marcado:'marcado',visto:'já vimos',
  top:'favorita',arquivo:'fora'};"""
assert OLD_LABELS in s
s = s.replace(OLD_LABELS, NEW_LABELS)

# ---- booking a time means the visit is agreed -----------------------------
s = s.replace("if(vi.value){ VISITS[id]=vi.value; STATUS[id]='visita'; }",
              "if(vi.value){ VISITS[id]=vi.value; STATUS[id]='marcado'; }")

# ---- anything saved under the old name keeps working ----------------------
s = s.replace("function renderStBar(){",
              """function migrateStatus(){
  let moved=false;
  Object.keys(STATUS).forEach(function(id){
    if(STATUS[id]==='visita'){ STATUS[id]='marcado'; moved=true; }
  });
  if(moved){ cacheSave(); }
}
function renderStBar(){
  migrateStatus();""")

p.write_text(s, encoding="utf-8")
print("statuses widened to", STEPS)
