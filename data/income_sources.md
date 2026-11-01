# income.json: sources and method

**Survey:** 令和5年住宅・土地統計調査 (2023 Housing and Land Survey), Statistics Bureau of Japan, on e-Stat.
The tables come from 確報集計 → 住宅及び世帯に関する基本集計 → 全国・都道府県・市区町村 (tstat 000001207800).

## Tables used

| Level | Table | statInfId | URL |
|---|---|---|---|
| Prefectures, Japan total, 特別区部 | 第40-1表 世帯の年間収入階級(11区分)、世帯人員(7区分)、住宅の所有の関係(6区分)別主世帯数－全国、都道府県、21大都市 | 000040209911 | https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040209911&fileKind=0 |
| 23 special wards | 第43-4表 世帯の年間収入階級(10区分)、住宅の所有の関係(5区分)別主世帯数、１世帯当たり人員、１世帯当たり居住室数及び１世帯当たり居住室の畳数－全国、都道府県、市区町村 | 000040209921 | https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040209921&fileKind=0 |

The `fileKind=0` link returns an .xlsx file, not a CSV.

Rows used: 住宅の所有の関係 = 総数 (all tenure types). For 40-1, the column used is 世帯人員 = 総数.

## Household concept
**主世帯 (main households).** Both tables count 主世帯数. They do not count 普通世帯.

## How 不詳 (income not stated) was handled
- **Prefectures (40-1):** stated = 総数 − 99_不詳. 不詳 is left out of both the top and the bottom of each share. The script checks that brackets 01–11 add up to `stated` (allowing for the source's rounding to the nearest 100).
- **Wards (43-4):** this table has no 不詳 row. Its 総数 still includes 不詳. So stated = the sum of all listed brackets, and `unknown` = 総数 − stated.

## Brackets
- 40-1 has 11 classes: … 09 = 1000～1500万円未満, 10 = 1500～2000万円未満, 11 = 2000万円以上, plus 99 不詳.
- 43-4 (the ward table) has 10 classes, and its top class is **1500万円以上**. The 1500–2000 and 2000+ split **is not published at ward level** in 2023. The 2018 ward table (平成30年 第44-4表, statInfId 000031865704, 9 classes) was also checked. It also stops at 1500万円以上. So no year gives 2000万円以上 by ward.
  → For wards: `b1500p` is given, `b1500_2000` and `b2000p` are null, `over10` and `over15` are real 2023 values, and `over20` is **null**. No ward numbers were made up.

## Derived regions
- `JP-13-REST` (Tokyo outside the 23 wards: Tama area and islands) = 東京都 minus 13100 特別区部. Both rows come from table 40-1, which has all brackets. So REST has a real over20.
- `aggregates.JP-13-KUBU` = 特別区部 (all 23 wards together) from 40-1. It has a real over20 of 2.41 %.
- Cross-check: the 23 ward rows from 43-4 add up to the 特別区部 row in 40-1 (stated 4,820,490 vs 4,820,500; 1000–1500: 496,940 vs 496,900; 1500+: 265,590 vs 265,600). The small gaps come from rounding.

## Check figures (shares of households with income stated)

| | over10 (≥1000万) | over15 (≥1500万) | over20 (≥2000万) |
|---|---|---|---|
| Japan | 8.15 % | 2.11 % | 0.84 % |
| Tokyo (all) | 14.45 % | 4.75 % | 2.02 % |
| Tokyo 23 wards together | 15.8 % | 5.51 % | 2.41 % |
| Tokyo outside the 23 wards | 10.99 % | 2.82 % | 1.03 % |
| 千代田区 | 38.3 % | 16.9 % | n/a |
| 港区 | 36.9 % | 20.4 % | n/a |
| 中央区 | 33.9 % | 14.8 % | n/a |
| 渋谷区 | 22.3 % | 8.6 % | n/a |

The Japan figures are a little **below** the rough targets in the brief (about 1 % / 3 % / 11–13 %). The rows are correct: they are 主世帯数 (households, not housing units), 不詳 is excluded, and the brackets add up. The gap comes from the survey itself. In this survey, people tick an income bracket for their household, and the results run lower than the Comprehensive Survey of Living Conditions (国民生活基礎調査), which is probably where the brief's targets came from. Tokyo (2.0 %) is the highest prefecture for over20. Next come 神奈川 (1.08 %) and 愛知 (0.87 %). The lowest are 鳥取, 高知 and 鹿児島 (about 0.34 %).

## Files
- Downloads: `dl_hls/t000040209911.xlsx`, `dl_hls/t000040209921.xlsx`, `dl_hls/h30_000031865704.xlsx` (2018 table, only used to check its brackets)
- Scripts: `scripts/xlsx.py` (an xlsx reader that needs only the standard library), `scripts/build_income.py`, `scripts/parse_list.py`
- To rebuild: `python3 -I scripts/build_income.py dl_hls/t000040209911.xlsx dl_hls/t000040209921.xlsx income.json`
