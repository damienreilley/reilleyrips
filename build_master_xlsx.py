#!/usr/bin/env python3
"""Build master checklist xlsx from verified JSON data."""
import json, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('data/stars-stripes.json', 'r', encoding='utf-8') as f:
    ss = json.load(f)

wb = Workbook()
hdr_fill = PatternFill(start_color="8F261F", end_color="8F261F", fill_type="solid")
hdr_font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
fills = {
    'Base': PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid"),
    'Autograph': PatternFill(start_color="FFF3E0", end_color="FFF3E0", fill_type="solid"),
    'Memorabilia': PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid"),
    'Insert': PatternFill(start_color="F3E5F5", end_color="F3E5F5", fill_type="solid"),
}
labels = {'Base':'Base','Autograph':'Autograph','Memorabilia':'Relic','Insert':'Insert'}
thin = Border(left=Side(style='thin',color='BDBDBD'),right=Side(style='thin',color='BDBDBD'),
              top=Side(style='thin',color='BDBDBD'),bottom=Side(style='thin',color='BDBDBD'))
# Order families to match the website filter order: Base -> Insert -> Autograph -> Relic
_order = {'Base':0,'Insert':1,'Autograph':2,'Memorabilia':3}
families = sorted(ss.get('families', []), key=lambda f: _order.get(f['type'], 9))

# SHEET 1: Master Checklist
ws = wb.active
ws.title = "Master Checklist"
headers = ["#","Card #","Player","Team","Position","Type","Set","Parallel Count"]
for col, h in enumerate(headers, 1):
    c = ws.cell(row=1, column=col, value=h)
    c.font = hdr_font; c.fill = hdr_fill; c.alignment = Alignment(horizontal='center'); c.border = thin

row_num = 2; card_count = 0
for fam in families:
    cat = labels.get(fam['type'], fam['type'])
    fill = fills.get(fam['type'])
    pc = len(fam['cards'][0].get('r',{})) if fam['cards'] and fam['cards'][0].get('r') else 0
    for card in fam['cards']:
        card_count += 1
        vals = [card_count, card['n'], card['a'], card.get('t',''), card.get('p',''), cat, fam['name'], pc if pc else '']
        for col, v in enumerate(vals, 1):
            c = ws.cell(row=row_num, column=col, value=v)
            c.border = thin
            if fill: c.fill = fill
        row_num += 1
widths = [6,8,28,45,12,12,40,14]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = 'A2'
ws.auto_filter.ref = f"A1:H{row_num-1}"

# SHEET 2: Summary
ws2 = wb.create_sheet("Summary")
ws2.column_dimensions['A'].width = 35; ws2.column_dimensions['B'].width = 12; ws2.column_dimensions['C'].width = 55
ws2.cell(row=1, column=1, value="2026 Panini Stars & Stripes Prizm USA Baseball").font = Font(bold=True, size=14)
ws2.cell(row=2, column=1, value="Master Checklist - Independently Verified").font = Font(italic=True, size=11, color="666666")
ws2.cell(row=3, column=1, value="Sources: Beckett, BaseballCardPedia, DiamondCardsOnline, ChecklistCenter, SiteLiftMedia")
r = 5
for h in ["Type","Cards","Sets"]:
    ws2.cell(row=r, column=["Type","Cards","Sets"].index(h)+1, value=h).font = Font(bold=True)
for ct, cl in [('Base','Base'),('Insert','Inserts'),('Autograph','Autographs'),('Memorabilia','Relic / Game-Used')]:
    r += 1
    fams = [f for f in families if f['type']==ct]
    count = sum(len(f['cards']) for f in fams)
    names = ', '.join(f['name']+f' ({len(f["cards"])})' for f in fams)
    fill = fills.get(ct)
    for col in range(1,4):
        ws2.cell(row=r, column=col).fill = fill
    ws2.cell(row=r, column=1, value=cl)
    ws2.cell(row=r, column=2, value=count)
    ws2.cell(row=r, column=3, value=names)
r += 1
ws2.cell(row=r, column=1, value="TOTAL UNIQUE CARDS").font = Font(bold=True)
ws2.cell(row=r, column=2, value=card_count).font = Font(bold=True)

# SHEET 3: Parallels
ws3 = wb.create_sheet("Parallels")
ws3.column_dimensions['A'].width = 25; ws3.column_dimensions['B'].width = 12; ws3.column_dimensions['C'].width = 22
for col, h in enumerate(["Parallel Name","Print Run","Notes"], 1):
    c = ws3.cell(row=1, column=col, value=h); c.font = hdr_font; c.fill = hdr_fill
base_card = families[0]['cards'][0]
pars = base_card.get('r', {})
pr = 2
for name, run in pars.items():
    ws3.cell(row=pr, column=1, value=name)
    ws3.cell(row=pr, column=2, value=('1/1' if run=='1' else int(run)) if run else 'Unnumbered')
    note = ''
    if 'Ice' in name and 'Disco' not in name and 'Cracked' not in name: note = 'Mega Box exclusive'
    elif 'Disco' in name: note = 'H2 exclusive'
    elif 'Cherry' in name: note = 'Hobby exclusive'
    elif 'Box Set' in name or 'Pandora' in name: note = 'Factory Set exclusive'
    ws3.cell(row=pr, column=3, value=note)
    pr += 1
ws3.freeze_panes = 'A2'

# SHEET 4: By Subset
ws4 = wb.create_sheet("By Set")
ws4.column_dimensions['A'].width = 30; ws4.column_dimensions['B'].width = 8
ws4.column_dimensions['C'].width = 28; ws4.column_dimensions['D'].width = 45; ws4.column_dimensions['E'].width = 12
r4 = 1
for fam in families:
    cat = labels.get(fam['type'], fam['type'])
    fill = fills.get(fam['type'])
    ws4.cell(row=r4, column=1, value=f"{fam['name']} ({cat})").font = Font(bold=True, size=12)
    ws4.cell(row=r4, column=2, value=f"{len(fam['cards'])} cards").font = Font(italic=True, color="666666")
    r4 += 1
    for col, h in enumerate(["Set","#","Player","Team","Position"], 1):
        c = ws4.cell(row=r4, column=col, value=h); c.font = Font(bold=True, size=10)
        if fill: c.fill = fill
    r4 += 1
    for card in fam['cards']:
        ws4.cell(row=r4, column=1, value=fam['name'])
        ws4.cell(row=r4, column=2, value=card['n'])
        ws4.cell(row=r4, column=3, value=card['a'])
        ws4.cell(row=r4, column=4, value=card.get('t',''))
        ws4.cell(row=r4, column=5, value=card.get('p',''))
        r4 += 1
    r4 += 1

# Save to Master Checklist folder
outdir = r"C:\Users\damie\OneDrive\Gifts-Presents\Baseball Cards\cheat sheets - Info Sheets\2026 Panini Prizm USA Stars n Stripes Baseball\Master Checklist"
outpath = os.path.join(outdir, "2026_Panini_Stars_Stripes_Prizm_Master_Checklist_v2.xlsx")
wb.save(outpath)
print(f"Saved: {outpath}")
print(f"  {card_count} unique cards, {len(pars)} parallel types, {len(families)} subsets, 4 sheets")
print(f"  File size: {os.path.getsize(outpath):,} bytes")
