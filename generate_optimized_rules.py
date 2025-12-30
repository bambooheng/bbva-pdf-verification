import pandas as pd
import os

def create_optimized_rules():
    # Define optimized rules with LLM-friendly Chain-of-Thought logic
    rules_data = [
        {
            "Rule ID": "MSTAR_BBVA_DTL_CNT_CARGOS",
            "Rule Name": "明细交易笔数校验_出账笔数",
            "Condition Logic": "(Step 1) 从 'Comportamiento' 表格中提取 'Retiros / Cargos (-)'（出账）对应的总笔数（Total Movimientos Cargos）。注意：通常不仅有金额，还有笔数列。\n(Step 2) 遍历 'Detalle de Movimientos Realizados'（交易明细）部分的所有交易行。\n(Step 3) [关键过滤] 仅统计 'Cargo' 列有有效数值（非空且不为0）的行。如果某行只有 'Abono' 列有值，必须忽略。\n(Step 4) 计算符合条件的交易总行数。",
            "Decision Result": "比较 Step 1 提取的笔数与 Step 4 计算的笔数。如果相等，输出一致；否则输出不一致。"
        },
        {
            "Rule ID": "MSTAR_BBVA_DTL_CNT_ABONOS",
            "Rule Name": "明细交易笔数校验_入账笔数",
            "Condition Logic": "(Step 1) 从 'Comportamiento' 表格中提取 'Depósitos / Abonos (+)'（入账）对应的总笔数（Total Movimientos Abonos）。\n(Step 2) 遍历 'Detalle de Movimientos Realizados'（交易明细）部分的所有交易行。\n(Step 3) [关键过滤] 仅统计 'Abono' 列有有效数值（非空且不为0）的行。如果某行只有 'Cargo' 列有值，必须忽略。\n(Step 4) 计算符合条件的交易总行数。",
            "Decision Result": "比较 Step 1 提取的笔数与 Step 4 计算的笔数。如果相等，输出一致；否则输出不一致。"
        },
        {
            "Rule ID": "MSTAR_BBVA_DTL_AMT_CARGOS",
            "Rule Name": "明细交易金额校验_出账总额",
            "Condition Logic": "(Step 1) 从 'Comportamiento' 表格中提取 'Retiros / Cargos (-)'（出账）对应的总金额。\n(Step 2) 遍历 'Detalle de Movimientos Realizados' 部分。\n(Step 3) [关键过滤] 累加所有 'Cargo' 列的数值。忽略 'Abono' 列的数值。\n(Step 4) 确保金额格式转换正确（处理千分位逗号）。",
            "Decision Result": "比较 Step 1 提取的总金额与 Step 3 计算的累加总和（允许 0.01 的误差）。如果相等，输出一致；否则输出不一致。"
        },
        {
            "Rule ID": "MSTAR_BBVA_DTL_AMT_ABONOS",
            "Rule Name": "明细交易金额校验_入账总额",
            "Condition Logic": "(Step 1) 从 'Comportamiento' (或 Summary/Resumen) 表格中提取 'Depósitos / Abonos (+)' 对应的总金额。\n(Step 2) 遍历 'Detalle de Movimientos Realizados' 部分的所有交易。\n(Step 3) [关键过滤] 仅累加 'Abono' 列的有效数值。忽略 'Cargo' 列和空值。\n(Step 4) 将累加值与 Step 1 的提取值进行比较（允许 0.01 误差）。",
            "Decision Result": "比较是否相等。如果相等，输出一致；否则输出不一致。"
        },
        {
            "Rule ID": "MSTAR_BBVA_DTL_AMT_SINGLE",
            "Rule Name": "明细交易金额校验_单笔金额 (Rolling Balance)",
            "Condition Logic": """(Step 1) 按原始顺序遍历列表。
(Step 2) 确定初始锚点(Balance_1/OPERACION1)：
   - 若第一笔交易 'Operacion' 不为空，取其值为 OPERACION1。
   - 若为空，取 'Summary (Comportamiento)' 中的 'Saldo Anterior' 为 OPERACION1。
(Step 3) 寻找下一个锚点(Balance_2/OPERACION2)：
   - 向下遍历，直到找到一下个 'Operacion' 不为空的行，记为 OPERACION2。
(Step 4) 区间计算(Result)：
   - 计算区间：(OPERACION1所在行 + 1) 到 (OPERACION2所在行)。注意：包括 OPERACION2 所在行，但不包括 OPERACION1 所在行。
   - 累加该区间内所有 'Cargo' (支出) 和 'Abono' (收入)。若为空则视为 0。
   - 验证公式：Result = OPERACION1 - Sum(Cargos) + Sum(Abonos) - OPERACION2。
   - 理论上 Result 应为 0 (允许 0.05 误差)。
(Step 5) 迭代：以 OPERACION2 为新的 OPERACION1，重复 Step 3-5 直到结束。""",
            "Decision Result": "若所有区间的 Result 均为 0 (或极小误差)，输出一致；否则输出不一致，并列出计算错误的区间详情。"
        },
        {
            "Rule ID": "MSTAR_BBVA_DTL_BAL_START",
            "Rule Name": "期初余额校验",
            "Condition Logic": "比较 'Resumen' 或 'Comportamiento' 表中的 'Saldo Inicial'（期初余额）与上一期（如有）的期末余额，或直接提取并显示值。",
            "Decision Result": "如果能找到对应值，输出一致；否则如果有矛盾，输出不一致。"
        },
        {
            "Rule ID": "MSTAR_BBVA_DTL_BAL_END",
            "Rule Name": "期末余额校验",
            "Condition Logic": "比较 'Resumen' 或 'Comportamiento' 表中的 'Saldo Final'（期末余额）与最后一笔交易的 'Saldo'（余额）列数值。",
            "Decision Result": "比较两者是否相等。如果相等，输出一致；否则输出不一致。"
        }
    ]

    df = pd.DataFrame(rules_data)
    
    # Ensure inputs directory exists
    os.makedirs('inputs', exist_ok=True)
    
    output_path = 'inputs/bbva_llm_rules_verification_optimized.xlsx'
    try:
        df.to_excel(output_path, index=False)
        print(f"Successfully generated optimized rules at: {output_path}")
        print("Done.")
    except Exception as e:
        print(f"Error generating excel: {e}")

if __name__ == "__main__":
    create_optimized_rules()
