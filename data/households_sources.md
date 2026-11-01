# Household counts: sources

All numbers come from one e-Stat table. No other source was used.

- **Survey:** 令和2年国勢調査 (2020 Population Census), 人口等基本集計. Figures as of 2020-10-01.
- **Table:** 第1-1表 男女別人口，世帯の種類別世帯数及び世帯人員並びに2015年（平成27年）の人口（組替）…人口密度－全国，都道府県，市区町村（2000年（平成12年）市区町村含む）
- **statInfId:** 000032142402 (published 2021-11-30)
- **Download URL:** https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032142402&fileKind=0 (an Excel file, `b01_01.xlsx`)
- **Column used:** 世帯数 → 世帯の種類 → `1_一般世帯` (general households). This is the 18th column in the sheet. We did not use `0_総数` (all households) or `2_施設等の世帯` (institutional households).
- **Rows used:** the rows whose 2020 area code (`2020年_地域コード`) is 00000 (Japan), NN000 (each prefecture), or 13101–13123 (the 23 special wards). Rows for old pre-merger towns (names starting with `旧：`) were skipped.
- **JP-13-REST** = Tokyo total minus the sum of the 23 wards. It covers the Tama area and the islands.

## Check totals

| Check | Value |
|---|---|
| National total of general households | 55,704,949 |
| Tokyo total (JP-13) | 7,216,650 |
| Sum of the 23 wards | 5,208,438 |
| Tokyo rest (JP-13-REST) | 2,008,212 |

Cross-checks:
- The 47 prefectures add up exactly to the national total.
- The 23 wards add up exactly to the table's own 特別区部 row (code 13100): 5,208,438.

Scripts: `realdata/scripts/xlsx_dump.py` turns the xlsx into CSV using only the standard library. `realdata/scripts/build_households.py` builds the JSON.
