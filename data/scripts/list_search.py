import re,sys,html
t=open(sys.argv[1],encoding='utf-8').read()
blocks=t.split('stat-resource_list-item stat-resource_list-item-dataset')
for b in blocks[1:]:
    ids=sorted(set(re.findall(r'stat_infid=(\d+)',b)))
    txt=re.sub(r'<[^>]+>',' ',b); txt=re.sub(r'\s+',' ',html.unescape(txt))
    print(ids, txt[:300]); print()
