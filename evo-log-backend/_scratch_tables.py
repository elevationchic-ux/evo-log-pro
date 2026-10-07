import re
with open('app/main.py','r',encoding='utf-8') as f:
    lines = f.readlines()
last = None
for i, l in enumerate(lines):
    m = re.match(r'# </expansion:([^>]+)>', l.strip())
    if m:
        last = (i+1, m.group(1))
print('last expansion close:', last)
print('line preview:')
for i in range(max(0,last[0]-3), min(len(lines), last[0]+3)):
    print(i+1, ':', lines[i].rstrip())
