"""Rebuild web_static/data.json from casa.db.

The static app reads this one file, so everything the page shows has to be in
here - including lat/lon, which the route view needs to order stops and open
the day in Google Maps.
"""
import json
import sqlite3
import pathlib

DB = pathlib.Path(r"E:\MY\casa\data\casa.db")
OUT = pathlib.Path(__file__).parent / "data.json"

COLS = [
    "id", "url", "title", "price_eur", "area_m2", "land_area_m2",
    "bedrooms", "bathrooms", "energy_class", "year_built",
    "concelho", "freguesia", "district",
    "lat", "lon", "elevation_m", "elevation_relative_m",
    "nearest_building_m", "dist_lisbon_km",
    "agent_phone", "whatsapp", "agency_name",
    "desc_blockers", "desc_goods", "desc_rooms",
    "auto_score", "score_parts", "price_per_m2",
    "first_photo_url", "photo_count",
]


def excerpt(txt):
    if not txt:
        return ""
    t = " ".join(txt.split())
    return t[:320] + ("..." if len(t) > 320 else "")


def main():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        f"SELECT {','.join(COLS)}, description FROM listings "
        "WHERE url IS NOT NULL "
        "ORDER BY price_eur IS NULL, price_eur"   # unpriced ones sink to the end
    ).fetchall()

    out = []
    for r in rows:
        h = {c: r[c] for c in COLS if r[c] not in (None, "")}
        h["id"] = r["id"]
        ex = excerpt(r["description"])
        if ex:
            h["excerpt"] = ex
        out.append(h)

    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    coords = sum(1 for h in out if h.get("lat"))
    print(f"{len(out)} houses, {coords} with coords, {OUT.stat().st_size//1024} KB")


if __name__ == "__main__":
    main()
