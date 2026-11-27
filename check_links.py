"""Extract every external link (href=http...) from index.html and checklist.html."""
import os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
for fn in ['index.html', 'checklist.html']:
    h = open(fn, 'r', encoding='utf-8').read()
    links = set(re.findall(r'href=[\'"](https?://[^\'"]+)[\'"]', h))
    # Also catch links built in JS strings
    js_links = set(re.findall(r'href="\'\+[^+]+\+\'"', h))
    print(f"=== {fn} ===")
    for l in sorted(links):
        print(f"  {l}")
    # Find sellSheet/checklist URLs in the data metadata
    for m in re.finditer(r'"(sellSheet|checklist|beckettGuide)":\s*"([^"]+)"', h):
        print(f"  [meta {m.group(1)}]: {m.group(2)}")
