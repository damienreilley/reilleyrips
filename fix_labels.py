import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
h = open('index.html', 'r', encoding='utf-8').read()
# Replace every remaining Materials label in JS
old = 'class="l">Materials</span>'
new = 'class="l">Relic</span>'
count = h.count(old)
h = h.replace(old, new)
open('index.html', 'w', encoding='utf-8').write(h)
print(f'Replaced {count} occurrences. Materials labels remaining: {h.count(">Materials<")}')
print(f'Relic labels: {h.count(">Relic<")}')
