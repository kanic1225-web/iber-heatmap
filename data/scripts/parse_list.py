import re, sys, html
# usage: parse_list.py file1.html [file2 ...]  -> prints statInfId<TAB>title
seen = set()
for fn in sys.argv[1:]:
    t = open(fn, encoding='utf-8', errors='replace').read()
    for m in re.finditer(r'data-key="uid" data-value="(\d+)"[^>]*>(.*?)</a>', t, re.S):
        sid = m.group(1)
        if sid in seen:
            continue
        seen.add(sid)
        title = re.sub(r'<[^>]+>', ' ', m.group(2))
        title = re.sub(r'\s+', ' ', html.unescape(title)).strip()
        print(sid + '\t' + title)
