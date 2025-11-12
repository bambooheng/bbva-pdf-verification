import json
from pathlib import Path
from src.data_loader import DataLoader

path = next(Path('inputs').glob('BBVA JUN-JUL*_structured.json'))
dl = DataLoader(str(path), 'inputs/bbva_llm_rules_verification.xlsx')
with path.open(encoding='utf-8') as f:
    data = json.load(f)

page2 = data['pages'][1]
print(dl._compute_detalle_column_ranges(page2['layout_elements']))
