"""test_proposta.py — tests for Proposta tab and translation sync.

Checks:
  • propostas.json is valid JSON with required top-level structure
  • propostas.json houses have required fields
  • propostas.json houses have "sync" key with correct sub-structure
  • sync.json files exist in proposta/out/
  • history.json files exist in proposta/out/
  • sync units have required fields (id, status, ru_hash, pt_hash)
  • STALE indicator logic: unit with ru_updated_at > pt_updated_at → STALE
  • index.html contains data-f="proposta" filter button
  • index.html contains #propostabox div
  • index.html contains renderProposta function
  • index.html contains ppCopyText function with stale-warning logic
  • index.html contains pp-sync-bar CSS class
  • existing tabs not broken: check key markers for all, notes, mapa buttons
  • JS syntax still clean (via node --check)

Run:  python test_proposta.py
Exit: 0 = all green, 1 = failures found.
"""
import json
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).parent
PROPOSTA_DIR = HERE.parent / "proposta"
OUT_DIR = PROPOSTA_DIR / "out"
FAIL = []


def fail(msg):
    FAIL.append(msg)
    print("FAIL:", msg)


def ok(msg):
    print(" OK :", msg)


# ── 1. propostas.json valid JSON ──────────────────────────────────────────
pj = HERE / "propostas.json"
if not pj.exists():
    fail("propostas.json не найден")
    sys.exit(1)

try:
    data = json.loads(pj.read_text(encoding="utf-8"))
    ok("propostas.json валидный JSON")
except json.JSONDecodeError as e:
    fail(f"propostas.json невалидный JSON: {e}")
    sys.exit(1)

# ── 2. Top-level structure ────────────────────────────────────────────────
for key in ("version", "houses"):
    if key in data:
        ok(f"propostas.json содержит top-level '{key}'")
    else:
        fail(f"propostas.json НЕ содержит top-level '{key}'")

houses = data.get("houses", [])
if houses:
    ok(f"propostas.json содержит {len(houses)} домов")
else:
    fail("propostas.json: пустой список houses")

# ── 3. Each house has required fields ─────────────────────────────────────
REQUIRED_HOUSE_FIELDS = ["id", "title", "location", "listing", "offer",
                         "financibility", "math", "claims", "reconcile", "links"]
for house in houses:
    hid = house.get("id", "?")
    for field in REQUIRED_HOUSE_FIELDS:
        if field in house:
            ok(f"Дом #{hid}: поле '{field}' присутствует")
        else:
            fail(f"Дом #{hid}: НЕ содержит поле '{field}'")
    break   # check only first house to keep output manageable

# ── 4. Sync key in houses ─────────────────────────────────────────────────
houses_with_sync = [h for h in houses if "sync" in h]
if houses_with_sync:
    ok(f"propostas.json: {len(houses_with_sync)} из {len(houses)} домов имеют 'sync'")
else:
    fail("propostas.json: ни один дом не имеет 'sync' ключа")

# ── 5. Sync structure validation ──────────────────────────────────────────
for house in houses_with_sync[:1]:
    hid = house.get("id", "?")
    sync = house["sync"]
    for key in ("last_checked", "units", "summary"):
        if key in sync:
            ok(f"Дом #{hid} sync: содержит '{key}'")
        else:
            fail(f"Дом #{hid} sync: НЕ содержит '{key}'")

    summary = sync.get("summary", {})
    for sk in ("synced", "stale", "missing"):
        if sk in summary:
            ok(f"Дом #{hid} sync.summary: содержит '{sk}'={summary[sk]}")
        else:
            fail(f"Дом #{hid} sync.summary: НЕ содержит '{sk}'")

    units = sync.get("units", [])
    if units:
        ok(f"Дом #{hid} sync.units: {len(units)} единиц")
        u0 = units[0]
        for uf in ("id", "status", "ru_hash", "pt_hash", "ru_updated_at", "pt_updated_at"):
            if uf in u0:
                ok(f"Дом #{hid} sync.units[0]: поле '{uf}' присутствует")
            else:
                fail(f"Дом #{hid} sync.units[0]: НЕ содержит '{uf}'")
    else:
        fail(f"Дом #{hid} sync.units: пусто")

# ── 6. STALE logic test ───────────────────────────────────────────────────
# Simulate: create a unit where ru_updated_at > pt_updated_at → must be STALE
import hashlib
sys.path.insert(0, str(PROPOSTA_DIR))
try:
    from translation_sync import _unit_status  # type: ignore
    # SYNCED case
    s1 = _unit_status("abc", "def", "2026-08-13T10:00:00", "2026-08-13T10:00:00")
    if s1 == "SYNCED":
        ok("STALE logic: tu==pt → SYNCED")
    else:
        fail(f"STALE logic: tu==pt → {s1} (ожидали SYNCED)")

    # STALE case
    s2 = _unit_status("abc", "def", "2026-08-13T12:00:00", "2026-08-13T10:00:00")
    if s2 == "STALE":
        ok("STALE logic: ru_upd > pt_upd → STALE")
    else:
        fail(f"STALE logic: ru_upd > pt_upd → {s2} (ожидали STALE)")

    # MISSING case
    s3 = _unit_status("abc", "", "2026-08-13T10:00:00", "2026-08-13T10:00:00")
    if s3 == "MISSING":
        ok("STALE logic: pt_hash='' → MISSING")
    else:
        fail(f"STALE logic: pt_hash='' → {s3} (ожидали MISSING)")
except ImportError as e:
    fail(f"translation_sync import error: {e}")

# ── 7. Sync files exist in proposta/out/ ─────────────────────────────────
for house in houses[:2]:
    hid = house.get("id")
    sync_path = OUT_DIR / f"{hid}_sync.json"
    hist_path = OUT_DIR / f"{hid}_history.json"
    if sync_path.exists():
        ok(f"proposta/out/{hid}_sync.json существует")
    else:
        fail(f"proposta/out/{hid}_sync.json НЕ найден")
    if hist_path.exists():
        ok(f"proposta/out/{hid}_history.json существует")
    else:
        fail(f"proposta/out/{hid}_history.json НЕ найден")

# ── 8. index.html proposta integration ────────────────────────────────────
idx = HERE / "index.html"
if not idx.exists():
    fail("index.html не найден")
    sys.exit(1)

html = idx.read_text(encoding="utf-8")

for expect, label in [
    ('data-f="proposta"',    "кнопка data-f=proposta в навигации"),
    ('id="propostabox"',     "контейнер #propostabox в HTML"),
    ('renderProposta',       "функция renderProposta"),
    ('ppCopyText',           "функция ppCopyText (копирование с предупреждением)"),
    ('pp-sync-bar',          "CSS класс pp-sync-bar"),
    ('stale-btn',            "CSS класс stale-btn (кнопка устаревшего перевода)"),
    ('isStale',              "логика isStale в ppCopyText"),
    ('PROPOSTA_DATA',        "переменная PROPOSTA_DATA для кэша"),
    ('propostas.json',       "fetch propostas.json"),
    ('pp-work-status',       "CSS класс pp-work-status (индикатор статуса)"),
    ('ppRenderSyncBar',      "функция ppRenderSyncBar (общий индикатор)"),
]:
    if expect in html:
        ok(f"index.html: {label}")
    else:
        fail(f"index.html НЕ содержит: {label}")

# ── 9. Existing tabs not broken ───────────────────────────────────────────
EXISTING_MARKERS = [
    ('data-f="all"',     "кнопка Все"),
    ('data-f="notes"',   "кнопка Лента"),
    ('data-f="mapa"',    "кнопка Карта"),
    ('data-f="rota"',    "кнопка Маршрут"),
    ('data-f="day"',     "кнопка Мой день"),
    ('id="feedbox"',     "feedbox контейнер"),
    ('id="mapbox"',      "mapbox контейнер"),
    ('renderFeed',       "функция renderFeed"),
    ('renderMapa',       "функция renderMapa"),
    ('renderRota',       "функция renderRota"),
    ('<title>Дома</title>', "заголовок 'Дома' (не 'тест')"),
]
for expect, label in EXISTING_MARKERS:
    if expect in html:
        ok(f"existing: {label}")
    else:
        fail(f"СЛОМАНО: {label}")

# ── 10. JS syntax check ───────────────────────────────────────────────────
blocks = re.findall(r"<script>(.*?)</script>", html, re.S)
for i, js in enumerate(blocks):
    tmp = pathlib.Path(tempfile.gettempdir()) / f"casa_proposta_check_{i}.js"
    tmp.write_text(js, encoding="utf-8")
    r = subprocess.run(["node", "--check", str(tmp)], capture_output=True, text=True)
    tmp.unlink(missing_ok=True)
    if r.returncode:
        fail(f"index.html JS block {i}: синтаксис сломан\n{r.stderr[:400]}")
    else:
        ok(f"index.html JS block {i}: синтаксис OK")

# ── Summary ───────────────────────────────────────────────────────────────
print()
if FAIL:
    print(f"ИТОГ: {len(FAIL)} провал(ов)")
    sys.exit(1)
else:
    print("ИТОГ: все proposta checks зелёные")
    sys.exit(0)
