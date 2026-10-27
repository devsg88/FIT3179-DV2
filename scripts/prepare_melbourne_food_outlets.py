"""Extract 2024 food outlets and matching point geometry from the supplied CLUE exports."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "business-establishments-with-address-and-industry-classification"
CATEGORIES = {
    "4511": "Cafes and restaurants",
    "4512": "Takeaway food",
    "4110": "Supermarkets and groceries",
    "4129": "Other specialised food shops",
    "4122": "Fruit and vegetable shops",
}


def key(name, address, code):
    return (name.strip(), address.strip(), str(code).strip())


with (ROOT / f"{SOURCE}.csv").open(encoding="utf-8-sig", newline="") as source:
    selected = [
        row for row in csv.DictReader(source)
        if row["Census year"] == "2024" and row["Industry (ANZSIC4) code"] in CATEGORIES
    ]

rows = []
by_key = {}
for row in sorted(selected, key=lambda r: (r["Industry (ANZSIC4) code"], r["Trading name"], r["Business address"])):
    identity = key(row["Trading name"], row["Business address"], row["Industry (ANZSIC4) code"])
    if identity in by_key:
        raise ValueError(f"Duplicate establishment requires review: {identity}")
    longitude, latitude = float(row["Longitude"]), float(row["Latitude"])
    assert 144 < longitude < 146 and -39 < latitude < -37
    outlet = {
        "outlet_id": f"food-{len(rows) + 1:04d}",
        "year": 2024,
        "name": row["Trading name"],
        "address": row["Business address"],
        "neighbourhood": row["CLUE small area"],
        "industry_code": row["Industry (ANZSIC4) code"],
        "category": CATEGORIES[row["Industry (ANZSIC4) code"]],
        "longitude": longitude,
        "latitude": latitude,
    }
    rows.append(outlet)
    by_key[identity] = outlet

topology = json.loads((ROOT / "topojson files" / f"{SOURCE}.json").read_text(encoding="utf-8-sig"))
assert topology["type"] == "Topology" and "transform" not in topology
geometries = []
matched = set()
for geometry in topology["objects"][SOURCE]["geometries"]:
    properties = geometry["properties"]
    if str(properties["census_year"]) != "2024":
        continue
    identity = key(properties["trading_name"], properties["business_address"], properties["industry_anzsic4_code"])
    if identity not in by_key:
        continue
    outlet = by_key[identity]
    assert identity not in matched and geometry["type"] == "Point"
    assert abs(geometry["coordinates"][0] - outlet["longitude"]) < 1e-7
    assert abs(geometry["coordinates"][1] - outlet["latitude"]) < 1e-7
    matched.add(identity)
    geometries.append({
        "type": "Point",
        "coordinates": geometry["coordinates"],
        "properties": {"outlet_id": outlet["outlet_id"]},
    })
assert len(matched) == len(rows), "Every CSV outlet must have matching point geometry."

with (ROOT / "Formatted Data" / "melbourne_food_outlets_2024.csv").open("w", encoding="utf-8", newline="") as output:
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

output_topology = {
    "type": "Topology",
    "objects": {"food_outlets": {"type": "GeometryCollection", "geometries": geometries}},
    "arcs": [],
}
(ROOT / "topojson files" / "Melbourne_food_outlets_2024.json").write_text(
    json.dumps(output_topology, separators=(",", ":")), encoding="utf-8"
)
print(f"Extracted {len(rows):,} outlets, all matched to the supplied TopoJSON.")
print(dict(Counter(row["category"] for row in rows)))
