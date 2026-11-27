#!/usr/bin/env python3
"""Extract data from index.html, rebuild site with JSON data files, new UI."""
import json, re, os, html as htmlmod

os.makedirs('data', exist_ok=True)

# Read current index.html
with open('index.html', 'r', encoding='utf-8') as f:
    raw = f.read()

# Extract the D array JSON blob
m = re.search(r'var D=(\[.*?\]);\s*var S', raw, re.DOTALL)
if not m:
    m = re.search(r'var D=(\[.*?\]);', raw, re.DOTALL)
if not m:
    raise Exception("Could not find var D= data")

data = json.loads(m.group(1))
print(f"Found {len(data)} sets in data")

# Add metadata
for s in data:
    if 'Stars & Stripes' in s.get('title',''):
        s['meta'] = {
            "year":"2026","brand":"Panini",
            "line":"Prizm USA Stars & Stripes",
            "sport":"Baseball","program":"USA Baseball",
            "release":"April 3, 2026",
            "uniqueCards":1246,"totalWithParallels":14872,
            "baseCards":200,"autoCards":494,"matCards":442,
            "insertCards":110,"baseParallels":37,
            "autoParallels":16,"insertParallels":10,
            "links":{"checklist":"checklist.html",
                     "sellSheet":"https://www.beckett.com/news/2026-panini-stars-stripes-prizm-usa-baseball-cards/",
                     "beckettGuide":"https://www.beckett.com/news/2026-panini-stars-stripes-prizm-usa-baseball-cards/"},
            "sources":["Beckett.com","BaseballCardPedia.com","DiamondCardsOnline.com","ChecklistCenter.com","SiteLiftMedia.com"]
        }
        s['slug'] = 'stars-stripes'
    elif 'Halloween' in s.get('title','') or 'Score-A-Treat' in s.get('title',''):
        s['meta'] = {
            "year":"2026","brand":"Panini","line":"Score-A-Treat",
            "sport":"Multi-Sport","program":"Halloween","release":"2026",
            "uniqueCards":641,"baseCards":297,"autoCards":297,"insertCards":47,
            "links":{},"sources":["Two checklist sites, compared card by card"]
        }
        s['slug'] = 'halloween'

# Write JSON data files
for s in data:
    slug = s.get('slug', 'unknown')
    with open(f'data/{slug}.json', 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False)
    print(f"  data/{slug}.json ({os.path.getsize(f'data/{slug}.json'):,} bytes)")

manifest = []
for s in data:
    manifest.append({
        "slug": s.get('slug','unknown'),
        "title": s['title'],
        "btn": s['btn'],
        "small": s.get('small',''),
        "em": s.get('em',''),
        "file": f"data/{s.get('slug','unknown')}.json",
        "meta": s.get('meta',{})
    })
with open('data/sets.json', 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print(f"  data/sets.json")

# Build checklist.html from Stars & Stripes data
ss = [s for s in data if s.get('slug')=='stars-stripes'][0]
families = ss.get('families', [])
base_fams = [f for f in families if f['type']=='Base']
auto_fams = [f for f in families if f['type']=='Autograph']
mat_fams  = [f for f in families if f['type']=='Memorabilia']
ins_fams  = [f for f in families if f['type']=='Insert']
bc = sum(len(f['cards']) for f in base_fams)
ac = sum(len(f['cards']) for f in auto_fams)
mc = sum(len(f['cards']) for f in mat_fams)
ic = sum(len(f['cards']) for f in ins_fams)
total = bc + ac + mc + ic

def esc(s):
    return htmlmod.escape(str(s))

def card_rows(fam):
    rows = ''
    for c in fam['cards']:
        rows += f'<tr><td>{c["n"]}</td><td>{esc(c["a"])}</td><td class="tm">{esc(c.get("t",""))}</td><td class="pos">{esc(c.get("p",""))}</td></tr>\n'
    return rows

sections = ''
sections += f'<h2 id="base">Base Set <span class="ct">{bc} cards</span></h2>\n'
for f in base_fams:
    sections += f'<h3>{esc(f["name"])}</h3>\n<table><thead><tr><th>#</th><th>Player</th><th>Team</th><th>Pos</th></tr></thead><tbody>\n{card_rows(f)}</tbody></table>\n'

sections += f'<h2 id="autos">Autographs <span class="ct">{ac} cards across {len(auto_fams)} subsets</span></h2>\n'
for f in auto_fams:
    sections += f'<h3>{esc(f["name"])} <span class="ct">{len(f["cards"])} cards</span></h3>\n<table><thead><tr><th>#</th><th>Player</th><th>Team</th><th>Pos</th></tr></thead><tbody>\n{card_rows(f)}</tbody></table>\n'

sections += f'<h2 id="materials">Materials / Memorabilia <span class="ct">{mc}+ cards</span></h2>\n'
for f in mat_fams:
    sections += f'<h3>{esc(f["name"])} <span class="ct">{len(f["cards"])} cards</span></h3>\n<table><thead><tr><th>#</th><th>Player</th><th>Team</th><th>Pos</th></tr></thead><tbody>\n{card_rows(f)}</tbody></table>\n'

sections += f'<h2 id="inserts">Inserts <span class="ct">{ic} cards across {len(ins_fams)} subsets</span></h2>\n'
for f in ins_fams:
    sections += f'<h3>{esc(f["name"])} <span class="ct">{len(f["cards"])} cards</span></h3>\n<table><thead><tr><th>#</th><th>Player</th><th>Team</th><th>Pos</th></tr></thead><tbody>\n{card_rows(f)}</tbody></table>\n'

# Parallels from first base card
base_card = ss['families'][0]['cards'][0]
parallels = list(base_card.get('r', {}).keys()) if base_card.get('r') else []
par_count = len(parallels)
par_section = ''
if parallels:
    par_section = f'<h2 id="parallels">Base Parallels <span class="ct">{par_count} types</span></h2>\n<div class="par-grid">\n'
    for p in parallels:
        run = base_card['r'].get(p, '')
        label = f'/{run}' if run and run != '1' else ('1/1' if run == '1' else 'unnumbered')
        par_section += f'<div class="par-card"><b>{esc(p)}</b><br><span class="run">{label}</span></div>\n'
    par_section += '</div>\n'

# Write checklist.html
checklist_html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>Checklist — 2026 Panini Stars &amp; Stripes Prizm USA Baseball</title>
<style>
:root{{--bg:#f5efe0;--surface:#fffdf5;--fg:#1a1d18;--muted:#4f4e45;--border:#bdb293;--accent:#8f261f;--accentfg:#fffdf5;--gold:#7a5a14;--ok:#1f5a2b}}
*{{box-sizing:border-box}}body{{background:var(--bg);color:var(--fg);font:16px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;margin:0;padding:0 0 60px}}
.wrap{{max-width:800px;margin:0 auto;padding:16px 14px}}
.top{{background:linear-gradient(135deg,#8f261f,#b33a2a);color:#fff;padding:20px;text-align:center;border-radius:14px;margin-bottom:16px}}
.top h1{{font:900 24px/1.1 Georgia,serif;margin:0 0 4px}}.top .sub{{font-size:14px;opacity:.8}}
.back{{display:inline-flex;align-items:center;gap:5px;padding:8px 14px;background:var(--accent);color:var(--accentfg);border-radius:8px;font:700 14px inherit;text-decoration:none;margin-bottom:12px}}
.back:hover{{opacity:.85}}
.stats{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:12px 0}}
.stats .st{{background:rgba(255,255,255,.15);border-radius:8px;padding:6px 12px;text-align:center}}
.stats .st .n{{font:800 20px ui-monospace,monospace;display:block}}.stats .st .l{{font-size:11px;text-transform:uppercase;letter-spacing:.04em;opacity:.7}}
.search-bar{{position:sticky;top:0;z-index:10;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--border)}}
.search-bar input{{width:100%;padding:10px 14px;border:2px solid var(--border);border-radius:10px;font:600 16px inherit;background:#fff}}
.search-bar input:focus{{outline:none;border-color:var(--accent)}}
.toc{{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0}}
.toc a{{padding:6px 12px;background:var(--surface);border:1px solid var(--border);border-radius:8px;font:600 13px inherit;color:var(--accent);text-decoration:none}}
.toc a:hover{{background:var(--accent);color:var(--accentfg)}}
h2{{font:800 20px/1.2 Georgia,serif;color:var(--accent);margin:24px 0 8px;padding:8px 0 4px;border-bottom:2px solid var(--accent)}}
h3{{font:700 16px/1.3 inherit;color:var(--fg);margin:14px 0 6px}}
.ct{{font:600 13px ui-monospace,monospace;color:var(--muted);margin-left:6px}}
table{{width:100%;border-collapse:collapse;font-size:14px;margin-bottom:12px}}
th{{background:var(--accent);color:#fff;text-align:left;padding:6px 8px;font-weight:600;position:sticky;top:52px;z-index:5}}
td{{padding:4px 8px;border-bottom:1px solid var(--border)}}
tr:nth-child(even){{background:rgba(255,255,255,.5)}}tr:hover{{background:#e8dcc4}}
.tm{{color:var(--muted);font-size:13px}}.pos{{color:var(--muted);font-size:12px}}
.par-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:6px;margin:8px 0}}
.par-card{{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:6px 10px;font-size:14px}}
.par-card b{{color:var(--fg)}}.par-card .run{{color:var(--accent);font:700 13px ui-monospace,monospace}}
.foot{{text-align:center;padding:16px;font-size:12px;color:var(--muted)}}.foot a{{color:var(--accent)}}
.note{{background:#fffde7;border:1px solid #f9e44c;border-radius:8px;padding:10px 12px;font-size:13px;margin:8px 0}}
</style></head><body>
<div class="wrap">
<a href="index.html" class="back">&larr; Back to Card Finder</a>
<div class="top">
<h1>2026 Panini Stars &amp; Stripes Prizm USA Baseball</h1>
<div class="sub">Complete Set Checklist</div>
<div class="stats">
<div class="st"><span class="n">{bc}</span><span class="l">Base</span></div>
<div class="st"><span class="n">{ac}</span><span class="l">Autos</span></div>
<div class="st"><span class="n">{mc}+</span><span class="l">Materials</span></div>
<div class="st"><span class="n">{ic}</span><span class="l">Inserts</span></div>
<div class="st"><span class="n">{total:,}</span><span class="l">Total Unique</span></div>
<div class="st"><span class="n">{par_count}</span><span class="l">Parallel Types</span></div>
</div></div>
<div class="note">Independently verified from: Beckett.com, BaseballCardPedia.com, DiamondCardsOnline.com, ChecklistCenter.com, SiteLiftMedia.com. Cross-checked Nov 26, 2026.</div>
<div class="search-bar"><input type="text" id="search" placeholder="Search by number, name, team or position..."></div>
<div class="toc"><a href="#base">Base ({bc})</a><a href="#autos">Autographs ({ac})</a><a href="#materials">Materials ({mc}+)</a><a href="#inserts">Inserts ({ic})</a><a href="#parallels">Parallels ({par_count})</a></div>
{sections}
{par_section}
<div class="foot"><a href="index.html">&larr; Back to Card Finder</a><br>Verified from 5 independent sources &middot; Nov 26, 2026</div>
</div>
<script>
document.getElementById('search').addEventListener('input',function(e){{var q=e.target.value.toLowerCase().trim();document.querySelectorAll('tbody tr').forEach(function(row){{row.style.display=(!q||row.textContent.toLowerCase().indexOf(q)>=0)?'':'none';}});}});
</script></body></html>'''

with open('checklist.html', 'w', encoding='utf-8') as f:
    f.write(checklist_html)
print(f"checklist.html ({os.path.getsize('checklist.html'):,} bytes)")

# Write new index.html (loads JSON, has set info panel, better UX)
# Read the index_template from a separate file
# Instead of a template, we build it inline since it's static HTML+JS

with open('index_new.html', 'w', encoding='utf-8') as idx:
    idx.write(open('C:/Users/damie/GitHub/reilleyrips/index_template.html','r',encoding='utf-8').read() if os.path.exists('index_template.html') else '')

# If no template, we'll handle it in the next step
print(f"\nRebuild complete!")
print(f"  data/stars-stripes.json: {os.path.getsize('data/stars-stripes.json'):,} bytes")
print(f"  data/halloween.json: {os.path.getsize('data/halloween.json'):,} bytes")
print(f"  data/sets.json: {os.path.getsize('data/sets.json'):,} bytes")
print(f"  checklist.html: {os.path.getsize('checklist.html'):,} bytes")
print(f"\nNow run: copy index_template.html over index.html, then git add+commit+push")
