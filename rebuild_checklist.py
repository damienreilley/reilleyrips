#!/usr/bin/env python3
"""Rebuild checklist.html per Damien's spec:
Filters: All, Base, Parallels, Inserts, Autographs, Relic (in that order)
- Default: All selected, all sections shown, no parallel panel
- Click a filter: that section stays expanded, others collapse, no page jump,
  the parallels for that sub-set appear between the filter bar and the card list,
  the filter stays highlighted until cleared
- Click All (or the active filter again): clears back to default
- Each section has a Back-to-top link
- Sections are collapsible (click header to expand/collapse)
"""
import json, os, html as htmlmod
from collections import OrderedDict

os.chdir(os.path.dirname(os.path.abspath(__file__)))
ss = json.load(open('data/stars-stripes.json', 'r', encoding='utf-8'))

def esc(s):
    return htmlmod.escape(str(s))

# Order families: Base -> Insert -> Autograph -> Relic
_order = {'Base':0,'Insert':1,'Autograph':2,'Memorabilia':3}
families = sorted(ss['families'], key=lambda f: _order.get(f['type'], 9))

# Map internal type -> filter key + label
TYPEKEY = {'Base':'base','Insert':'insert','Autograph':'auto','Memorabilia':'relic'}
TYPELABEL = {'Base':'Base','Insert':'Inserts','Autograph':'Autographs','Memorabilia':'Relic'}

# Collect parallels per type (union across that type's cards), excluding "Standard"
pars_by_key = {}
for fam in families:
    k = TYPEKEY[fam['type']]
    pars_by_key.setdefault(k, OrderedDict())
    for c in fam['cards']:
        for name, run in (c.get('r') or {}).items():
            if name == 'Standard':
                continue
            if name not in pars_by_key[k]:
                pars_by_key[k][name] = run

# counts
counts = {}
for fam in families:
    k = TYPEKEY[fam['type']]
    counts[k] = counts.get(k, 0) + len(fam['cards'])
total = sum(counts.values())
base_par_count = len(pars_by_key.get('base', {}))

def par_label(run):
    if run == '1':
        return '1/1'
    if run:
        return '/' + run
    return 'unnumbered'

# Build parallel panels HTML per filter key (base, parallels, auto, relic)
# "parallels" filter uses the base parallels
def par_panel_html(key, pars):
    if not pars:
        return ''
    chips = ''.join(f'<span class="pchip">{esc(n)} <b>{par_label(r)}</b></span>' for n, r in pars.items())
    return f'<div class="par-panel" data-par="{key}"><div class="plabel">{len(pars)} parallel types for this sub-set</div><div class="pchips">{chips}</div></div>'

par_panels = ''
par_panels += par_panel_html('base', pars_by_key.get('base', {}))
par_panels += par_panel_html('parallels', pars_by_key.get('base', {}))  # Parallels filter shows base parallels
par_panels += par_panel_html('auto', pars_by_key.get('auto', {}))
par_panels += par_panel_html('relic', pars_by_key.get('relic', {}))

# Build sections (one per filter key, grouping its families)
def card_table(fam):
    rows = ''.join(
        f'<tr><td>{c["n"]}</td><td>{esc(c["a"])}</td><td class="tm">{esc(c.get("t",""))}</td><td class="pos">{esc(c.get("p",""))}</td></tr>'
        for c in fam['cards']
    )
    return f'<table><thead><tr><th>#</th><th>Player</th><th>Team</th><th>Pos</th></tr></thead><tbody>{rows}</tbody></table>'

# Group families by filter key, preserving order
section_order = [('base','Base Set'),('insert','Inserts'),('auto','Autographs'),('relic','Relic / Game-Used')]
sections = ''
for key, title in section_order:
    fams = [f for f in families if TYPEKEY[f['type']] == key]
    if not fams:
        continue
    cnt = sum(len(f['cards']) for f in fams)
    sections += f'<div class="sec" data-type="{key}">'
    sections += f'<div class="sec-head" data-toggle="{key}"><h2>{title} <span class="ct">{cnt} cards</span></h2>'
    sections += '<div class="sec-head-right"><a href="#top" class="top-link">Back to top</a><span class="caret">&#9650;</span></div></div>'
    sections += f'<div class="sec-body" data-body="{key}">'
    for f in fams:
        sections += f'<h3>{esc(f["name"])} <span class="ct">{len(f["cards"])} cards</span></h3>'
        sections += card_table(f)
    sections += '</div></div>'

page = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>Checklist &#8212; 2026 Panini Stars &amp; Stripes Prizm USA Baseball</title>
<style>
:root{{--bg:#f5efe0;--surface:#fffdf5;--surface2:#ebe3cd;--fg:#1a1d18;--muted:#4f4e45;--border:#bdb293;--accent:#8f261f;--accentfg:#fffdf5;--gold:#7a5a14;--ok:#1f5a2b}}
*{{box-sizing:border-box}}body{{background:var(--bg);color:var(--fg);font:16px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;margin:0;padding:0 0 60px}}
.wrap{{max-width:860px;margin:0 auto;padding:16px 14px}}
.back{{display:inline-flex;align-items:center;gap:5px;padding:8px 14px;background:var(--accent);color:var(--accentfg);border-radius:8px;font:700 14px inherit;text-decoration:none;margin-bottom:12px}}
.back:hover{{opacity:.85}}
.top-bar{{background:linear-gradient(135deg,#8f261f,#b33a2a);color:#fff;padding:20px;text-align:center;border-radius:14px;margin-bottom:16px}}
.top-bar h1{{font:900 24px/1.1 Georgia,serif;margin:0 0 4px}}.top-bar .sub{{font-size:14px;opacity:.8}}
.stats{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:12px 0}}
.stats .st{{background:rgba(255,255,255,.15);border-radius:8px;padding:6px 12px;text-align:center}}
.stats .st .n{{font:800 20px ui-monospace,monospace;display:block}}.stats .st .l{{font-size:11px;text-transform:uppercase;letter-spacing:.04em;opacity:.7}}
.note{{background:#fffde7;border:1px solid #f9e44c;border-radius:8px;padding:10px 12px;font-size:13px;margin:8px 0}}
.search-bar{{position:sticky;top:0;z-index:20;background:var(--bg);padding:8px 0 6px;border-bottom:1px solid var(--border)}}
.search-bar input{{width:100%;padding:10px 14px;border:2px solid var(--border);border-radius:10px;font:600 16px inherit;background:#fff}}
.search-bar input:focus{{outline:none;border-color:var(--accent)}}
.filters{{position:sticky;top:52px;z-index:19;background:var(--bg);padding:8px 0;display:flex;flex-wrap:wrap;gap:6px}}
.fbtn{{padding:7px 14px;border:2px solid var(--border);border-radius:20px;background:var(--surface);font:700 13px inherit;color:var(--fg);cursor:pointer}}
.fbtn:hover{{border-color:var(--accent)}}
.fbtn.on{{background:var(--accent);color:var(--accentfg);border-color:var(--accent)}}
.fbtn .fc{{font-weight:400;opacity:.7;margin-left:3px}}
.par-panel{{display:none;padding:10px 12px;margin:4px 0 10px;background:var(--surface);border:1px solid var(--border);border-radius:10px}}
.par-panel.on{{display:block}}
.par-panel .plabel{{font:700 13px inherit;color:var(--muted);margin-bottom:6px}}
.pchips{{display:flex;flex-wrap:wrap;gap:5px}}
.pchip{{display:inline-block;padding:3px 10px;border-radius:12px;background:var(--surface2);font:600 12px ui-monospace,Menlo,monospace;color:var(--fg);border:1px solid var(--border)}}
.pchip b{{color:var(--accent)}}
.sec{{margin-bottom:8px}}
.sec[hidden]{{display:none}}
.sec-head{{display:flex;align-items:center;justify-content:space-between;border-bottom:2px solid var(--accent);padding:8px 0 5px;margin-top:16px;cursor:pointer}}
.sec-head h2{{font:800 20px/1.2 Georgia,serif;color:var(--accent);margin:0}}
.sec-head-right{{display:flex;align-items:center;gap:12px}}
.top-link{{font:600 12px inherit;color:var(--accent);text-decoration:none}}
.top-link:hover{{text-decoration:underline}}
.caret{{font-size:11px;color:var(--muted);transition:transform .15s}}
.sec.collapsed .caret{{transform:rotate(180deg)}}
.sec.collapsed .sec-body{{display:none}}
h3{{font:700 15px/1.3 inherit;color:var(--fg);margin:12px 0 6px}}
.ct{{font:600 13px ui-monospace,monospace;color:var(--muted);margin-left:6px}}
table{{width:100%;border-collapse:collapse;font-size:14px;margin-bottom:12px}}
th{{background:var(--accent);color:#fff;text-align:left;padding:6px 8px;font-weight:600}}
td{{padding:4px 8px;border-bottom:1px solid var(--border)}}
tr:nth-child(even){{background:rgba(255,255,255,.5)}}tr:hover{{background:#e8dcc4}}
.tm{{color:var(--muted);font-size:13px}}.pos{{color:var(--muted);font-size:12px}}
.foot{{text-align:center;padding:16px;font-size:12px;color:var(--muted)}}.foot a{{color:var(--accent)}}
@media(max-width:500px){{th,td{{padding:3px 5px;font-size:13px}}.pchip{{font-size:11px;padding:2px 7px}}}}
</style></head><body>
<div class="wrap" id="top">
<a href="index.html" class="back">&larr; Back to Card Finder</a>
<div class="top-bar">
<h1>2026 Panini Stars &amp; Stripes Prizm USA Baseball</h1>
<div class="sub">Complete Set Checklist</div>
<div class="stats">
<div class="st"><span class="n">{counts.get('base',0)}</span><span class="l">Base</span></div>
<div class="st"><span class="n">{counts.get('auto',0)}</span><span class="l">Autos</span></div>
<div class="st"><span class="n">{counts.get('relic',0)}+</span><span class="l">Relic</span></div>
<div class="st"><span class="n">{counts.get('insert',0)}</span><span class="l">Inserts</span></div>
<div class="st"><span class="n">{total:,}</span><span class="l">Total Unique</span></div>
<div class="st"><span class="n">{base_par_count}</span><span class="l">Parallel Types</span></div>
</div></div>
<div class="note">Independently verified from: Beckett.com, BaseballCardPedia.com, DiamondCardsOnline.com, ChecklistCenter.com, SiteLiftMedia.com. Cross-checked Nov 26, 2026.</div>
<div class="search-bar"><input type="text" id="search" placeholder="Search by number, name, team or position..."></div>
<div class="filters" id="filters">
<button class="fbtn on" data-f="all">All <span class="fc">{total:,}</span></button>
<button class="fbtn" data-f="base">Base <span class="fc">{counts.get('base',0)}</span></button>
<button class="fbtn" data-f="parallels">Parallels <span class="fc">{base_par_count}</span></button>
<button class="fbtn" data-f="insert">Inserts <span class="fc">{counts.get('insert',0)}</span></button>
<button class="fbtn" data-f="auto">Autographs <span class="fc">{counts.get('auto',0)}</span></button>
<button class="fbtn" data-f="relic">Relic <span class="fc">{counts.get('relic',0)}+</span></button>
</div>
{par_panels}
{sections}
<div class="foot"><a href="index.html">&larr; Back to Card Finder</a><br>Verified from 5 independent sources &middot; Nov 26, 2026</div>
</div>
'''

page += r"""<script>
(function(){
  var active='all';
  var filters=document.getElementById('filters');
  var btns=document.querySelectorAll('.fbtn');
  var secs=document.querySelectorAll('.sec');
  var panels=document.querySelectorAll('.par-panel');
  var search=document.getElementById('search');

  // For the "parallels" filter, which section to show (base)
  var PANEL_FOR={base:'base', parallels:'parallels', insert:null, auto:'auto', relic:'relic'};
  var SECTION_FOR={base:'base', parallels:'base', insert:'insert', auto:'auto', relic:'relic'};

  function apply(f){
    var y=window.scrollY;           // preserve scroll — no jump
    active=f;
    btns.forEach(function(b){ b.classList.toggle('on', b.dataset.f===f); });
    // sections
    if(f==='all'){
      secs.forEach(function(s){ s.hidden=false; s.classList.remove('collapsed'); });
    } else {
      var showKey=SECTION_FOR[f];
      secs.forEach(function(s){
        if(s.dataset.type===showKey){ s.hidden=false; s.classList.remove('collapsed'); }
        else { s.hidden=true; }
      });
    }
    // parallel panels
    var pk=PANEL_FOR[f];
    panels.forEach(function(p){ p.classList.toggle('on', !!pk && p.dataset.par===pk); });
    window.scrollTo(0,y);
  }

  filters.addEventListener('click', function(e){
    var b=e.target.closest('.fbtn'); if(!b) return;
    e.preventDefault();
    var f=b.dataset.f;
    if(f===active && f!=='all'){ apply('all'); }   // click active again = clear to All
    else { apply(f); }
  });

  // Collapsible section headers (manual expand/collapse)
  document.addEventListener('click', function(e){
    var head=e.target.closest('.sec-head'); if(!head) return;
    if(e.target.closest('.top-link')) return;      // let Back-to-top work
    head.parentElement.classList.toggle('collapsed');
  });

  // Search: show all sections, filter rows
  search.addEventListener('input', function(e){
    var q=e.target.value.toLowerCase().trim();
    if(q){
      secs.forEach(function(s){ s.hidden=false; s.classList.remove('collapsed'); });
      panels.forEach(function(p){ p.classList.remove('on'); });
      btns.forEach(function(b){ b.classList.toggle('on', b.dataset.f==='all'); });
      active='all';
    }
    document.querySelectorAll('tbody tr').forEach(function(row){
      row.style.display=(!q||row.textContent.toLowerCase().indexOf(q)>=0)?'':'none';
    });
  });

  apply('all');  // default state
})();
</script></body></html>"""

with open('checklist.html', 'w', encoding='utf-8') as f:
    f.write(page)
print(f"checklist.html rebuilt ({os.path.getsize('checklist.html'):,} bytes)")
print(f"  Parallel panels: base={len(pars_by_key.get('base',{}))}, auto={len(pars_by_key.get('auto',{}))}, relic={len(pars_by_key.get('relic',{}))}, insert={len(pars_by_key.get('insert',{}))}")
