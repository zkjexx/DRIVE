import json

with open("qc_barangays.geojson", "r", encoding="utf-8") as f:
    data = json.load(f)

count = 0

for feature in data["features"]:

    geom = feature.get("geometry", {}).get("type")

    props = feature.get("properties", {})

    name = (
        props.get("name")
        or props.get("Name")
        or props.get("barangay")
        or props.get("Barangay")
    )

    if geom in ["Polygon", "MultiPolygon"]:
        print(name, geom)
        count += 1

print("\nPolygon count:", count)