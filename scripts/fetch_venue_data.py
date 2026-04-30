#!/usr/bin/env python3
"""
Fetch latest LCSD Sports Centre data from CSDI Geoportal WFS.
Updates lcsd_sports_centres.geojson with fresh venue information.

The CSDI Geoportal provides the base venue data (location, name, facilities).
The booking schedule fields (BwfSchedule, BskSchedule, VlbSchedule) must be
merged from the LCSD booking system separately — this script preserves any
existing schedule data when updating.
"""
import json
import urllib.request
import urllib.error
from pathlib import Path

WFS_URL = (
    "https://portal.csdi.gov.hk/server/services/common/"
    "lcsd_rcd_1629267205215_31341/MapServer/WFSServer"
    "?service=wfs&request=GetFeature&typenames=SC"
    "&outputFormat=geojson&count=500"
)

GEOJSON_PATH = Path(__file__).parent.parent / "lcsd_sports_centres.geojson"


def fetch_wfs_data():
    """Download fresh venue data from CSDI Geoportal WFS."""
    print(f"Fetching from: {WFS_URL[:80]}...")
    req = urllib.request.Request(WFS_URL, headers={"User-Agent": "Mozilla/5.0"})
    try:
        response = urllib.request.urlopen(req, timeout=60)
        data = json.loads(response.read())
        features = data.get("features", [])
        print(f"  → Received {len(features)} features from WFS")
        return data
    except urllib.error.HTTPError as e:
        print(f"  → HTTP Error {e.code}: {e.reason}")
        raise
    except Exception as e:
        print(f"  → Fetch failed: {e}")
        raise


def load_existing_data():
    """Load existing GeoJSON to preserve schedule fields."""
    if not GEOJSON_PATH.exists():
        return None
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def merge_schedule_data(fresh_features, existing_data):
    """
    Preserve booking schedule fields from existing data.
    Fresh WFS data has venue info but NOT schedule fields (BwfSchedule etc.).
    We match by GmlID/OBJECTID and carry forward any existing schedule data.
    """
    if existing_data is None:
        return fresh_features

    # Build lookup from existing data keyed by GmlID
    existing_by_gmlid = {}
    for f in existing_data.get("features", []):
        gmlid = f["properties"].get("GmlID")
        if gmlid:
            existing_by_gmlid[gmlid] = f["properties"]

    schedule_keys = {"BwfSchedule", "BskSchedule", "VlbSchedule",
                     "BwfTodaySlots", "BwfTodayCourts",
                     "BwfTomorrowSlots", "BwfTomorrowCourts", "BwfDays"}

    merged = 0
    for f in fresh_features:
        gmlid = f["properties"].get("GmlID")
        if gmlid and gmlid in existing_by_gmlid:
            existing_props = existing_by_gmlid[gmlid]
            for key in schedule_keys:
                if existing_props.get(key):
                    f["properties"][key] = existing_props[key]
                    merged += 1

    if merged > 0:
        print(f"  → Merged {merged} schedule field(s) from existing data")
    return fresh_features


def save_geojson(data):
    """Write updated GeoJSON to file."""
    with open(GEOJSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  → Saved {GEOJSON_PATH}")


def main():
    print("=== LCSD Venue Data Fetcher ===")
    print()

    # Load existing to preserve schedules
    existing = load_existing_data()
    if existing:
        print("Loaded existing GeoJSON (schedule fields will be preserved)")
    else:
        print("No existing GeoJSON found — fresh download only")

    # Fetch fresh base data
    fresh = fetch_wfs_data()

    # Merge schedule data
    features = merge_schedule_data(fresh["features"], existing)
    fresh["features"] = features

    # Save
    save_geojson(fresh)

    print()
    print("Done.")


if __name__ == "__main__":
    main()
