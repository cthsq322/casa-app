"""Two addresses: one to work on, one to test on.

Serhii, Violeta and Milena are using the site all day. Pushing half-finished
work to the address they have open is what broke their afternoon, so the
candidate build goes to /next/ instead. It is the same site, same data file,
its own copy of the page - nobody has it open, and it can be as broken as it
needs to be while a change is being tried.

    python release.py stage   - publish the working files to /next/
    python release.py live    - promote /next/ to the real address

Nothing reaches the real address except through `live`, and `live` refuses to
run unless the tests have passed against /next/ first.
"""
import os
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
NEXT = HERE / "next"
STAMP = HERE / ".tested"
FILES = ["index.html", "data.json", "plan.json", "version.txt",
         "frases.html", "lista.html"]

LIVE_URL = "https://cthsq322.github.io/casa-app/"
NEXT_URL = "https://cthsq322.github.io/casa-app/next/"


def run(*args):
    return subprocess.run(args, cwd=HERE, capture_output=True, text=True)


def syntax_ok(path):
    """A broken string literal takes the whole page down - check before shipping."""
    import re, tempfile
    html = pathlib.Path(path).read_text(encoding="utf-8")
    blocks = re.findall(r"<script>(.*?)</script>", html, re.S)
    for i, js in enumerate(blocks):
        tmp = pathlib.Path(tempfile.gettempdir()) / f"casa_check_{i}.js"
        tmp.write_text(js, encoding="utf-8")
        r = subprocess.run(["node", "--check", str(tmp)], capture_output=True, text=True)
        tmp.unlink(missing_ok=True)
        if r.returncode:
            print("СИНТАКСИС СЛОМАН:")
            print(r.stderr[:600])
            return False
    return True


def stage():
    if not syntax_ok(HERE / "index.html"):
        raise SystemExit("не собираю: скрипт не парсится")
    NEXT.mkdir(exist_ok=True)
    for f in FILES:
        src = HERE / f
        if src.exists():
            shutil.copy2(src, NEXT / f)
    # stamp the copy, never the file the live site is built from
    env = dict(os.environ, CASA_BUILD_DIR=str(NEXT))
    subprocess.run([sys.executable, str(HERE / "deploy.py")],
                   cwd=HERE, env=env, check=True)
    # the copy under /next/ must not tell phones on the real site to reload
    idx = NEXT / "index.html"
    idx.write_text(idx.read_text(encoding="utf-8")
                   .replace("<title>Дома</title>", "<title>Дома · тест</title>"),
                   encoding="utf-8")
    if STAMP.exists():
        STAMP.unlink()
    print("собрано в next/  ->  " + NEXT_URL)
    print("дальше: прогнать тесты против next/, потом release.py live")


def live():
    if not syntax_ok(NEXT / "index.html"):
        raise SystemExit("не переношу: скрипт в next/ не парсится")
    if not STAMP.exists():
        print("СТОП: тесты против /next/ ещё не отмечены как зелёные.")
        print("Прогони их и создай файл .tested, иначе на рабочий адрес ничего не пойдёт.")
        return 1
    for f in FILES:
        src = NEXT / f
        if src.exists():
            shutil.copy2(src, HERE / f)
    STAMP.unlink()
    print("перенесено на рабочий адрес  ->  " + LIVE_URL)
    print("осталось: git add -A && git commit && git push")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stage"
    sys.exit(live() if cmd == "live" else stage())
