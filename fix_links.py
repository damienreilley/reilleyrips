"""Replace the dead Beckett link with the working Cardsmith's Breaks checklist.
Update both index.html (live) and write_index.py (future rebuilds)."""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

DEAD = "https://www.beckett.com/news/2026-panini-stars-stripes-prizm-usa-baseball-cards/"
GOOD = "https://cardsmithsbreaks.com/full-checklist/2026-panini-usa-stars-stripes-prizm-baseball/"

for fn in ['index.html', 'write_index.py', 'rebuild_checklist.py', 'build_master_xlsx.py']:
    if not os.path.exists(fn):
        continue
    h = open(fn, 'r', encoding='utf-8').read()
    n = h.count(DEAD)
    if n:
        h = h.replace(DEAD, GOOD)
        # Also change link label "Beckett Guide" to "Checklist & Print Runs"
        h = h.replace('Beckett Guide</a>', 'Checklist &amp; Odds</a>')
        h = h.replace('&#128196; Beckett Guide', '&#128196; Checklist &amp; Odds')
        open(fn, 'w', encoding='utf-8').write(h)
        print(f"{fn}: replaced {n} dead link(s)")
    else:
        print(f"{fn}: no dead link found")

# Verify index.html
h = open('index.html', 'r', encoding='utf-8').read()
print(f"\nindex.html now: Beckett links={h.count('beckett.com')}, Cardsmith links={h.count('cardsmithsbreaks.com')}")
