# Japan heat map

An interactive map of Japan that counts how many households could realistically buy an electric Porsche. One HTML file with no server behind it.

Live page: https://heatmap.kanic1225.workers.dev

## How it works

Every region (46 prefectures, Tokyo's 23 wards, and Tokyo outside the wards) starts with its number of households. Four switches, called "doors", each keep only a share of them:

| Door | Meaning | Data |
|---|---|---|
| Can park | has a parking space | mock |
| Can charge | that space can take a home charger | mock |
| Renewal soon | likely to replace the car within 24 months | mock |
| Can pay | household income over ¥10m / ¥15m / ¥20m (slider) | real |

Households and the income shares are real. The 69 Porsche locations drawn as dots are real. The other three doors are placeholder numbers until the team collects the real ones. The page says so in one line at the bottom.

## Folder layout

| Path | What it is |
|---|---|
| `dist/index.html` | the finished page, deployed as is |
| `index.artifact.html` | the same page without the deploy wrapper |
| `tools/template.html` | the page's HTML, CSS and JavaScript (D3) |
| `tools/gen.py` | fills the template with data and writes the page |
| `tools/build.sh` | runs the whole build |
| `tools/make_dist.py` | makes the `dist/` copy |
| `data/` | real inputs: households, income shares, dealer list, plus notes on where each came from |
| `geo/` | simplified map shapes |
| `NOTES.md` | the long notes: every decision, source and formula |

## Build it yourself

You need Python 3. Node is optional (it only syntax-checks the page) and Google Chrome is optional (it only renders preview screenshots).

```
bash tools/build.sh
```

This rewrites `index.artifact.html` and `dist/index.html`. The placeholder numbers come from a fixed random seed, so the output is the same every time.

## Deploy

The live page is a Cloudflare Worker that serves the `dist/` folder as static files. With your own Cloudflare account:

```
npx wrangler deploy
```

## Data sources

- Households: 2020 Population Census, general households (e-Stat).
- Income shares: 2023 Housing and Land Survey (e-Stat). Ward shares over ¥20m are estimated, see `data/income_sources.md`.
- Porsche locations: porsche.com dealer search, read on 31 Oct 2026.
- Map shapes: dataofjapan/land for prefectures and niiyz/JapanCityGeoJson (MLIT N03) for the Tokyo wards, simplified with mapshaper. See those projects for their licence terms.

Details and the exact files are in `data/*_sources.md` and `NOTES.md`.
