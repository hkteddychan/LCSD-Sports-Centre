# LCSD Sports Centre Map — Technical Specification

## 1. Overview

**Project name:** LCSD-Sports-Centre
**Type:** Interactive web map (single HTML file + GeoJSON data file)
**Summary:** Bilingual (EN + 繁體中文) Leaflet map showing all 106 LCSD Sports Centres in Hong Kong, with district filtering and text search.
**Target users:** General public looking for LCSD sports facilities in Hong Kong.

---

## 2. Data Source

### Origin
- **Portal:** CSDI Geoportal (https://portal.csdi.gov.hk)
- **Dataset ID:** `lcsd_rcd_1629267205215_31341`
- **Dataset name:** 體育館 (Sports Centres)
- **Providing agency:** 康樂及文化事務署 (LCSD)

### WFS Endpoint
```
https://portal.csdi.gov.hk/server/services/common/lcsd_rcd_1629267205215_31341/MapServer/WFSServer?service=wfs&request=GetFeature&typenames=SC&outputFormat=geojson&count=500
```

### Data format
- GeoJSON (RFC 7946)
- CRS: WGS84 (EPSG:4326)
- Geometry type: Point
- Features: 106 sports centres

### Properties (35 fields)
See README.md Section "Data > Fields" for full table.

---

## 3. Visual & Rendering Specification

### Layout
- **Header:** Dark blue gradient bar (#1a237e → #283593) with title and language toggle
- **Controls:** Light gray strip with district dropdown + search input + stats counter
- **Map:** Full viewport height minus header/controls (~100vh - 110px)

### Map
- **Library:** Leaflet.js v1.9.4 via CDN (unpkg)
- **Tile provider:** OpenStreetMap standard tile layer
- **Initial view:** Centre on Hong Kong (22.35, 114.18), zoom level 11
- **Attribution:** OSM + LCSD data source

### Markers
- **Type:** Leaflet divIcon (custom HTML markers)
- **Shape:** 24×24px circle, #3949ab fill, 2.5px white border, shadow
- **Label:** Centered white digit (1–106), font-size 10px, bold
- **Hover:** Scale 1.2×, darker fill (#1a237e)
- **Click:** Opens popup

### Popup
- **Style:** Rounded corners (10px), drop shadow
- **Width:** min-width 280px
- **Fields:** Name (bold header), district, address, hours, tel, fax, facilities tags, website link
- **Facility tags:** #e8eaf6 background, #3949ab text, rounded pill badges

### Color Palette
| Element | Color |
|---------|-------|
| Header gradient start | #1a237e |
| Header gradient end | #283593 |
| Accent / active elements | #3949ab |
| Marker fill | #3949ab |
| Marker hover | #1a237e |
| Facility tag bg | #e8eaf6 |
| Text primary | #333 |
| Text secondary | #555 |
| Control bar | #f5f5f5 |
| Border | #ccc |

### Typography
- Font stack: `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- Header title: 18px, weight 600
- Popup values: 13px
- Facility tags: 11px
- Stats: 12px

---

## 4. Interaction Specification

### Language Toggle
- Three buttons: EN | 繁體 | EN+中
- Active button has white background + dark text
- Switching language updates: title, district dropdown options, popup content, stats label
- EN+中 mode shows both languages separated by " / "

### District Filter
- Dropdown populated from GeoJSON properties (19 districts including "All")
- Bilingual district names
- Filters markers in real-time (show/hide based on DistrictEN match)

### Text Search
- Filters by: NameEN, NameTC, AddressEN, AddressTC (case-insensitive substring match)
- Real-time filtering as user types
- Combines with district filter (AND logic)

### Stats Counter
- Format: "Showing X of 106"
- Label language changes with language toggle

---

## 5. File Structure

```
LCSD-Sports-Centre/
├── index.html               # Main app (HTML + CSS + JS, ~16KB)
├── lcsd_sports_centres.geojson   # Raw data (~228KB, 106 features)
├── README.md                # User-facing documentation
└── SPEC.md                  # This technical specification
```

### index.html Structure
- Inline CSS in `<style>` block (no external CSS files needed)
- Inline JavaScript in `<script>` block at bottom of `<body>`
- Loads Leaflet from CDN
- Fetches GeoJSON via fetch() on page load

---

## 6. Deployment

### GitHub Pages
- Repository: https://github.com/hkteddychan/LCSD-Sports-Centre
- Branch: `main`
- Published URL: https://hkteddychan.github.io/LCSD-Sports-Centre
- Files served from repo root

### GitHub Pages Config
- Source: `main` branch, root folder
- No custom domain
- No Jekyll processing needed (pure static HTML/JSON)

---

## 7. Compatibility

- **Browsers:** Modern browsers (Chrome, Firefox, Safari, Edge) — last 2 versions
- **Mobile:** Responsive design, works on iOS/Android browsers
- **No IE11 support** (uses CSS gap, flexwrap, ES6 features)
- **No build step required** — pure HTML/JS/CSS, no bundler

---

## 8. Known Limitations

1. **No offline support** — requires internet to load Leaflet CDN + tile layer + GeoJSON
2. **Marker overlap** — at city centre zoom levels, markers may visually overlap; Leaflet's default z-index ordering applies
3. **Static data** — GeoJSON is fetched on page load; if source data updates, local copy becomes stale
4. **Facility count fields** (`NoOfFitnessRoomsEN`, etc.) are mostly null in source data and not displayed
5. **Tseung Kwan O** has only 1 sports centre in dataset

---

## 9. Change Log

### 2026-04-28 — Initial release
- 106 sports centres from CSDI Geoportal WFS
- Bilingual EN/TC map with district filter and search
- GitHub Pages hosting at https://hkteddychan.github.io/LCSD-Sports-Centre