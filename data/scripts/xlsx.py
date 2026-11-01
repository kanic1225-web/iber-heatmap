"""Minimal xlsx reader (stdlib only). read_rows(path, sheet_index=0) -> list of lists of str."""
import zipfile, re, sys
import xml.etree.ElementTree as ET

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def col_idx(ref):
    letters = re.match(r'([A-Z]+)', ref).group(1)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def sheet_names(path):
    z = zipfile.ZipFile(path)
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    return [s.get('name') for s in wb.find('m:sheets', NS)]


def read_rows(path, sheet_index=0):
    z = zipfile.ZipFile(path)
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root.findall('m:si', NS):
            ss.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
    sheets = sorted([n for n in z.namelist() if re.match(r'xl/worksheets/sheet\d+\.xml', n)],
                    key=lambda s: int(re.search(r'(\d+)\.xml', s).group(1)))
    root = ET.fromstring(z.read(sheets[sheet_index]))
    rows = []
    for r in root.iter('{%s}row' % NS['m']):
        row = {}
        for c in r.findall('m:c', NS):
            t = c.get('t')
            v = c.find('m:v', NS)
            if t == 's' and v is not None:
                val = ss[int(v.text)]
            elif t == 'inlineStr':
                val = ''.join(x.text or '' for x in c.iter('{%s}t' % NS['m']))
            else:
                val = v.text if v is not None else ''
            row[col_idx(c.get('r'))] = val
        if row:
            rows.append([row.get(i, '') for i in range(max(row) + 1)])
        else:
            rows.append([])
    return rows


if __name__ == '__main__':
    p = sys.argv[1]
    print(sheet_names(p))
    rows = read_rows(p, int(sys.argv[2]) if len(sys.argv) > 2 else 0)
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 25
    for r in rows[:n]:
        print(r)
    print('rows:', len(rows))
