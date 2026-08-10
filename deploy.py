"""Stamp the build, so open phones learn there is a newer one.

All day Serhii, Violeta and Milena were looking at whatever version their
browser had cached, which is why fixes kept "not showing up". The notes sync
themselves every twenty seconds; the page itself never did.

This writes a build stamp into index.html and into version.txt beside it. The
running page compares the two on the same twenty-second tick and says when it
is out of date - reloading on its own if nobody is mid-sentence.

Run this instead of committing index.html by hand.
"""
import datetime
import pathlib
import re
import subprocess

import os
HERE = pathlib.Path(os.environ.get("CASA_BUILD_DIR",
                                   pathlib.Path(__file__).parent))
INDEX = HERE / "index.html"
VERSION = HERE / "version.txt"


def build_id():
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=HERE,
                             capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        sha = ""
    return f"{ts}-{sha}" if sha else ts


CHECK = """
// The page cannot update itself in the background, but it can notice.
const BUILD='__BUILD__';
let updateSeen=false;
async function checkBuild(){
  if(updateSeen) return;
  try{
    const r=await fetch('version.txt?t='+Date.now(),{cache:'no-store'});
    if(!r.ok) return;
    const live=(await r.text()).trim();
    if(!live||live===BUILD) return;
    updateSeen=true;
    const busy=document.activeElement&&
      (document.activeElement.tagName==='TEXTAREA'||document.activeElement.tagName==='INPUT');
    if(!busy&&!DIRTY.size){ location.reload(); return; }   // nothing to lose
    const bar=document.getElementById('upd');
    if(bar){ bar.className='upd on';
      bar.innerHTML='Вышла новая версия сайта <button id="updgo">обновить</button>'; }
  }catch(e){}
}
"""


def main():
    s = INDEX.read_text(encoding="utf-8")
    bid = build_id()

    if "const BUILD=" not in s:
        s = s.replace("async function tick(){",
                      CHECK + "\nasync function tick(){", 1)
        s = s.replace("    mark();\n  }\n  pollTimer=setTimeout(tick, pollWait);",
                      "    mark();\n    checkBuild();\n  }\n"
                      "  pollTimer=setTimeout(tick, pollWait);", 1)
        s = s.replace('<div class="soon" id="soon"></div>',
                      '<div class="upd" id="upd"></div>\n<div class="soon" id="soon"></div>', 1)
        s = s.replace(".soon{display:none}",
                      ".upd{display:none}\n"
                      ".upd.on{display:flex;align-items:center;gap:10px;margin:10px 0 0;\n"
                      " background:var(--accent);color:var(--paper);border-radius:12px;\n"
                      " padding:10px 13px;font-size:14px;font-weight:600}\n"
                      ".upd button{margin-left:auto;background:var(--paper);\n"
                      " border-color:var(--paper);color:var(--accent);font-weight:600}\n"
                      ".soon{display:none}", 1)
        s = s.replace("document.addEventListener('click',async e=>{",
                      "document.addEventListener('click',async e=>{\n"
                      " if(e.target.id==='updgo'){ location.reload(); return; }", 1)

    s = re.sub(r"const BUILD='[^']*'", f"const BUILD='{bid}'", s, count=1)
    INDEX.write_text(s, encoding="utf-8")
    VERSION.write_text(bid + "\n", encoding="utf-8")
    print(f"build {bid} stamped into index.html and version.txt")


if __name__ == "__main__":
    main()
