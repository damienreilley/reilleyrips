import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
h = open('index.html', 'r', encoding='utf-8').read()
funcs = ['pickSet','resetCard','onQ','pickCard','finish','cands','showSetInfo']
for fn in funcs:
    count = h.count('function ' + fn)
    print(f'  {fn}: {count} definitions')
print(f'  var D= found: {"var D=[" in h}')
print(f'  Total size: {len(h):,} chars')
print(f'  Materials labels: {h.count(">Materials<")}')
print(f'  Relic labels: {h.count(">Relic<")}')
