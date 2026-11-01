import re,sys,html
t=open(sys.argv[1],encoding='utf-8').read()
parts=re.split(r'class="stat-dataset_list-item',t)
for b in parts[1:]:
    ids=sorted(set(re.findall(r'(?:stat_infid|statInfId)=(\d+)',b)))
    kinds=sorted(set(re.findall(r'fileKind=(\d)',b)))
    txt=re.sub(r'<[^>]+>',' ',b); txt=re.sub(r'\s+',' ',html.unescape(txt))
    print(ids,kinds,txt[:200])
