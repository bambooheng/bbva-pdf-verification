import pandas as pd
import os

def inspect_rules():
    file_path = 'inputs/bbva_llm_rules_verification.xlsx'
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    try:
        df = pd.read_excel(file_path)
        print(f"Loaded rules from {file_path}")
        print("-" * 50)
        
        # Check for expected columns
        expected_cols = ['Rule ID', 'Condition Logic', 'Decision Result']
        for col in expected_cols:
            if col not in df.columns:
                print(f"WARNING: Column '{col}' not found in Excel!")
        
        # Print all rules
        for index, row in df.iterrows():
            rule_id = row.get('Rule ID', 'N/A')
            print(f"Rule: {rule_id}")
            print(f"Logic: {row.get('Condition Logic', 'N/A')}")
            print(f"Decision: {row.get('Decision Result', 'N/A')}")
            print("-" * 30)

    except Exception as e:
        print(f"Error reading excel: {e}")

if __name__ == "__main__":
    inspect_rules()
