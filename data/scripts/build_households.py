import csv,sys,json
src,out=sys.argv[1],sys.argv[2]
rows=list(csv.reader(open(src,encoding='utf-8')))
# locate header rows
hdr_kind=next(r for r in rows if len(r)>17 and r[16]=='0_総数' and r[17]=='1_一般世帯')
assert hdr_kind[18]=='2_施設等の世帯'
COL=17
data=[r for r in rows if len(r)>COL and r[5].isdigit() and len(r[5])==5]
def val(code):
    m=[r for r in data if r[5]==code and '旧：' not in r[6]]
    assert len(m)==1,(code,len(m),[x[:7] for x in m])
    return int(m[0][COL]), m[0][6]
nat,_=val('00000')
prefs={}
for p in range(1,48):
    v,name=val('%02d000'%p); prefs['JP-%02d'%p]=v
wards={}
for w in range(101,124):
    v,name=val('13%d'%w); wards['JP-13-%d'%w]=v; print(w,name,v)
ku,_=val('13100')
tokyo=prefs['JP-13']; wsum=sum(wards.values())
assert wsum==ku,(wsum,ku)
assert sum(prefs.values())==nat,(sum(prefs.values()),nat)
res={
 "definition":"一般世帯数 (general households), 2020 Population Census, as of 2020-10-01",
 "source":[{"table":"令和2年国勢調査 人口等基本集計 第1-1表 男女別人口，世帯の種類別世帯数及び世帯人員並びに…－全国，都道府県，市区町村（2000年（平成12年）市区町村含む）; column 世帯数 > 世帯の種類 > 1_一般世帯",
   "statInfId":"000032142402",
   "url":"https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032142402&fileKind=0"}],
 "prefectures":prefs,"tokyo_wards":wards,
 "tokyo_rest":{"JP-13-REST":tokyo-wsum},
 "checks":{"national_total":nat,"tokyo_total":tokyo,"wards_sum":wsum,
           "prefectures_sum":sum(prefs.values()),"tokubetsu_kubu_row_13100":ku}
}
json.dump(res,open(out,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print(json.dumps(res["checks"]), res["tokyo_rest"])
