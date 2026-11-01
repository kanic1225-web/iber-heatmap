"""Build income.json from 2023 Housing and Land Survey tables.
usage: python3 -I build_income.py <t000040209911.xlsx> <t000040209921.xlsx> <out.json>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xlsx

pref_path, muni_path, out_path = sys.argv[1:4]

WARDS = {13101 + i: None for i in range(23)}

# ---------- Table 40-1 (11 brackets, 全国/都道府県/21大都市, 主世帯) ----------
rows = xlsx.read_rows(pref_path)
pref = {}  # area code -> {bracket code: count}
for r in rows:
    if len(r) < 5 or r[2] != '0_総数':
        continue
    area = r[1]
    code = area.split('_')[0]
    if not code.isdigit():
        continue
    b = r[3].split('_')[0]
    pref.setdefault(code, {'name': area.split('_', 1)[1]})[b] = int(r[4])  # col 4 = 世帯人員 総数


def rec_full(d, level):
    stated = d['00'] - d['99']
    # consistency: sum of brackets 01..11 should equal stated (allow rounding to 100s)
    s = sum(d['%02d' % i] for i in range(1, 12))
    assert abs(s - stated) <= 1000, (d, s, stated)
    a, b, c = d['09'], d['10'], d['11']
    return {
        'name': d.get('name'),
        'total': d['00'], 'unknown': d['99'],
        'stated': stated, 'b1000_1500': a, 'b1500_2000': b, 'b2000p': c,
        'over10': round((a + b + c) / stated, 6),
        'over15': round((b + c) / stated, 6),
        'over20': round(c / stated, 6),
        'level': level,
    }


regions = {}
for code, d in pref.items():
    if code.endswith('000') and code != '00000':
        regions['JP-' + code[:2]] = rec_full(d, 'prefecture')
national = rec_full(pref['00000'], 'national')
kubu = rec_full(pref['13100'], 'tokyo-23-wards-aggregate')

# JP-13-REST = 東京都 minus 特別区部 (both from table 40-1, full brackets)
t, k = pref['13000'], pref['13100']
rest = {key: t[key] - k[key] for key in t if key != 'name'}
rest['name'] = '東京都（23区以外：多摩・島しょ）'
regions['JP-13-REST'] = rec_full(rest, 'prefecture-minus-wards')
regions['JP-13-REST']['note'] = 'Derived: 東京都 minus 特別区部, both from table 40-1 (11 brackets).'

# ---------- Table 43-4 (10 brackets, 市区町村, 主世帯; top bracket = 1500万円以上, no 不詳 row) ----------
rows = xlsx.read_rows(muni_path)
muni = {}
for r in rows:
    if len(r) < 5 or r[2] != '0_総数':
        continue
    code = r[1].split('_')[0]
    if not code.isdigit() or int(code) not in WARDS:
        continue
    b = r[3].split('_')[0]
    muni.setdefault(code, {'name': r[1].split('_', 1)[1]})[b] = int(r[4])

assert len(muni) == 23, sorted(muni)
ward_sum = {'stated': 0, 'b1000_1500': 0, 'b1500p': 0}
for code in sorted(muni):
    d = muni[code]
    stated = sum(d[k] for k in d if k not in ('name', '00'))  # all listed brackets; 不詳 not listed
    a, bp = d['10'], d['11']
    regions['JP-13-' + code[2:]] = {
        'name': d['name'],
        'total': d['00'], 'unknown': d['00'] - stated,
        'stated': stated, 'b1000_1500': a, 'b1500_2000': None, 'b2000p': None, 'b1500p': bp,
        'over10': round((a + bp) / stated, 6),
        'over15': round(bp / stated, 6),
        'over20': None,
        'level': 'ward',
        'note': 'Ward table (43-4) tops out at 1500万円以上; 1500-2000 / 2000+ split not published at ward level, so over20 is null.',
    }
    ward_sum['stated'] += stated
    ward_sum['b1000_1500'] += a
    ward_sum['b1500p'] += bp

# cross-check: 23-ward sum vs 特別区部 in table 40-1
xcheck = {
    'wards_sum_stated': ward_sum['stated'], 'kubu_stated_t40_1': kubu['stated'],
    'wards_sum_b1000_1500': ward_sum['b1000_1500'], 'kubu_b1000_1500_t40_1': kubu['b1000_1500'],
    'wards_sum_b1500p': ward_sum['b1500p'], 'kubu_b1500p_t40_1': kubu['b1500_2000'] + kubu['b2000p'],
}

base = 'https://www.e-stat.go.jp/stat-search/file-download?statInfId=%s&fileKind=0'
out = {
    'definition': ('世帯の年間収入階級 (annual household income class), 2023 Housing and Land Survey '
                   '(令和5年住宅・土地統計調査, 確報集計 住宅及び世帯に関する基本集計), household concept = 主世帯 '
                   '(main households), all tenure types (住宅の所有の関係=総数). '
                   'shares = bracket count / households with income stated (総数 minus 不詳; 不詳 excluded from numerator and denominator). '
                   'Prefectures: 11-bracket table with 1000-1500 / 1500-2000 / 2000万円以上. '
                   'Wards: 10-bracket table whose top bracket is 1500万円以上, so wards have over10 and over15 but over20 = null. '
                   'Counts are survey estimates rounded by the source (prefecture: 100s; wards: 10s).'),
    'source': [
        {'table': '第40-1表 世帯の年間収入階級(11区分)、世帯人員(7区分)、住宅の所有の関係(6区分)別主世帯数－全国、都道府県、21大都市',
         'statInfId': '000040209911', 'url': base % '000040209911', 'level': 'prefecture'},
        {'table': '第43-4表 世帯の年間収入階級(10区分)、住宅の所有の関係(5区分)別主世帯数、１世帯当たり人員、１世帯当たり居住室数及び１世帯当たり居住室の畳数－全国、都道府県、市区町村',
         'statInfId': '000040209921', 'url': base % '000040209921', 'level': 'ward'},
    ],
    'regions': dict(sorted(regions.items())),
    'aggregates': {'JP': national, 'JP-13-KUBU': kubu},
    'checks': {
        'national_over20': national['over20'], 'national_over15': national['over15'], 'national_over10': national['over10'],
        'tokyo_over20': regions['JP-13']['over20'], 'tokyo_over15': regions['JP-13']['over15'], 'tokyo_over10': regions['JP-13']['over10'],
        'tokyo23_over20': kubu['over20'], 'tokyo_rest_over20': regions['JP-13-REST']['over20'],
        'ward_crosscheck': xcheck,
    },
}
json.dump(out, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(out['checks'], ensure_ascii=False, indent=1))
for k in sorted(regions):
    if k.startswith('JP-13'):
        v = regions[k]
        print(k, v['name'], v['stated'], v['over10'], v['over15'], v['over20'])
top = sorted([(v['over20'], k, v['name']) for k, v in regions.items() if v['level'] == 'prefecture'], reverse=True)
print('top prefs over20:', top[:5])
print('bottom:', top[-3:])
