"""Set-info panel: 3 separate working links, spaced stat breakdown, clean styling.
Also fix the mojibake dash in finish()."""
import os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
h = open('index.html', 'r', encoding='utf-8').read()

# 1. Update the Stars & Stripes meta.links to include odds + sellSheet (verified URLs)
#    Current embedded: "links": {"checklist": "checklist.html", "sellSheet": "https://cardsmithsbreaks..."}
#    Replace the whole links object for stars-stripes.
h = re.sub(
    r'"links":\s*\{[^}]*"checklist":\s*"checklist\.html"[^}]*\}',
    '"links": {"checklist": "checklist.html", "odds": "https://cardsmithsbreaks.com/full-checklist/2026-panini-usa-stars-stripes-prizm-baseball/", "sellSheet": "https://blog.paniniamerica.net/?p=297497"}',
    h, count=1
)

# 2. Replace BOTH showSetInfo functions with a clean version
new_fn = r"""function showSetInfo(i){
 var s=D[i],m=s.meta;
 if(!m){$('setInfo').hidden=true;return;}
 var fams=s.families||[];
 function cnt(t){return fams.filter(function(f){return f.type===t;}).reduce(function(a,f){return a+f.cards.length;},0);}
 function nsets(t){return fams.filter(function(f){return f.type===t;}).length;}
 var h='<div class="set-info">';
 h+='<div class="set-title">'+esc(s.title)+'</div>';
 h+='<div class="set-meta"><b>'+esc(m.year)+' '+esc(m.brand)+'</b> &middot; '+esc(m.line)+' &middot; '+esc(m.sport)+'</div>';
 h+='<div class="set-rel">Release Date: '+esc(m.release||'TBD')+' &middot; Checklist updated Nov 26, 2026</div>';
 // Links row (only those that exist)
 h+='<div class="set-links">';
 if(m.links&&m.links.checklist)h+='<a class="slink" href="'+m.links.checklist+'" target="_blank" rel="noopener">Checklist &rarr;</a>';
 if(m.links&&m.links.odds)h+='<a class="slink" href="'+m.links.odds+'" target="_blank" rel="noopener">Odds &amp; Print Runs &rarr;</a>';
 if(m.links&&m.links.sellSheet)h+='<a class="slink" href="'+m.links.sellSheet+'" target="_blank" rel="noopener">Sell Sheet &rarr;</a>';
 h+='</div>';
 // Spaced breakdown
 h+='<div class="set-break">';
 h+='<div class="brow"><span class="bk">Base</span><span class="bv">'+cnt('Base')+' cards</span></div>';
 var ac=cnt('Autograph'); if(ac)h+='<div class="brow"><span class="bk">Autographs</span><span class="bv">'+ac+' cards across '+nsets('Autograph')+' sets</span></div>';
 var rc=cnt('Memorabilia'); if(rc)h+='<div class="brow"><span class="bk">Relic / Game-Used</span><span class="bv">'+rc+'+ cards across '+nsets('Memorabilia')+' sets</span></div>';
 var ic=cnt('Insert'); if(ic)h+='<div class="brow"><span class="bk">Inserts</span><span class="bv">'+ic+' cards across '+nsets('Insert')+' sets</span></div>';
 if(m.uniqueCards)h+='<div class="brow"><span class="bk">Unique cards (before parallels)</span><span class="bv">'+m.uniqueCards.toLocaleString()+'</span></div>';
 if(m.baseParallels)h+='<div class="brow"><span class="bk">Parallel types</span><span class="bv">'+m.baseParallels+' base &middot; 16 auto &middot; 13 relic</span></div>';
 h+='</div>';
 h+='</div>';
 $('setInfo').innerHTML=h;$('setInfo').hidden=false;
 var ft='';
 if(m.sources)ft+='Verified: '+m.sources.join(', ')+'.';
 if(m.totalWithParallels)ft+=' Total rows including all parallel variants: '+m.totalWithParallels.toLocaleString()+'.';
 $('srcfoot').innerHTML=ft;
}"""

pattern = re.compile(r'function showSetInfo\(i\)\{.*?\$\(\'srcfoot\'\)\.innerHTML=ft;\s*\}', re.DOTALL)
n = len(pattern.findall(h))
h = pattern.sub(lambda mm: new_fn, h)
print(f"Replaced {n} showSetInfo function(s)")

# 3. Fix the mojibake dash in finish() -> proper en dash via – safe literal
h = h.replace("(v.v==='Standard'?'':' � '+esc(v.v))", "(v.v==='Standard'?'':' – '+esc(v.v))")
# also catch any literal replacement-char dash
h = h.replace("' � '+esc(v.v)", "' – '+esc(v.v)")

open('index.html','w',encoding='utf-8').write(h)
print("mojibake dash present:", '�' in h)
