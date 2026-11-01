import json,sys,os
raw=sys.argv[1]; out=sys.argv[2]
g=json.load(open(os.path.join(raw,'pref','japan.geojson')))
prefs=[];tokyo=None
for f in g['features']:
    p=f['properties']; geom=f['geometry']
    polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
    if p['id']==13:
        keep=[]
        for poly in polys:
            xs=[q[0] for q in poly[0]]; ys=[q[1] for q in poly[0]]
            if max(xs)<=143 and min(ys)>=24: keep.append(poly)
        polys=keep
    feat={'type':'Feature','properties':{'code':p['id'],'name_en':p['nam'],'name_ja':p['nam_ja']},'geometry':{'type':'MultiPolygon','coordinates':polys}}
    if p['id']==13: tokyo=feat
    else: prefs.append(feat)
json.dump({'type':'FeatureCollection','features':prefs},open(os.path.join(out,'prefs.geojson'),'w'))
json.dump({'type':'FeatureCollection','features':[tokyo]},open(os.path.join(out,'tokyo.geojson'),'w'))
wards=[]
for c in range(13101,13124):
    w=json.load(open(os.path.join(raw,'tokyo','%d.json'%c)))
    polys=[]
    for f in w['features']:
        gm=f['geometry']; polys+= gm['coordinates'] if gm['type']=='MultiPolygon' else [gm['coordinates']]
        nj=f['properties']['N03_004']
    wards.append({'type':'Feature','properties':{'code':c,'name_ja':nj},'geometry':{'type':'MultiPolygon','coordinates':polys}})
json.dump({'type':'FeatureCollection','features':wards},open(os.path.join(out,'wards.geojson'),'w'))
print(len(prefs),len(tokyo['geometry']['coordinates']),len(wards))
