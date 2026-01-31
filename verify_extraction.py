from src.data_loader import DataLoader
import json
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

path = r"D:\Mstar\4.MSN20251028359银行流水1_20251231问题单\MSN20251028359银行流水1\MSN20251028359银行流水1.json"

# Initialize DataLoader with minimal valid args
dl = DataLoader(path, "dummy.xlsx")

try:
    print(f"Loading data from {path}")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Extracting transactions...")
    txns = dl.extract_detalle_transactions(data)
    
    print(f"Total transactions extracted: {len(txns)}")
    
    if len(txns) > 1:
        txn2 = txns[1]
        print("\n--- Transaction Index 2 (0-based index 1) ---")
        print(f"Oper: {txn2.get('oper')}")
        print(f"Description: {txn2.get('description')}")
        # Check raw extraction key
        print(f"Operacion (Extracted): '{txn2.get('operacion')}'")
        
        # Also simulate format_detalle_transactions
        formatted = dl.format_detalle_transactions(txns[:5]) # Show first 5
        print("\n--- Formatted Output (First 5) ---")
        print(formatted)
        
    else:
        print("Not enough transactions extracted.")

except Exception as e:
    print(f"Error: {e}")
