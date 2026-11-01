# Map shapes in this folder

All four files are simplified with mapshaper from public sources. They are used only to draw the map; no statistics are read from them.

| File | What it holds | Made from |
|---|---|---|
| `prefs_s.geojson` | 46 prefectures (all except Tokyo) | `japan.geojson` from the GitHub project dataofjapan/land |
| `tokyo_s.geojson` | the outline of Tokyo without its far islands | same file, prefecture 13 |
| `wards_s.geojson` | Tokyo's 23 wards | niiyz/JapanCityGeoJson, which is built from MLIT's 国土数値情報 行政区域データ (N03) |
| `tr_s.geojson` | Tokyo outside the 23 wards | the Tokyo outline minus the wards |

Credit line for the ward shapes, as the ministry asks: 「国土数値情報（行政区域データ）」（国土交通省）を加工して作成.

Please check the two GitHub projects for their own licence terms before reusing these files elsewhere.
