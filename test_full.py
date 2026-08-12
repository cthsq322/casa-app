"""test_full.py — structural tests for the casa-app build.

Checks:
  • frases-data.js exists and defines the 5 picker templates
  • index.html loads frases-data.js via <script src>
  • index.html contains picker modal elements (mpback, mplist, mpx)
  • index.html contains buildFirstContact, openPicker, closePicker functions
  • index.html JS syntax is clean (via node --check)
  • frases.html loads frases-data.js
  • frases.html placeholder divs exist (s1, s2, s3, s6, s7 as bare <div id="sN">)
  • release.py includes frases-data.js in FILES list

Run:  python test_full.py
Exit: 0 = all green, 1 = failures found.
"""
import pathlib, re, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).parent
FAIL = []


def fail(msg):
    FAIL.append(msg)
    print("FAIL:", msg)


def ok(msg):
    print(" OK :", msg)


# ── frases-data.js ────────────────────────────────────────
fd = HERE / "frases-data.js"
if not fd.exists():
    fail("frases-data.js не найден")
else:
    src = fd.read_text(encoding="utf-8")
    for expect in ["FRASES_PICKER", "FRASES_FIRE_CONCELHOS",
                   "primeiro-contacto", "docs-banco", "incendio",
                   "mudar-hora", "cancelar"]:
        if expect in src:
            ok(f"frases-data.js содержит '{expect}'")
        else:
            fail(f"frases-data.js НЕ содержит '{expect}'")

# ── index.html ────────────────────────────────────────────
idx = HERE / "index.html"
if not idx.exists():
    fail("index.html не найден")
    sys.exit(1)

html = idx.read_text(encoding="utf-8")

for expect, label in [
    ('src="frases-data.js"',         "загружает frases-data.js"),
    ('id="mpback"',                  "picker backdrop #mpback"),
    ('id="mplist"',                  "picker list #mplist"),
    ('id="mpx"',                     "picker close #mpx"),
    ('id="mptitle"',                 "picker title #mptitle"),
    ('buildFirstContact',            "функция buildFirstContact"),
    ('openPicker',                   "функция openPicker"),
    ('closePicker',                  "функция closePicker"),
    ('portalRef',                    "функция portalRef"),
    ('buildWhenNew',                 "функция buildWhenNew"),
    ('isFireRisk',                   "функция isFireRisk"),
    ('data-pick',                    "атрибут data-pick на кнопках picker"),
    ('buildPickerText',              "функция buildPickerText"),
    ('<title>Дома</title>',          "заголовок 'Дома' (не 'тест')"),
]:
    if expect in html:
        ok(f"index.html: {label}")
    else:
        fail(f"index.html НЕ содержит: {label}")

# ── JS syntax check ───────────────────────────────────────
blocks = re.findall(r"<script>(.*?)</script>", html, re.S)
for i, js in enumerate(blocks):
    tmp = pathlib.Path(tempfile.gettempdir()) / f"casa_test_{i}.js"
    tmp.write_text(js, encoding="utf-8")
    r = subprocess.run(["node", "--check", str(tmp)], capture_output=True, text=True)
    tmp.unlink(missing_ok=True)
    if r.returncode:
        fail(f"index.html JS block {i}: синтаксис сломан\n{r.stderr[:400]}")
    else:
        ok(f"index.html JS block {i}: синтаксис OK")

# ── frases.html ───────────────────────────────────────────
fr = HERE / "frases.html"
if not fr.exists():
    fail("frases.html не найден")
else:
    fhtml = fr.read_text(encoding="utf-8")
    if 'src="frases-data.js"' in fhtml:
        ok("frases.html загружает frases-data.js")
    else:
        fail("frases.html НЕ загружает frases-data.js")
    # placeholder divs must be bare (no data-n on the div itself)
    for sid in ["s1", "s2", "s3", "s6", "s7"]:
        if f'id="{sid}"' in fhtml:
            ok(f"frases.html содержит placeholder #{sid}")
        else:
            fail(f"frases.html НЕ содержит placeholder #{sid}")
    # static inline sections must be gone
    for old_marker in [
        "Boa tarde.",  # old s1 greeting (replaced by Bom dia. in data)
        'data-n="1"',  # static s1 — should be set by JS now
    ]:
        if old_marker in fhtml:
            fail(f"frases.html всё ещё содержит статичный маркер: '{old_marker}'")
        else:
            ok(f"frases.html: старый маркер '{old_marker}' убран — хорошо")

# ── release.py ────────────────────────────────────────────
rel = HERE / "release.py"
if rel.exists() and "frases-data.js" in rel.read_text(encoding="utf-8"):
    ok("release.py: frases-data.js в FILES")
else:
    fail("release.py: frases-data.js НЕ добавлен в FILES")

# ── summary ───────────────────────────────────────────────
print()
if FAIL:
    print(f"ИТОГ: {len(FAIL)} провал(ов)")
    sys.exit(1)
else:
    total = html.count(" OK :") + 1  # rough
    print("ИТОГ: все проверки зелёные")
    sys.exit(0)
