import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
h = open('index.html','r',encoding='utf-8').read()
css = """
.set-meta{font:600 14px/1.4 inherit;color:var(--fg);margin:2px 0 2px}
.set-rel{font:500 13px/1.4 inherit;color:var(--muted);margin:0 0 12px}
.set-links{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 14px}
.set-links .slink{display:inline-flex;align-items:center;padding:9px 16px;background:var(--accent);color:var(--accentfg);border-radius:8px;font:700 13px inherit;text-decoration:none;min-height:40px}
.set-links .slink:hover{opacity:.88}
.set-break{display:grid;gap:0;border:1px solid var(--border);border-radius:10px;overflow:hidden}
.set-break .brow{display:flex;justify-content:space-between;align-items:baseline;gap:10px;padding:9px 14px;background:var(--surface)}
.set-break .brow:nth-child(even){background:var(--bg)}
.set-break .bk{font:600 13px inherit;color:var(--muted)}
.set-break .bv{font:800 15px ui-monospace,Menlo,monospace;color:var(--accent);text-align:right}
"""
h = h.replace('</style>', css + '</style>')
open('index.html','w',encoding='utf-8').write(h)
print("CSS added:", '.set-break' in h)
