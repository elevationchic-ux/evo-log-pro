import json, collections
d = json.load(open('_gap_report.json'))
print('Total:', len(d))
c = collections.Counter(x['genre'] for x in d)
for k, v in c.most_common():
    print(f'  {k}: {v}')
print()
print("=== Non-couverts (vrais trous) ===")
for x in d:
    if x['genre'] not in ('couvert', 'joker_ambigu'):
        print(f"  [{x['genre']}] {x['appel']} ({x.get('fichier','?')})")
