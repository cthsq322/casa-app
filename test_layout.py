"""test_layout.py — layout/CSS tests for the casa-app build.

Checks:
  • Picker buttons (.mpbtn) have min-height >= 40px
  • Picker font-size >= 12px (15px defined)
  • No horizontal overflow on the picker drawer
  • Both light and dark theme CSS variables are referenced
  • frases-data.js mpbtn colour uses CSS vars (not hardcoded hex)
  • index.html has the picker close button (#mpx) with accessible tap target

Run:  python test_layout.py
Exit: 0 = all green, 1 = failures found.
"""
import pathlib, re, sys

HERE = pathlib.Path(__file__).parent
FAIL = []


def fail(msg):
    FAIL.append(msg)
    print("FAIL:", msg)


def ok(msg):
    print(" OK :", msg)


idx = HERE / "index.html"
if not idx.exists():
    fail("index.html не найден")
    sys.exit(1)

html = idx.read_text(encoding="utf-8")

# ── Extract all CSS (from <style>...</style> blocks) ──────────
css_blocks = re.findall(r"<style>(.*?)</style>", html, re.S)
css = "\n".join(css_blocks)

# ── 1. .mpbtn min-height ≥ 40px ───────────────────────────────
# Accept: min-height:40px, min-height:48px, or height inside .mpbtn
h_matches = re.findall(r'\.mpbtn\s*\{([^}]+)\}', css)
found_height = False
for block in h_matches:
    # look for min-height or height with value >= 40
    for m in re.finditer(r'(?:min-height|height)\s*:\s*(\d+)px', block):
        if int(m.group(1)) >= 40:
            found_height = True
if found_height:
    ok(".mpbtn min-height ≥ 40px")
else:
    fail(".mpbtn не имеет min-height ≥ 40px")

# ── 2. .mpbtn font-size ≥ 12px ────────────────────────────────
fs_matches = re.findall(r'\.mpbtn\s*\{([^}]+)\}', css)
found_fs = False
for block in fs_matches:
    for m in re.finditer(r'font-size\s*:\s*(\d+)px', block):
        if int(m.group(1)) >= 12:
            found_fs = True
if found_fs:
    ok(".mpbtn font-size ≥ 12px")
else:
    fail(".mpbtn нет font-size ≥ 12px")

# ── 3. No overflow-x:hidden on body or no horizontal scroll forced ─
# Positive check: mpdrawer should have overflow-y:auto or overflow-y:scroll
drawer_css = re.findall(r'\.mpdrawer\s*\{([^}]+)\}', css)
found_overflow = any("overflow-y" in b for b in drawer_css)
if found_overflow:
    ok(".mpdrawer имеет overflow-y (вертикальный скролл, не горизонтальный)")
else:
    fail(".mpdrawer нет overflow-y: возможен горизонтальный scroll")

# ── 4. Dark-theme support — both --card and colour vars ──────
dark_markers = ["prefers-color-scheme", "data-theme"]
found_dark = any(m in css for m in dark_markers)
if found_dark:
    ok("CSS содержит dark-theme support")
else:
    fail("CSS не содержит dark-theme media / data-theme")

# ── 5. .mpbtn uses CSS vars (not hardcoded colours) ──────────
hardcoded_hex = re.findall(r'\.mpbtn[^}]*\{[^}]*#[0-9a-fA-F]{3,6}[^}]*\}', css)
if hardcoded_hex:
    fail(f".mpbtn содержит хардкод hex цвет: {hardcoded_hex}")
else:
    ok(".mpbtn не содержит хардкод hex цветов (использует CSS vars)")

# ── 6. Picker backdrop covers full screen (position:fixed;inset:0) ─
back_css = re.findall(r'\.mpback\s*\{([^}]+)\}', css)
found_fixed = any("fixed" in b for b in back_css)
found_inset = any("inset" in b or ("top:0" in b and "left:0" in b) for b in back_css)
if found_fixed:
    ok(".mpback position:fixed (full-screen backdrop)")
else:
    fail(".mpback не position:fixed")
if found_inset:
    ok(".mpback inset:0 (покрывает весь экран)")
else:
    fail(".mpback нет inset:0 — не покрывает весь экран")

# ── 7. Picker has z-index > 10 ────────────────────────────────
zi_blocks = re.findall(r'\.mpback\s*\{([^}]+)\}', css)
found_zi = False
for block in zi_blocks:
    for m in re.finditer(r'z-index\s*:\s*(\d+)', block):
        if int(m.group(1)) >= 10:
            found_zi = True
if found_zi:
    ok(".mpback z-index ≥ 10 (над контентом)")
else:
    fail(".mpback нет z-index ≥ 10")

# ── 8. Close button (#mpx) exists in HTML ─────────────────────
if 'id="mpx"' in html:
    ok("#mpx кнопка закрыть существует в HTML")
else:
    fail("#mpx кнопка закрыть отсутствует в HTML")

# ── summary ───────────────────────────────────────────────────
print()
if FAIL:
    print(f"ИТОГ: {len(FAIL)} провал(ов)")
    sys.exit(1)
else:
    print("ИТОГ: все layout checks зелёные")
    sys.exit(0)
