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
    "dup_of", "dup_note", "added_by", "added_at",
    "access_score", "dist_city_km", "city_name",
    "town_lat", "town_lon",     # the town, never the house - see scoring notes
    "listing_status", "listing_checked",
]


def excerpt(txt):
    if not txt:
        return ""
    t = " ".join(txt.split())
    return t[:320] + ("..." if len(t) > 320 else "")



def hunt_twins(con):
    """Mark fresh duplicate suspects; never touch confirmed hand-set marks."""
    import math
    rows = list(con.execute(
        "SELECT id,domain,concelho,price_eur,area_m2,bedrooms,lat,lon,"
        "dup_of,dup_note FROM listings"))

    def km(a, b):
        R = 6371
        p1, p2 = math.radians(a[0]), math.radians(b[0])
        h = (math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2)
             * math.sin(math.radians(b[1] - a[1]) / 2) ** 2)
        return 2 * R * math.asin(math.sqrt(h))

    def close(a, b, tol):
        return bool(a and b) and abs(a - b) / max(a, b) <= tol

    fresh = 0
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            if a[8] or b[8] or a[9] or b[9]:      # уже размечены рукой
                continue
            geo = (a[6] and b[6] and km((a[6], a[7]), (b[6], b[7])) < 0.25)
            shape = (close(a[3], b[3], 0.09) and close(a[4], b[4], 0.06)
                     and a[5] and a[5] == b[5])
            named = (a[1] != b[1] and (a[2] or "").lower() == (b[2] or "").lower()
                     and shape)
            if (geo and shape) or named:
                note = f"дубль? похож на #{b[0]} — сверить фото и адрес"
                con.execute("UPDATE listings SET dup_note=? WHERE id=?",
                            (note, a[0]))
                con.execute("UPDATE listings SET dup_note=? WHERE id=?",
                            (f"дубль? похож на #{a[0]} — сверить фото и адрес", b[0]))
                fresh += 1
    if fresh:
        con.commit()
        print(f"новых подозрений на дубль: {fresh}")

def main():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    hunt_twins(con)                    # каждый rebuild сам ищет двойников
    rows = con.execute(
        f"SELECT {','.join(COLS)}, description FROM listings "
        "WHERE url IS NOT NULL "
        "ORDER BY price_eur IS NULL, price_eur"   # unpriced ones sink to the end
    ).fetchall()

    out = []
    for r in rows:
        h = {c: r[c] for c in COLS if r[c] not in (None, "")}
        h["id"] = r["id"]
        # description stays in the database - the card does not show it
        out.append(h)

    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    coords = sum(1 for h in out if h.get("lat"))
    print(f"{len(out)} houses, {coords} with coords, {OUT.stat().st_size//1024} KB")


if __name__ == "__main__":
    main()
