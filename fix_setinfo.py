"""Fix the set info panel to match Cardsmith's level of detail."""
import os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))

h = open('index.html', 'r', encoding='utf-8').read()

# Find and replace the FIRST showSetInfo function (the injected one)
# It starts with "function showSetInfo(i){" and ends before the next top-level function

old_fn_pattern = r'function showSetInfo\(i\)\{[^}]*?\$\(\'srcfoot\'\)\.innerHTML=ft;\s*\}'

# Build the new showSetInfo function
new_fn = r"""function showSetInfo(i){
 var s=D[i],m=s.meta;
 if(!m){$('setInfo').hidden=true;return;}
 var h='<div class="set-info">';
 h+='<div class="set-title">'+esc(s.title)+'</div>';
 h+='<div class="set-detail">';
 h+='<b>'+esc(m.year)+' '+esc(m.brand)+'</b> &middot; '+esc(m.line)+' &middot; '+esc(m.sport);
 if(m.program)h+=' &middot; '+esc(m.program);
 h+='<br>Release Date: '+esc(m.release||'TBD')+' &middot; Checklist updated Nov 26';
 h+='<br>'+esc(s.title)+' checklist: '+(m.uniqueCards?m.uniqueCards.toLocaleString():'?')+' cards in '+s.families.length+' sets, with print runs for Hobby and H2, released '+(m.release||'TBD')+'.';
 h+='</div>';
"""

new_fn += r"""
 // Tags
 h+='<div class="set-tags">';
 h+='<span class="stag">'+esc(s.title)+'</span>';
 h+='<span class="stag">Hobby</span><span class="stag">H2</span><span class="stag">Mega</span><span class="stag">Blaster</span><span class="stag">Factory Set</span>';
 h+='</div>';

 // Links
 h+='<div class="set-links">';
 if(m.links&&m.links.checklist)h+='<a href="'+m.links.checklist+'" target="_blank">&#128203; Full Checklist</a>';
 if(m.links&&m.links.sellSheet)h+='<a href="'+m.links.sellSheet+'" target="_blank" class="sec">&#128196; Beckett Guide</a>';
 h+='</div>';

 // Box config table
 h+='<table class="box-cfg"><tr><th></th><th>Hobby</th><th>H2</th><th>Mega</th><th>Blaster</th></tr>';
 h+='<tr><td>Packs &times; cards</td><td>12&times;12</td><td>12&times;5</td><td>10&times;4</td><td>6&times;4</td></tr>';
 h+='<tr><td>Cards per box</td><td>144</td><td>60</td><td>40</td><td>24</td></tr>';
 h+='<tr><td>Hits (avg)</td><td>6 auto/mem</td><td>3 auto</td><td>3 auto/mem</td><td>2 auto/mem</td></tr>';
 h+='</table>';
"""

new_fn += r"""
 // Stats grid
 h+='<div class="set-stats">';
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
}"""

# Count how many showSetInfo functions exist
count = len(re.findall(r'function showSetInfo\(', h))
print(f"Found {count} showSetInfo functions")

# Replace ALL showSetInfo functions with the new one
# Use regex that matches from "function showSetInfo(i){" to the closing "}" after srcfoot
pattern = re.compile(r'function showSetInfo\(i\)\{.*?\$\(\'srcfoot\'\)\.innerHTML=ft;\s*\}', re.DOTALL)
matches = pattern.findall(h)
print(f"Regex matched {len(matches)} function bodies")

h_new = pattern.sub(lambda mm: new_fn, h)

# Add CSS for tags and box config table if not present
if '.set-tags' not in h_new:
    css_add = """
.set-tags{display:flex;flex-wrap:wrap;gap:5px;margin:8px 0}
.set-tags .stag{padding:3px 10px;border-radius:12px;background:var(--surface2);font:600 11px inherit;color:var(--fg);border:1px solid var(--border)}
.box-cfg{width:100%;border-collapse:collapse;margin:10px 0;font-size:13px}
.box-cfg th{background:var(--accent);color:#fff;padding:5px 6px;text-align:center;font-weight:700}
.box-cfg td{padding:4px 6px;border:1px solid var(--border);text-align:center}
.box-cfg td:first-child{text-align:left;color:var(--muted);font-weight:600}
"""
    h_new = h_new.replace('</style>', css_add + '</style>')
    print("Added CSS for tags and box config")

open('index.html', 'w', encoding='utf-8').write(h_new)
print(f"Done. Materials labels: {h_new.count('>Materials<')}, Relic labels: {h_new.count('>Relic<')}")
print(f"Box config tables: {h_new.count('box-cfg')}, Tags: {h_new.count('set-tags')}")
