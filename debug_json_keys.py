import json
import os

path = r"D:\Mstar\4.MSN20251028359银行流水1_20251231问题单\MSN20251028359银行流水1\MSN20251028359银行流水1.json"

try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("JSON Loaded Successfully")
    
    sections = data.get('content', {}).get('sections', [])
    for section in sections:
        if 'detalle de movimientos' in section.get('title', '').lower():
            print(f"Found Section: {section.get('title')}")
            txns = section.get('data', [])
            if txns:
                first_txn = txns[0]
                print(f"First Transaction Keys (Raw): {list(first_txn.keys())}")
                print(f"First Transaction Keys (Repr): {[repr(k) for k in first_txn.keys()]}")
                
                # Check specific keys
                for k in first_txn.keys():
                    if "OPER" in k:
                        print(f"Key containing OPER: '{k}' -> repr: {repr(k)}")
                        # Check unicode hex
                        print(f"  Hex: {[hex(ord(c)) for c in k]}")
            else:
                print("No transactions in this section")
            break
except Exception as e:
    print(f"Error: {e}")
