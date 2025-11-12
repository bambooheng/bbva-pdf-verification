import json
from pathlib import Path

path = next(Path('inputs').glob('BBVA JUN-JUL*_structured.json'))
with path.open(encoding='utf-8') as f:
    data = json.load(f)

for page in data['pages']:
    if page.get('page_number') == 4:
        entries = []
        for elem in page.get('layout_elements', []):
            bbox = elem.get('bbox') or {}
            y = bbox.get('y')
            if y is None:
                continue
            for line in elem.get('lines') or []:
                text = (line.get('text') or '').strip()
                if not text:
                    continue
                ly = line['bbox'][1]
                lx = line['bbox'][0]
                entries.append((ly, lx, text))
        entries.sort()
        for ly, lx, text in entries:
            if abs(ly - 409.0) < 5 or abs(ly - 409.0) < 0.001:
                print(f"y={ly:.3f}, x={lx:.3f}, text={text}")
            if '110,490.00' in text or 'SPEI RECIBIDOSANTANDER' in text or '17/JUL' in text:
                print(f"y={ly:.3f}, x={lx:.3f}, text={text}")
        break
