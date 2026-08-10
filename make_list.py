"""Write the shortlist out as plain text, grouped by site.

Serhii forwards these links to agents and to Violeta, so the output has to
survive being pasted into WhatsApp: no tables, no markdown, one link per line
with just enough on the line above to know what it is.
"""
import sqlite3
import pathlib
from collections import defaultdict

DB = pathlib.Path(r"E:\MY\casa\data\casa.db")
OUT_DIR = pathlib.Path(r"E:\MY\casa\share")

SITE_NAMES = {
    "imovirtual.com": "Imovirtual",
    "iadportugal.pt": "IAD Portugal",
    "supercasa.pt": "SuperCasa",
    "era.pt": "ERA",
    "idealista.pt": "Idealista",
    "casa.sapo.pt": "Casa SAPO",
    "kwportugal.pt": "KW Portugal",
    "remax.pt": "RE/MAX",
    "century21.pt": "Century 21",
}


def money(v):
    return f"{v:,.0f}".replace(",", " ") + " EUR" if v else "preco sob consulta"


def line(r):
    bits = [money(r["price_eur"])]
    if r["bedrooms"]:
        bits.append(f"T{int(r['bedrooms'])}")
    if r["bathrooms"]:
        bits.append(f"{int(r['bathrooms'])} wc")
    if r["area_m2"]:
        bits.append(f"{int(r['area_m2'])} m2")
    if r["land_area_m2"]:
        bits.append(f"terreno {int(r['land_area_m2']):,}".replace(",", " ") + " m2")
    where = r["concelho"] or r["district"] or "?"
    return f"{where} - " + ", ".join(bits)


def main():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT domain,url,price_eur,area_m2,land_area_m2,bedrooms,bathrooms,"
        "concelho,district FROM listings WHERE url IS NOT NULL "
        "ORDER BY domain, district IS NULL, district, price_eur IS NULL, price_eur"
    ).fetchall()

    by_site = defaultdict(list)
    for r in rows:
        by_site[r["domain"]].append(r)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = [f"CASAS - lista para ver ({len(rows)} anuncios)", ""]

    order = sorted(by_site, key=lambda d: -len(by_site[d]))
    for dom in order:
        items = by_site[dom]
        out.append("=" * 46)
        out.append(f"{SITE_NAMES.get(dom, dom)}  ({len(items)})")
        out.append("=" * 46)
        for i, r in enumerate(items, 1):
            out.append(f"{i}. {line(r)}")
            out.append(f"   {r['url']}")
        out.append("")

    txt = "\n".join(out)
    (OUT_DIR / "lista_casas.txt").write_text(txt, encoding="utf-8")

    # links only - for pasting a bare batch to one agent
    bare = []
    for dom in order:
        bare.append(f"--- {SITE_NAMES.get(dom, dom)} ---")
        bare += [r["url"] for r in by_site[dom]]
        bare.append("")
    (OUT_DIR / "lista_links.txt").write_text("\n".join(bare), encoding="utf-8")

    print(f"{len(rows)} links, {len(by_site)} sites")
    for dom in order:
        print(f"  {SITE_NAMES.get(dom, dom):14} {len(by_site[dom])}")


if __name__ == "__main__":
    main()
