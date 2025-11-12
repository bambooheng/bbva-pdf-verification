import json
from pathlib import Path

path = next(Path('inputs').glob('BBVA JUN-JUL*_structured.json'))
with path.open(encoding='utf-8') as f:
    data = json.load(f)

for page in data['pages']:
    if page.get('page_number') == 4:
        for elem in page.get('layout_elements', []):
            for line in elem.get('lines') or []:
                text = (line.get('text') or '').strip()
                if '110,490.00' in text:
                    print(line['bbox'])
                    print(text)
        break
