# Build the inline DATA block for heatmap/index.html from simplified geometry + real and placeholder numbers.
# Usage: python3 -I gen.py <hmwork dir> <template.html> <out index.html> [<realdata dir>]
# Real: households (2020 Census), money shares (2023 Housing and Land Survey), dealers (porsche.com).
# Placeholder (mock): park, charge and timing door rates (park x charge equals the old combined parking rate).
import json, sys, os, random, math

work, tpl_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
real = sys.argv[4] if len(sys.argv) > 4 else os.path.join(os.path.dirname(os.path.abspath(work)), 'realdata')
random.seed(983)

def ring_area(r):
    return sum(r[i][0]*r[i+1][1]-r[i+1][0]*r[i][1] for i in range(len(r)-1))/2.0
def rewind(g):
    # d3-geo wants exterior rings clockwise (negative planar area with y=lat up), holes counter-clockwise
    polys = g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
    out=[]
    for poly in polys:
        rings=[]
        for i,r in enumerate(poly):
            a=ring_area(r)
            if (i==0 and a>0) or (i>0 and a<0): r=r[::-1]
            rings.append(r)
        out.append(rings)
    return {'type':'MultiPolygon','coordinates':out} if len(out)>1 else {'type':'Polygon','coordinates':out[0]}

def load_geoms(path):
    g = json.load(open(os.path.join(work, path)))
    if g.get('type') == 'FeatureCollection':
        return [(f.get('properties') or {}, f['geometry']) for f in g['features']]
    if g.get('type') == 'GeometryCollection':
        return [({}, x) for x in g['geometries']]
    return [({}, g)]

PREF = {  # code: (name_en, name_ja, old mock households in thousands -- UNUSED, real counts come from households.json)
 1:("Hokkaido","北海道",2476),2:("Aomori","青森県",511),3:("Iwate","岩手県",492),4:("Miyagi","宮城県",982),
 5:("Akita","秋田県",385),6:("Yamagata","山形県",398),7:("Fukushima","福島県",742),8:("Ibaraki","茨城県",1184),
 9:("Tochigi","栃木県",797),10:("Gunma","群馬県",805),11:("Saitama","埼玉県",3163),12:("Chiba","千葉県",2774),
 14:("Kanagawa","神奈川県",4224),15:("Niigata","新潟県",865),16:("Toyama","富山県",404),17:("Ishikawa","石川県",469),
 18:("Fukui","福井県",291),19:("Yamanashi","山梨県",339),20:("Nagano","長野県",832),21:("Gifu","岐阜県",780),
 22:("Shizuoka","静岡県",1483),23:("Aichi","愛知県",3238),24:("Mie","三重県",742),25:("Shiga","滋賀県",571),
 26:("Kyoto","京都府",1191),27:("Osaka","大阪府",4136),28:("Hyogo","兵庫県",2402),29:("Nara","奈良県",545),
 30:("Wakayama","和歌山県",393),31:("Tottori","鳥取県",220),32:("Shimane","島根県",270),33:("Okayama","岡山県",801),
 34:("Hiroshima","広島県",1243),35:("Yamaguchi","山口県",598),36:("Tokushima","徳島県",308),37:("Kagawa","香川県",407),
 38:("Ehime","愛媛県",601),39:("Kochi","高知県",315),40:("Fukuoka","福岡県",2323),41:("Saga","佐賀県",312),
 42:("Nagasaki","長崎県",558),43:("Kumamoto","熊本県",719),44:("Oita","大分県",489),45:("Miyazaki","宮崎県",469),
 46:("Kagoshima","鹿児島県",728),47:("Okinawa","沖縄県",614),
}
# combined park-and-charge placeholder base rates for prefectures (split into park and charge by split_park)
PREF_PARK = {27:.50,14:.60,23:.65,11:.70,12:.72,26:.65,28:.70,40:.72}
RURAL = {2,3,5,6,31,32,39,42,45,46,30,36}
CAR_DEP = {8,9,10,16,17,18,19,20,21,24,25,33,35,37,41,43,44,45,46,15,7,6,5,3,2,31,32,36,38,39,42,47,22}

WARDS = {  # code: (name_en, old mock households thousands UNUSED, old mock money UNUSED, placeholder combined park x charge)
 13101:("Chiyoda",40,.085,.16),13102:("Chuo",90,.070,.15),13103:("Minato",140,.090,.15),13104:("Shinjuku",220,.040,.20),
 13105:("Bunkyo",120,.055,.25),13106:("Taito",120,.030,.22),13107:("Sumida",150,.025,.30),13108:("Koto",270,.035,.30),
 13109:("Shinagawa",230,.040,.28),13110:("Meguro",150,.060,.30),13111:("Ota",400,.030,.38),13112:("Setagaya",490,.050,.38),
 13113:("Shibuya",140,.075,.20),13114:("Nakano",210,.030,.30),13115:("Suginami",330,.035,.38),13116:("Toshima",180,.030,.25),
 13117:("Kita",190,.022,.38),13118:("Arakawa",110,.020,.30),13119:("Itabashi",310,.025,.40),13120:("Nerima",370,.030,.45),
 13121:("Adachi",330,.020,.45),13122:("Katsushika",230,.020,.42),13123:("Edogawa",330,.022,.45),
}

def r3(x): return round(x, 4)
def doors(base):
    return {"low": r3(min(1, base*0.75)), "base": r3(base), "high": r3(min(1, base*1.25))}
def split_park(pk):
    # placeholder split of the old combined "can park and charge" rate pk into park x charge (= pk exactly, so totals do not move)
    park = round(0.55 + 0.45 * pk, 4)
    charge = round(pk / park, 6)
    assert abs(park * charge - pk) < 1e-5, (pk, park, charge)
    return doors(park), {"low": r3(min(1, charge * 0.75)), "base": charge, "high": r3(min(1, charge * 1.25))}
def noise(a): return random.uniform(-a, a)

# ---------- real data ----------
HH = json.load(open(os.path.join(real, 'households.json'), encoding='utf-8'))
INC = json.load(open(os.path.join(real, 'income.json'), encoding='utf-8'))
INC_R, KUBU = INC['regions'], INC['aggregates']['JP-13-KUBU']
def hh_of(rid):
    if rid == 'JP-13-REST': return HH['tokyo_rest'][rid]
    if rid.startswith('JP-13-'): return HH['tokyo_wards'][rid]
    return HH['prefectures'][rid]
def r6(x): return round(x, 6)

# Can pay: real shares of main households (income stated) with annual income over JPY 10m / 15m / 20m.
# Prefectures and JP-13-REST: all three real. Wards: m10, m15 real; m20 ESTIMATED (ward table stops at 15m+):
#   alpha_w = ln(m15_w/m10_w) / ln(1000/1500); raw20_w = m15_w * (1500/2000)**alpha_w   (power-law tail through
#   the ward's own two real points; fallback raw20_w = 0.438 * m15_w if m15_w >= m10_w or either is 0), then
#   k = (23-ward over20 * 23-ward stated) / sum_w(raw20_w * stated_w)  so ward over-20m households add up to the real
#   23-ward total (aggregate JP-13-KUBU, table 40-1), and m20_w = min(raw20_w * k, 0.95 * m15_w).
WARD_IDS = ["JP-13-%d" % c for c in range(101, 124)]
_raw20 = {}
for wid in WARD_IDS:
    w = INC_R[wid]; m10, m15 = w['over10'], w['over15']
    if m10 > 0 and m15 > 0 and m15 < m10:
        alpha = math.log(m15 / m10) / math.log(1000 / 1500)
        _raw20[wid] = m15 * (1500 / 2000) ** alpha
    else:
        _raw20[wid] = 0.438 * m15
K20 = (KUBU['over20'] * KUBU['stated']) / sum(_raw20[w] * INC_R[w]['stated'] for w in WARD_IDS)
def money_of(rid):
    x = INC_R[rid]
    if rid in _raw20:
        return {"m10": r6(x['over10']), "m15": r6(x['over15']), "m20": r6(min(_raw20[rid] * K20, 0.95 * x['over15']))}
    assert x['over20'] is not None, rid
    return {"m10": r6(x['over10']), "m15": r6(x['over15']), "m20": r6(x['over20'])}
print("k=%.4f" % K20, " ".join("%s m20=%.4f" % (n, money_of(i)['m20']) for n, i in
      (("Minato", "JP-13-103"), ("Chiyoda", "JP-13-101"), ("Chuo", "JP-13-102"), ("Shibuya", "JP-13-113"))))

regions, feats = [], []
pref_geoms = {p['code']: g for p, g in load_geoms('prefs_s.geojson')}
ward_geoms = {p['code']: (p, g) for p, g in load_geoms('wards_s.geojson')}
tr = load_geoms('tr_s.geojson')
assert len(tr) == 1

for code in range(1, 48):
    if code == 13:
        rid = "JP-13-REST"
        pk_d, ch_d = split_park(.60)
        regions.append(dict(id=rid, name_en="Tokyo outside 23 wards", name_ja="東京都（23区外）", group="tokyo_rest",
            households=hh_of(rid), money=money_of(rid), park=pk_d, charge=ch_d, timing=doors(round(.20+noise(.008),3))))
        feats.append((rid, tr[0][1]))
        for wc in range(13101, 13124):
            en, hh, m, pk = WARDS[wc]
            p, g = ward_geoms[wc]
            wid = "JP-13-%d" % (wc - 13000)
            pk_d, ch_d = split_park(pk)
            regions.append(dict(id=wid, name_en=en, name_ja=p['name_ja'], group="ward", households=hh_of(wid),
                money=money_of(wid), m20_est=True, park=pk_d, charge=ch_d, timing=doors(round(.19+noise(.01),3))))
            feats.append((wid, g))
        continue
    en, ja, hh = PREF[code]
    rid = "JP-%02d" % code
    if code in PREF_PARK: pk = PREF_PARK[code]
    elif code in RURAL: pk = round(random.uniform(.90, .95), 3)
    else: pk = round(random.uniform(.80, .92), 3)
    t = (.235 if code in CAR_DEP else .205) + noise(.012)
    t = round(max(.18, min(.26, t)), 3)
    pk_d, ch_d = split_park(pk)
    regions.append(dict(id=rid, name_en=en, name_ja=ja, group="prefecture", households=hh_of(rid),
        money=money_of(rid), park=pk_d, charge=ch_d, timing=doors(t)))
    feats.append((rid, pref_geoms[code]))

assert len(regions) == 70 and len(feats) == 70 and len({r['id'] for r in regions}) == 70
assert all('park' in r and 'charge' in r and 'parking' not in r for r in regions), "park x charge split"
_tk = sum(r['households'] for r in regions if r['id'].startswith('JP-13-'))
assert _tk == HH['prefectures']['JP-13'], ("Tokyo pieces", _tk, HH['prefectures']['JP-13'])
_nat = sum(r['households'] for r in regions)
assert _nat == HH['checks']['national_total'], ("national", _nat, HH['checks']['national_total'])
print("households national", _nat, "tokyo", _tk)

geo = {"type": "FeatureCollection", "features": [{"type": "Feature", "id": rid, "properties": {}, "geometry": rewind(g)} for rid, g in feats]}
# Whole-Tokyo outline (main map draws Tokyo as one prefecture unit; numbers are summed from the 24 pieces in JS)
tk = load_geoms('tokyo_s.geojson')
assert len(tk) == 1
geo["features"].append({"type": "Feature", "id": "JP-13", "properties": {"unit": "tokyo_summed"}, "geometry": rewind(tk[0][1])})

# DEALERS: 69 real Porsche locations. Japanese name/address from dealers_raw.tsv, coordinates/type/partner no./English
# name from dealers_coords.psv (same row order, joined by index). type: C = Porsche Center, S = Satellite Porsche
# Center (both sales points), P = Pre-owned, A = Approved & Service, X = Experience,
# V = Service, T = Studio.
_raw = [l.rstrip('\n').split('\t') for l in open(os.path.join(real, 'dealers_raw.tsv'), encoding='utf-8') if l.strip()]
assert _raw[0] == ['name', 'street', 'postal_city'], _raw[0]
_raw = _raw[1:]
_crd = [l.rstrip('\n').split('|') for l in open(os.path.join(real, 'dealers_coords.psv'), encoding='utf-8')
        if l.strip() and not l.startswith('#')]
assert len(_raw) == len(_crd) == 69, (len(_raw), len(_crd))
DEALERS = []
for i, (rw, cd) in enumerate(zip(_raw, _crd)):
    idx, lat, lng, typ, partner, name_en = cd
    assert int(idx) == i and typ in 'CSPAXVT' and len(typ) == 1, cd
    city = rw[2].split(' ', 1)[1].strip() if rw[2][:3].isdigit() and ' ' in rw[2] else rw[2].strip()
    DEALERS.append({"name": rw[0].strip(), "name_en": name_en.strip(), "type": typ, "city": city,
                    "lat": float(lat), "lng": float(lng), "partner": partner.strip()})
assert sum(d['type'] in 'CS' for d in DEALERS) == 50
assert len(DEALERS) == 69  # the page draws all 69 and uses all of them for the nearest-location distance

def js(o): return json.dumps(o, ensure_ascii=False, separators=(',', ':'))

lines = []
lines.append("// ===== DATA: replace these with real numbers =====  (households, money, dealers are now real; park, charge, timing still placeholders)")
lines.append("// Households: 2020 Census general households (REAL). money: 2023 Housing and Land Survey (REAL), shares of main")
lines.append("// households with income stated whose annual income is over JPY 10m / 15m / 20m: money = {m10, m15, m20}, picked by")
lines.append("// the income cutoff slider. Ward m20 is ESTIMATED (m20_est: true): power-law tail through the ward's real m10 and m15,")
lines.append("// scaled (k = %.4f) to the real 23-ward over-20m total, capped at 0.95 x m15." % K20)
lines.append("// park, charge and timing: PLACEHOLDER (mock) rates, low = base x 0.75, high = base x 1.25 (clamped to [0,1]); the page reads base.")
lines.append("// Door keys: money = can pay for a JPY 11-17 m car; park = has a parking space for the car (own or rented);")
lines.append("//            charge = of those who can park, the space can take a home charger (park x charge = the old combined rate);")
lines.append("//            timing = renewing (replacing) their car within the next 24 months.")
lines.append('const DATA_STATUS = { households: "real", money: "real (ward over-\u00a520m estimated)", park: "placeholder", charge: "placeholder", timing: "placeholder", dealers: "real" };')
lines.append('const INCOME_STOP_LABELS = ["\u00a510,000,000", "\u00a515,000,000", "\u00a520,000,000"];')
lines.append("const REGIONS = [")
for r in regions:
    lines.append("  " + js(r) + ",")
lines.append("];")
lines.append('const DEALERS_SOURCE = "porsche.com/jp/ja-JP/dealersearch/, read 31 Oct 2026; coordinates from Porsche\'s own dealer data";')
lines.append("const DEALERS = [")
for d in DEALERS:
    lines.append("  " + js(d) + ",")
lines.append("];")
lines.append('const GEO_SOURCE = "dataofjapan/land (prefectures) + niiyz/JapanCityGeoJson (Tokyo wards, MLIT N03), simplified with mapshaper";')
lines.append("// GEO: GeoJSON FeatureCollection, feature.id === REGIONS[i].id, plus one extra feature 'JP-13' = whole Tokyo outline")
lines.append("// used by the main map; Tokyo's numbers there are the SUM of the 24 Tokyo pieces. Outer rings clockwise (d3 convention).")
lines.append("const GEO = " + js(geo) + ";")
lines.append("// ===== END DATA =====")
block = "\n".join(lines)

tpl = open(tpl_path, encoding='utf-8').read()
assert "/*@@DATA@@*/" in tpl
open(out_path, 'w', encoding='utf-8').write(tpl.replace("/*@@DATA@@*/", block))
print("regions", len(regions), "dealers", len(DEALERS), "bytes", os.path.getsize(out_path))
print(" ".join(r['id'] for r in regions))
print("park x charge split ok", len(regions))
