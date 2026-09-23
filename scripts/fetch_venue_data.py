#!/usr/bin/env python3
"""
Fetch latest LCSD Sports Centre data and merge SmartPlay real-time schedules.

Stage 1: Fetch SmartPlay badminton/basketball/volleyball open-data
         (real, 7-day future booking schedule with available courts).
Stage 2: Fetch CSDI WFS for base venue info (location, address, facilities).
Stage 3: Merge schedule data into CSDI features, keyed by Venue_Name.
Stage 4: Write lcsd_sports_centres.geojson.

Schedule fields are JSON-encoded strings to match existing schema
(BwfSchedule / BskSchedule / VlbSchedule as {"date": {"HH:MM": courts}}).
Frontend parses them with JSON.parse() at runtime.
"""
import json
import re
import unicodedata
import urllib.request
from collections import defaultdict
from pathlib import Path

WFS_URL = (
    "https://portal.csdi.gov.hk/server/services/common/"
    "lcsd_rcd_1629267205215_31341/MapServer/WFSServer"
    "?service=wfs&request=GetFeature&typenames=SC"
    "&outputFormat=geojson&count=500"
)

SMARTPLAY_BASE = "https://data.smartplay.lcsd.gov.hk/rest/cms/api/v1/publ/contents/open-data"
SMARTPLAY_SPORTS = {
    "badminton":  ("BwfSchedule", "BwfDays", "BwfTodaySlots", "BwfTodayCourts",
                   "BwfTomorrowSlots", "BwfTomorrowCourts"),
    "basketball": ("BskSchedule", None, None, None, None, None),
    "volleyball": ("VlbSchedule", None, None, None, None, None),
}

GEOJSON_PATH = Path(__file__).parent.parent / "lcsd_sports_centres.geojson"

USER_AGENT = "Mozilla/5.0"


# ─── helpers ───────────────────────────────────────────────────────────────

def http_json(url, timeout=60):
    """Fetch URL and parse JSON."""
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def normalize_name(s):
    """
    Normalize a venue name so CSDI and SmartPlay names align:
      - strip trailing parenthesized suffix (e.g. '荃灣體育館 (毗鄰荃灣西站)' → '荃灣體育館')
      - NFC unicode normalization
      - drop numeric 號 markers ('一號體育館' → '體育館') to collapse 1-of-N vs merged centres
      - collapse parenthesized 南/北 inside the name ('藍田(南)體育館' → '藍田南體育館')
    """
    if not s:
        return ""
    s = re.sub(r"[（(].*?[)）]\s*$", "", s).strip()
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"[一二三四五六七八九十]號", "", s)
    s = re.sub(r"[（(](南|北)[)）]", r"\1", s)
    return s.strip()


# ─── Stage 1: SmartPlay ────────────────────────────────────────────────────

def fetch_smartplay_sport(sport):
    """Fetch one sport's records from SmartPlay, return list of dicts."""
    url = f"{SMARTPLAY_BASE}/{sport}/file"
    print(f"  → Fetching SmartPlay/{sport}...")
    data = http_json(url, timeout=120)
    print(f"    {len(data):,} records")
    return data


def build_schedule_index(records):
    """
    Aggregate SmartPlay records by (venue_tc, date) → {HH:MM: total_courts}.
    Also return a {normalized_name: original_name} map for matching to CSDI.
    Each (venue, date, time, hall) row adds its Available_Courts to the same slot.
    """
    by_venue_date = defaultdict(dict)  # venue -> {date: {HH:MM: courts}}
    norm_to_original = {}

    for r in records:
        venue_tc = (r.get("Venue_Name_TC") or "").strip()
        venue_en = (r.get("Venue_Name_EN") or "").strip()
        date = r.get("Available_Date") or ""
        start = r.get("Session_Start_Time") or ""
        try:
            courts = int(r.get("Available_Courts", 0) or 0)
        except (TypeError, ValueError):
            courts = 0

        if not venue_tc or not date or not start:
            continue

        venue_bucket = by_venue_date[venue_tc]
        date_bucket = venue_bucket.get(date)
        if date_bucket is None:
            date_bucket = {}
            venue_bucket[date] = date_bucket
        date_bucket[start] = date_bucket.get(start, 0) + courts
        if venue_tc:
            norm_to_original.setdefault(normalize_name(venue_tc), venue_tc)
        if venue_en:
            norm_en = re.sub(r"\s*\(.*?\)\s*$", "", venue_en).strip()
            norm_to_original.setdefault(norm_en, venue_tc)

    return by_venue_date, norm_to_original


def build_schedule_payload(by_venue_date_tc):
    """
    For a CSDI feature, look up its venue_tc in the index and produce:
      - BwfSchedule-style payload: {date: {HH:MM: courts}, ...}
      - BwfDays-style payload:    {date: {"courts": N, "slots": N}, ...}
      - Today/Tomorrow slots & courts
    Returns dict with keys schedule_json, days_json, today_slots, today_courts,
    tomorrow_slots, tomorrow_courts.
    """
    all_dates = sorted(by_venue_date_tc.keys())
    if not all_dates:
        return {
            "schedule_json": "{}",
            "days_json":     "{}",
            "today_slots":   0,
            "today_courts":  0,
            "tomorrow_slots": 0,
            "tomorrow_courts": 0,
        }

    # Anchor "today" on the earliest date in the SmartPlay window —
    # SmartPlay only exposes a 7-day forward window so the first date IS today.
    today_iso = all_dates[0]
    tomorrow_iso = all_dates[1] if len(all_dates) > 1 else today_iso

    schedule = {}
    days = {}
    for date in all_dates:
        slots = by_venue_date_tc[date]
        schedule[date] = {hh: int(v) for hh, v in slots.items()}
        total_courts = sum(int(v) for v in slots.values())
        slots_with_avail = sum(1 for v in slots.values() if int(v) > 0)
        days[date] = {"courts": total_courts, "slots": slots_with_avail}

    today = by_venue_date_tc.get(today_iso, {})
    tomorrow = by_venue_date_tc.get(tomorrow_iso, {})

    return {
        "schedule_json": json.dumps(schedule, ensure_ascii=False, sort_keys=True),
        "days_json":     json.dumps(days, ensure_ascii=False, sort_keys=True),
        "today_slots":   sum(1 for v in today.values() if int(v) > 0),
        "today_courts":  sum(int(v) for v in today.values()),
        "tomorrow_slots":   sum(1 for v in tomorrow.values() if int(v) > 0),
        "tomorrow_courts":  sum(int(v) for v in tomorrow.values()),
    }


# ─── Stage 2: CSDI WFS ─────────────────────────────────────────────────────

def fetch_csdi_wfs():
    print(f"  → Fetching CSDI WFS venues...")
    data = http_json(WFS_URL, timeout=120)
    features = data.get("features", [])
    print(f"    {len(features)} features")
    return data


# ─── Stage 3: merge ────────────────────────────────────────────────────────

def attach_schedules(features, sports_data):
    """
    For each CSDI feature, attach schedule fields from each SmartPlay sport.
    sports_data: {sport_key: (by_venue_date_tc, norm_to_original)}
    """
    stats = {}
    for sport, (sched_field, days_field, today_s, today_c, tom_s, tom_c) in SMARTPLAY_SPORTS.items():
        by_venue_date, norm_to_original = sports_data[sport]
        matched = 0
        schedule_total = 0
        court_total = 0
        for f in features:
            props = f["properties"]
            name_tc = (props.get("NameTC") or "").strip()
            name_en = (props.get("NameEN") or "").strip()
            key = None
            if name_tc and name_tc in by_venue_date:
                key = name_tc
            elif name_tc and normalize_name(name_tc) in norm_to_original:
                key = norm_to_original[normalize_name(name_tc)]
            elif name_en:
                en_norm = re.sub(r"\s*\(.*?\)\s*$", "", name_en).strip()
                if en_norm in norm_to_original:
                    key = norm_to_original[en_norm]

            if key is None:
                # No schedule for this venue — clear stale fields
                for k in (sched_field, days_field, today_s, today_c, tom_s, tom_c):
                    if k and k in props:
                        props[k] = "" if k.endswith("Schedule") or (k and k.endswith("Days")) else 0
                continue

            payload = build_schedule_payload(by_venue_date[key])
            props[sched_field] = payload["schedule_json"]
            if days_field:
                props[days_field] = payload["days_json"]
            if today_s:
                props[today_s] = payload["today_slots"]
            if today_c:
                props[today_c] = payload["today_courts"]
            if tom_s:
                props[tom_s] = payload["tomorrow_slots"]
            if tom_c:
                props[tom_c] = payload["tomorrow_courts"]
            matched += 1
            schedule_total += sum(len(v) for v in by_venue_date[key].values())
            court_total += sum(sum(int(x) for x in v.values())
                               for v in by_venue_date[key].values())

        stats[sport] = {
            "matched_venues": matched,
            "total_slots":    schedule_total,
            "total_courts":   court_total,
        }
        print(f"  → {sport}: matched {matched}/{len(features)} venues, "
              f"{schedule_total:,} slots, {court_total:,} court-units")
    return stats


# ─── Stage 4: write ────────────────────────────────────────────────────────

def save_geojson(data):
    with open(GEOJSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  → Saved {GEOJSON_PATH}")


# ─── main ──────────────────────────────────────────────────────────────────

def main():
    print("=== LCSD Sports Centre + SmartPlay Fetcher ===")
    print()

    # Stage 1: SmartPlay
    print("[Stage 1] Fetching SmartPlay open-data (badminton/basketball/volleyball)...")
    sports_data = {}
    sport_stats = {}
    for sport in SMARTPLAY_SPORTS.keys():
        records = fetch_smartplay_sport(sport)
        sports_data[sport] = build_schedule_index(records)
        sport_stats[sport] = len(records)

    # Stage 2: CSDI WFS
    print("\n[Stage 2] Fetching CSDI WFS base venues...")
    csdi_data = fetch_csdi_wfs()

    # Stage 3: merge
    print("\n[Stage 3] Merging schedules into CSDI features...")
    merge_stats = attach_schedules(csdi_data["features"], sports_data)

    # Stage 4: write
    print("\n[Stage 4] Writing GeoJSON...")
    save_geojson(csdi_data)

    # Summary
    print("\n=== Summary ===")
    for sport, count in sport_stats.items():
        m = merge_stats[sport]
        print(f"  {sport:11s}: {count:>6,} raw records → {m['matched_venues']:>3}/{len(csdi_data['features'])} venues matched, "
              f"{m['total_slots']:>5,} slots, {m['total_courts']:>5,} court-units")
    print("Done.")


if __name__ == "__main__":
    main()
