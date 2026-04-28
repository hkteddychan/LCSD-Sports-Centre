# LCSD Sports Centre | 康文署體育館地圖

> Interactive bilingual (EN + 繁體中文) map of all 106 LCSD Sports Centres in Hong Kong

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://hkteddychan.github.io/LCSD-Sports-Centre)
[![Data Source](https://img.shields.io/badge/Data%20Source-CSDI%20Geoportal-blue)](https://portal.csdi.gov.hk/geoportal/?datasetId=lcsd_rcd_1629267205215_31341&lang=zh-hk)
[![Last Updated](https://img.shields.io/badge/Last%20Updated-2026--04--28-orange)]()

## 🌐 Live Demo

**https://hkteddychan.github.io/LCSD-Sports-Centre**

## 📋 Overview

This project provides an interactive web map displaying all **106 LCSD Sports Centres** across Hong Kong's 18 districts. The map is fully **bilingual** (English / Traditional Chinese) and supports real-time filtering by district and text search by name or address.

## 🗂️ Project Structure

```
LCSD-Sports-Centre/
├── index.html          # Main map application (bilingual Leaflet map)
├── lcsd_sports_centres.geojson  # Raw data: 106 sports centres, WGS84
├── README.md           # This file
└── SPEC.md             # Technical specification
```

## ✨ Features

### Map
- **Interactive Leaflet map** with OpenStreetMap tiles
- **106 numbered markers** (1-106) corresponding to each sports centre
- **Cluster-free** — all markers visible at zoom level 11+
- **Info popups** with comprehensive details for each centre

### Language Support
| Mode | Description |
|------|-------------|
| **EN** | English-only labels |
| **繁體** | Traditional Chinese-only labels |
| **EN+中** | Both languages displayed together |

### Filtering & Search
- **District filter** — dropdown with all 18 districts (bilingual names)
- **Text search** — filters by sports centre name (EN/TC) or address
- **Real-time stats** — "Showing X of 106" counter

### Popup Information
Each marker popup displays:
- 🏢 Sports centre name (bilingual)
- 📍 District & full address
- 🕐 Opening hours
- 📞 Telephone & fax number
- 🏀 Facilities (as colored badge tags)
- 🔗 Link to LCSD website

## 📊 Data

### Source
- **Origin:** [CSDI Geoportal](https://portal.csdi.gov.hk/geoportal/?datasetId=lcsd_rcd_1629267205215_31341&lang=zh-hk) — Leisure and Cultural Services Department, Hong Kong SAR Government
- **Format:** WFS GeoJSON via ArcGIS MapServer
- **Update frequency:** When new facilities are added

### WFS Endpoint
```
https://portal.csdi.gov.hk/server/services/common/lcsd_rcd_1629267205215_31341/MapServer/WFSServer?service=wfs&request=GetFeature&typenames=SC&outputFormat=geojson&count=500
```

### Fields (35 properties per feature)
| Field | EN | TC |
|-------|----|----|
| `NameEN` / `NameTC` | Centre name | 體育館名稱 |
| `AddressEN` / `AddressTC` | Full address | 地址 |
| `DistrictEN` / `DistrictTC` | District | 地區 |
| `FacilityTypeEN` / `FacilityTypeTC` | Available facilities | 設施類型 |
| `OpeningHoursEN` / `OpeningHoursTC` | Hours of operation | 開放時間 |
| `TelephoneEN` / `TelephoneTC` | Phone number | 電話 |
| `FaxNumberEN` / `FaxNumberTC` | Fax number | 傳真 |
| `EmailAddressEN` / `EmailAddressTC` | Email | 電郵 |
| `WebsiteEN` / `WebsiteTC` | LCSD facility page | 康文署網頁 |
| `LATITUDE` / `LONGITUDE` | WGS84 coordinates | 坐標 |
| `LASTUPDATE` | Data last updated | 最後更新 |

### Coverage by District
| District | Count | District (TC) |
|----------|-------|---------------|
| Central & Western | 5 | 中西區 |
| Eastern | 6 | 東區 |
| Islands | 5 | 離島 |
| Kowloon City | 5 | 九龍城 |
| Kwai Tsing | 8 | 葵青 |
| Kwun Tong | 9 | 觀塘 |
| North | 5 | 北區 |
| Sai Kung | 5 | 西貢 |
| Sha Tin | 7 | 沙田 |
| Sham Shui Po | 6 | 深水埗 |
| Southern | 5 | 南區 |
| Tai Po | 6 | 大埔 |
| Tseung Kwan O | 1 | 將軍澳 |
| Tsuen Wan | 5 | 荃灣 |
| Tuen Mun | 5 | 屯門 |
| Wan Chai | 3 | 灣仔 |
| Wong Tai Sin | 7 | 黃大仙 |
| Yau Tsim Mong | 6 | 油尖旺 |
| Yuen Long | 7 | 元朗 |

## 🔧 Technical Stack

| Component | Technology |
|-----------|------------|
| Map rendering | [Leaflet.js](https://leafletjs.com/) v1.9.4 (CDN) |
| Map tiles | OpenStreetMap |
| Language | Vanilla JavaScript (no build step) |
| Styling | CSS3 with CSS custom properties |
| Data format | GeoJSON (WGS84 / EPSG:4326) |
| Hosting | GitHub Pages |
| Data access | CSDI Geoportal WFS (ArcGIS MapServer) |

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/hkteddychan/LCSD-Sports-Centre.git
cd LCSD-Sports-Centre

# Serve locally
python3 -m http.server 8000
# Open http://localhost:8000
```

## 🔄 How to Update Data

When LCSD adds new sports centres, refresh the GeoJSON:

```python
import urllib.request, json

url = (
    "https://portal.csdi.gov.hk/server/services/common/"
    "lcsd_rcd_1629267205215_31341/MapServer/WFSServer"
    "?service=wfs&request=GetFeature&typenames=SC"
    "&outputFormat=geojson&count=500"
)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = json.loads(urllib.request.urlopen(req).read())

with open('lcsd_sports_centres.geojson', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

## 📝 Facilities Available

Badminton Courts, Basketball Courts, Bowling Greens, Children's Play Rooms, Fitness Rooms, Table Tennis Tables, Volleyball Courts, Activity Rooms, 5-A-Side Football Pitches, and more.

## 📄 License

Data sourced from Hong Kong SAR Government CSDI Geoportal under the [Government's Open Data Licence](https://data.gov.hk/en/about us/policy/open-license/).

## 🤝 Contributing

Issues and pull requests welcome! If you find incorrect information or want to add features, please open an issue first.