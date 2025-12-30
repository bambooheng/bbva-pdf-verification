import logging
import sys
from pathlib import Path
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from src.data_loader import DataLoader

# Configure logging to console
logging.basicConfig(level=logging.INFO)

def test_context_extraction():
    # Paths
    json_path = r"D:\Mstar\bbva-pdf-verification_部署版本\inputs\MSN20250923030银行流水1.json"
    excel_path = r"D:\Mstar\bbva-pdf-verification_部署版本\inputs\bbva_llm_rules_verification.xlsx"

    
    loader = DataLoader(json_path, excel_path)
    
    # Load data
    try:
        data = loader.load_bank_statement()
        print(f"Loaded JSON. Keys: {data.keys()}")
        if 'content' in data:
            print(f"Content keys: {data['content'].keys()}")
            if 'sections' in data['content']:
                print(f"Number of sections: {len(data['content']['sections'])}")
                for i, sec in enumerate(data['content']['sections']):
                    print(f"Section {i} Type: {sec.get('section_type')}")
                    if sec.get('section_type') == 'account_details':
                        print(f"  FOUND account_details: {sec.get('data')}")

        if 'page_metadata' in data:
             print(f"Page Metadata: {data['page_metadata']}")

    except Exception as e:
        print(f"Failed to load data: {e}")
        return

    # Mock Rule for MSTAR_BBVA_DTL_AMT_SINGLE (Rolling Balance)
    rule = {
        'rule_id': 'MSTAR_BBVA_DTL_AMT_SINGLE',
        'rule_name': 'Rolling Balance Check',
        'condition_logic': 'Verify rolling balance from detalle de movimientos',
        'validation_rule': 'Balance check'
    }
    
    print("\n--- Generating Context ---")
    
    # Debug extraction directly first
    print("Debugging extract_detalle_transactions:")
    txns = loader.extract_detalle_transactions(data)
    print(f"Extracted {len(txns)} transactions directly.")
    if len(txns) > 0:
        print(f"First transaction: {txns[0]}")
    else:
        print("WARNING: No transactions extracted!")

    context = loader.get_relevant_text_content(data, rule)
    
    print("\n[Start of Context]")
    print(context)
    print("[End of Context]")

    if "Periodo" in context:
        print("\nSUCCESS: 'Periodo' found in context.")
    else:
        print("\nFAILURE: 'Periodo' NOT found in context.")

if __name__ == "__main__":
    test_context_extraction()
