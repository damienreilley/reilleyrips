"""Remove the tags row and box-config table I added without being asked.
Keep only: title, detail line, links, stats grid."""
import os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
h = open('index.html', 'r', encoding='utf-8').read()

# Remove the tags block: from "// Tags" through the set-tags div close
h = re.sub(r"\s*// Tags\s*\n\s*h\+='<div class=\"set-tags\">';.*?h\+='</div>';\s*\n", "\n", h, flags=re.DOTALL)

# Remove the box config block: from "// Box config table" through the table close
h = re.sub(r"\s*// Box config table\s*\n\s*h\+='<table class=\"box-cfg\">.*?</table>';\s*\n", "\n", h, flags=re.DOTALL)

open('index.html', 'w', encoding='utf-8').write(h)
print("set-tags remaining:", h.count('set-tags'))
print("box-cfg remaining:", h.count("class=\"box-cfg\""))
print("stag chips remaining:", h.count("class=\"stag\""))
