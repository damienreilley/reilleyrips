import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
ss = json.load(open('data/stars-stripes.json','r',encoding='utf-8'))
# For each type, collect union of parallel names across that type's cards
from collections import OrderedDict
by_type = {}
for fam in ss['families']:
    t = fam['type']
    by_type.setdefault(t, OrderedDict())
    for c in fam['cards']:
        r = c.get('r') or {}
        for name, run in r.items():
            if name not in by_type[t]:
                by_type[t][name] = run
for t, pars in by_type.items():
    print(f"=== {t}: {len(pars)} parallel types ===")
    for name, run in pars.items():
        label = ('1/1' if run=='1' else ('/'+run if run else 'unnumbered'))
        print(f"   {name}  {label}")
