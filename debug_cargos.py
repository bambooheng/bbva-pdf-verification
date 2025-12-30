import json

def analyze_cargos():
    with open('inputs/MSN20251105129银行流水1.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cargos = []
    
    # 遍历所有 section 查找交易
    if 'content' in data and 'sections' in data['content']:
        for section in data['content']['sections']:
            if section.get('section_type') == 'transactions':
                for item in section.get('data', []):
                    cargo_val = item.get('CARGOS', '')
                    if cargo_val and cargo_val.strip():
                        cargos.append({
                            'desc': item.get('DESCRIPCIÓN'),
                            'amount': cargo_val
                        })
    
    print(f"Total separate transaction sections found: {len(cargos)}")
    print("-" * 50)
    for idx, c in enumerate(cargos, 1):
        print(f"{idx}. {c['desc']} | {c['amount']}")

if __name__ == "__main__":
    analyze_cargos()
