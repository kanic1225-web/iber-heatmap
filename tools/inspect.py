import json,sys
g=json.load(open(sys.argv[1]))
for f in g['features']:
    p=f['properties']; c=f['geometry']['coordinates']
    pts=[pt for poly in c for ring in poly for pt in ring] if f['geometry']['type']=='MultiPolygon' else [pt for ring in c for pt in ring]
    xs=[q[0] for q in pts]; ys=[q[1] for q in pts]
    print(p.get('id'),p.get('nam'),p.get('nam_ja'),len(pts),round(min(xs),2),round(max(xs),2),round(min(ys),2),round(max(ys),2))
