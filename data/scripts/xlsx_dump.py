import zipfile,sys,re,csv
import xml.etree.ElementTree as ET
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def col2n(c):
    n=0
    for ch in c: n=n*26+ord(ch)-64
    return n-1
z=zipfile.ZipFile(sys.argv[1])
ss=[]
if 'xl/sharedStrings.xml' in z.namelist():
    for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS):
        ss.append(''.join(t.text or '' for t in si.iter('{%s}t'%NS['m'])))
sheets=sorted(n for n in z.namelist() if re.match(r'xl/worksheets/sheet\d+\.xml',n))
print(sheets,file=sys.stderr)
root=ET.fromstring(z.read(sheets[0]))
w=csv.writer(open(sys.argv[2],'w',newline='',encoding='utf-8'))
for row in root.iter('{%s}row'%NS['m']):
    vals={}
    for c in row.findall('m:c',NS):
        ref=re.match(r'([A-Z]+)',c.get('r')).group(1)
        v=c.find('m:v',NS); t=c.get('t')
        if t=='inlineStr':
            val=''.join(x.text or '' for x in c.iter('{%s}t'%NS['m']))
        elif v is None: val=''
        elif t=='s': val=ss[int(v.text)]
        else: val=v.text
        vals[col2n(ref)]=val
    if vals:
        m=max(vals); w.writerow([vals.get(i,'') for i in range(m+1)])
