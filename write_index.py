#!/usr/bin/env python3
"""Generate the new index.html from existing data + new UI template."""
import json, os, re

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Read old index to get the full JS app logic + browse mode
with open('index.html', 'r', encoding='utf-8') as f:
    old = f.read()

# Extract the data JSON
m = re.search(r'var D=(\[.*?\]);\s*var S', old, re.DOTALL)
if not m:
    m = re.search(r'var D=(\[.*?\]);', old, re.DOTALL)
data_json = m.group(1) if m else '[]'

# Load and inject metadata
data = json.loads(data_json)
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
                     "sellSheet":"https://cardsmithsbreaks.com/full-checklist/2026-panini-usa-stars-stripes-prizm-baseball/"},
            "sources":["Beckett.com","BaseballCardPedia.com","DiamondCardsOnline.com","ChecklistCenter.com","SiteLiftMedia.com"]
        }
    elif 'Halloween' in s.get('title','') or 'Score-A-Treat' in s.get('title',''):
        s['meta'] = {
            "year":"2026","brand":"Panini","line":"Score-A-Treat",
            "sport":"Multi-Sport","program":"Halloween","release":"2026",
            "uniqueCards":641,"baseCards":297,"autoCards":297,"insertCards":47,
            "links":{},"sources":["Two checklist sites"]
        }

# Re-serialize with metadata
data_json_new = json.dumps(data, ensure_ascii=False)

# Extract the existing JS functions (everything after var D=...;)
js_start = old.find('<script>') + 8
js_end = old.find('</script>')
full_js = old[js_start:js_end]

# Remove the old D= declaration, keep the rest
app_js = re.sub(r'var D=\[.*?\];', '', full_js, count=1, flags=re.DOTALL).strip()

# Get the second script block (browse mode)
scripts = old.split('<script>')
browse_js = ''
if len(scripts) > 2:
    browse_js = scripts[2].split('</script>')[0]

# Modify pickSet to call showSetInfo
app_js = app_js.replace(
    "function pickSet(i){S.set=i;",
    "function pickSet(i){S.set=i;showSetInfo(i);"
)

# Replace $('src').textContent=D[i].src; with nothing (we use footer now)
app_js = app_js.replace("$('src').textContent=D[i].src;", "")

# Replace "Question" with "Step" labels
app_js = app_js.replace("'Question '", "'Step '")

# Add the showSetInfo function before the init/pickSet area
set_info_fn = r"""
function showSetInfo(i){
 var s=D[i],m=s.meta;
 if(!m){$('setInfo').hidden=true;return;}
 var h='<div class="set-info">';
 h+='<div class="set-title">'+esc(s.title)+'</div>';
 h+='<div class="set-detail"><b>'+esc(m.year)+' '+esc(m.brand)+'</b> &middot; '+esc(m.line)+' &middot; '+esc(m.sport);
 if(m.program)h+=' &middot; '+esc(m.program);
 if(m.release)h+='<br>Released: '+esc(m.release);
 h+='</div><div class="set-links">';
 if(m.links&&m.links.checklist)h+='<a href="'+m.links.checklist+'" target="_blank">&#128203; Full Checklist</a>';
 if(m.links&&m.links.sellSheet)h+='<a href="'+m.links.sellSheet+'" target="_blank" class="sec">&#128196; Checklist &amp; Odds</a>';
 h+='</div><div class="set-stats">';
 if(m.baseCards)h+='<div class="st"><span class="n">'+m.baseCards+'</span><span class="l">Base</span></div>';
 if(m.autoCards)h+='<div class="st"><span class="n">'+m.autoCards+'</span><span class="l">Autos</span></div>';
 if(m.matCards)h+='<div class="st"><span class="n">'+m.matCards+'+</span><span class="l">Relic</span></div>';
 if(m.insertCards)h+='<div class="st"><span class="n">'+m.insertCards+'</span><span class="l">Inserts</span></div>';
 if(m.uniqueCards)h+='<div class="st"><span class="n">'+m.uniqueCards.toLocaleString()+'</span><span class="l">Total Unique</span></div>';
 if(m.baseParallels)h+='<div class="st"><span class="n">'+m.baseParallels+'</span><span class="l">Parallel Types</span></div>';
 h+='</div></div>';
 $('setInfo').innerHTML=h;$('setInfo').hidden=false;
 var ft='';
 if(m.sources)ft+='Verified: '+m.sources.join(', ')+'.';
 if(m.totalWithParallels)ft+=' Total rows including all parallel variants: '+m.totalWithParallels.toLocaleString()+'.';
 $('srcfoot').innerHTML=ft;
}
"""

app_js = set_info_fn + '\n' + app_js

# Read CSS from old file
css_start = old.find('<style>') + 7
css_end = old.find('</style>')
old_css = old[css_start:css_end]

# Add new CSS for set-info panel
new_css = old_css + """
.set-info{background:var(--surface);border:2px solid var(--accent);border-radius:14px;padding:18px;margin-bottom:14px}
.set-info .set-title{font:900 20px/1.15 Georgia,serif;color:var(--accent);margin:0 0 2px}
.set-info .set-detail{font:600 13px/1.4 inherit;color:var(--muted);margin:0 0 10px}
.set-info .set-links{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.set-info .set-links a{display:inline-flex;align-items:center;gap:5px;padding:8px 14px;background:var(--accent);color:var(--accentfg);border-radius:8px;font:700 13px inherit;text-decoration:none;min-height:38px}
.set-info .set-links a:hover{opacity:.85}
.set-info .set-links a.sec{background:var(--surface2);color:var(--fg);border:1px solid var(--border)}
.set-stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:6px;margin:10px 0 0}
.set-stats .st{background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:6px 8px;text-align:center}
.set-stats .st .n{font:800 20px ui-monospace,Menlo,monospace;color:var(--accent);display:block}
.set-stats .st .l{font:600 11px inherit;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.foot{text-align:center;padding:16px 10px;font-size:12px;color:var(--muted)}
.foot a{color:var(--accent)}
"""

# Build the new HTML
body_html = '''<div class="wrap">
<header>
<div class="eyebrow">Reilley's Rip</div>
<h1>What did you pull?</h1>
<p class="sub">Pick your set, then find your card in 3 quick steps.</p>
</header>

<div class="step" id="s1">
<span class="num">Step 1 &#8212; Pick your set</span>
<h2>Which pack did it come from?</h2>
<div class="choices" id="sets"></div>
</div>

<div id="setInfo" hidden></div>

<div class="step" id="s2" hidden>
<span class="num">Step 2 &#8212; Find the card</span>
<h2>Flip the card over. What is the card number?</h2>
<p class="hint">Pick a way to find the card. Any of these works.</p>
<div class="brws" id="brws">
<button type="button" data-br="num" class="br on">Type number or name</button>
<button type="button" data-br="player" class="br">Browse by player A-Z</button>
<button type="button" data-br="team" class="br">Browse by team</button>
<button type="button" data-br="design" class="br">Browse by design</button>
</div>
<div id="qwrap"><input id="q" type="search" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="number or name" enterkeyhint="search">
<div class="list" id="cl"></div></div>
<div class="picked" id="picked" hidden></div>
</div>

<div class="step" id="s3" hidden>
<span class="num">Step 3 &#8212; Numbered?</span>
<h2>Is there a number stamped on it, like <span style="font-family:ui-monospace,Menlo,monospace;background:var(--surface2);padding:1px 8px;border-radius:5px">23/99</span>?</h2>
<p class="hint">Look on the front and the back. It is usually shiny foil.</p>
<div class="yn">
<button type="button" data-a="yes"><span>&#10003; Yes</span><small>I see a number with a slash</small></button>
<button type="button" data-a="no"><span>&#10007; No</span><small>No stamped number</small></button>
</div>
</div>

<div class="step" id="s4" hidden>
<span class="num" id="s4n">Step 4</span>
<h2 id="s4h"></h2><p class="hint" id="s4p"></p>
<div class="runs" id="runs"></div>
<div class="cards" id="vcards"></div>
<p class="note" id="s4note"></p>
</div>

<div class="step final" id="fin" hidden></div>

<div class="foot" id="srcfoot"></div>
</div>'''

new_html = '<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">\n'
new_html += '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
new_html += '<meta name="robots" content="noindex,nofollow">\n'
new_html += "<title>Reilley's Rip — Card Finder</title>\n"
new_html += '<style>\n' + new_css + '\n</style></head><body>\n'
new_html += body_html + '\n'
new_html += '<script>\nvar D=' + data_json_new + ';\n' + app_js + '\n</script>\n'
if browse_js:
    new_html += '<script>\n' + browse_js + '\n</script>\n'
new_html += '</body></html>\n'

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"index.html written ({os.path.getsize('index.html'):,} bytes)")
print("Done! All files ready. Run: git add -A && git commit -m 'Rebuild' && git push")
