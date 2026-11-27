import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
meta = ('<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">'
        '<meta http-equiv="Pragma" content="no-cache">'
        '<meta http-equiv="Expires" content="0">')
for fn in ['index.html','checklist.html']:
    h = open(fn,'r',encoding='utf-8').read()
    if 'no-store' in h:
        print(fn, 'already has no-cache'); continue
    # insert right after the robots meta
    anchor = '<meta name="robots" content="noindex,nofollow">'
    if anchor in h:
        h = h.replace(anchor, anchor + meta, 1)
    else:
        h = h.replace('</title>', '</title>' + meta, 1)
    open(fn,'w',encoding='utf-8').write(h)
    print(fn, 'no-cache added:', 'no-store' in h)
