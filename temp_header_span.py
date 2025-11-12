import json
from pathlib import Path

path = next(Path('inputs').glob('BBVA JUN-JUL*_structured.json'))
with path.open(encoding='utf-8') as f:
    data = json.load(f)

page2 = data['pages'][1]
for elem in page2['layout_elements']:
    for line in elem.get('lines') or []:
        text = (line.get('text') or '').strip()
        if 'CARGOS' in text.upper() and 'ABONOS' in text.upper():
            print('line:', text)
            for span in line.get('spans') or []:
                print(' span:', span.get('text'), 'bbox:', span.get('bbox'))
