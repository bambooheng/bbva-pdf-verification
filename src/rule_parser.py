"""
规则解析模块：将 Excel 中的规则转换为可执行对象
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class RuleParser:
    """规则解析器"""
    
    def __init__(self):
        """初始化规则解析器"""
        pass
    
    def parse_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析单条规则
        
        Args:
            rule: 原始规则字典
            
        Returns:
            解析后的规则字典
        """
        parsed_rule = {
            'rule_id': rule.get('rule_id'),
            'rule_name': rule.get('rule_name'),
            'condition_logic': rule.get('condition_logic', ''),
            'validation_rule': rule.get('validation_rule', ''),
            'decision_result': rule.get('decision_result', ''),
            'row_index': rule.get('row_index'),
            'original_rule': rule  # 保留原始规则用于调试
        }
        
        logger.debug(f"解析规则: {parsed_rule['rule_id']} - {parsed_rule['rule_name']}")
        return parsed_rule
    
    def parse_all_rules(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        解析所有规则
        
        Args:
            rules: 原始规则列表
            
        Returns:
            解析后的规则列表
        """
        parsed_rules = []
        
        for rule in rules:
            try:
                parsed_rule = self.parse_rule(rule)
                parsed_rules.append(parsed_rule)
            except Exception as e:
                logger.error(f"解析规则失败 {rule.get('rule_id', 'N/A')}: {e}")
                # 即使解析失败，也保留规则以便后续处理
                parsed_rules.append(rule)
        
        logger.info(f"成功解析 {len(parsed_rules)} 条规则")
        return parsed_rules
    
    def build_llm_prompt(self, rule: Dict[str, Any], bank_statement_text: str) -> str:
        """
        构建发送给 LLM 的提示词
        
        Args:
            rule: 解析后的规则
            bank_statement_text: 银行流水的文本内容
            
        Returns:
            格式化的提示词
        """
        # 解析决策结果，明确 hit 值的判断逻辑
        decision_result = rule.get('decision_result', '')
        hit_logic_explanation = ""
        
        if "如果相等，输出一致" in decision_result or "如果相等" in decision_result:
            hit_logic_explanation = """
**hit 值判断逻辑（非常重要！）**：
- 如果两个数值**相等** → 根据决策结果输出"一致" → **hit=False**（合规/未命中）
- 如果两个数值**不相等** → 根据决策结果输出"不一致" → **hit=True**（违规/命中）

**关键理解**：
- "一致" = 数据匹配 = 合规 = hit=False
- "不一致" = 数据不匹配 = 违规 = hit=True
"""
        elif "如果不相等，输出不一致" in decision_result or "如果不相等" in decision_result:
            hit_logic_explanation = """
**hit 值判断逻辑（非常重要！）**：
- 如果两个数值**不相等** → 根据决策结果输出"不一致" → **hit=True**（违规/命中）
- 如果两个数值**相等** → 根据决策结果输出"一致" → **hit=False**（合规/未命中）

**关键理解**：
- "不一致" = 数据不匹配 = 违规 = hit=True
- "一致" = 数据匹配 = 合规 = hit=False
"""
        else:
            hit_logic_explanation = """
**hit 值判断逻辑（非常重要！）**：
- hit=True 表示规则被命中（违规/不一致）
- hit=False 表示规则未命中（合规/一致）
- 请根据"决策结果"字段的逻辑来判断
"""
        
        prompt = f"""你是一个专业的银行审计系统。请根据以下审计规则和银行流水数据，判断规则是否被命中。

## 审计规则

**规则ID**: {rule['rule_id']}
**规则名称**: {rule['rule_name']}
**判断逻辑**: {rule['condition_logic']}
**校验规则**: {rule['validation_rule']}
**预期决策结果**: {rule['decision_result']}

{hit_logic_explanation}

## 银行流水数据

{bank_statement_text}

## 任务要求

1. **仔细分析银行流水数据**，提取与规则相关的所有信息
2. **必须列出所有明细数据**：
   - 对于涉及交易笔数的规则：必须逐一列出每笔符合条件的交易（包括日期、描述、金额等）
     * **⚠️ 关键：必须严格按照原始文档中的顺序列出交易，不能改变顺序**
     * **⚠️ 关键：必须按照页面顺序（从第1页到最后一页）和行顺序（从上到下）来列出交易**
     * **⚠️ 关键：第一条交易应该是原始文档中第一条符合条件的交易（按照页面和行顺序）**
     * **⚠️ 禁止：不能按照日期排序、金额排序或其他任何排序方式，必须严格按照原始文档中的出现顺序**
   - 对于涉及交易金额的规则：必须列出每笔交易的明细，并显示计算过程
     * **⚠️ 关键：必须严格按照原始文档中的顺序列出交易，不能改变顺序**
     * **⚠️ 关键：必须按照页面顺序（从第1页到最后一页）和行顺序（从上到下）来列出交易**
   - 从"Comportamiento"部分提取的数据，需要明确标注来源
   - 从"Detalle de Movimientos Realizados"部分提取的数据，需要逐条列出
     * **⚠️ 关键：必须严格按照原始文档中的顺序列出，不能使用示例中的顺序**
     * **⚠️ 关键：必须按照页面顺序和行顺序，第一条交易应该是原始文档中第一条符合条件的交易**
   - **⚠️ 重要：关于"不为空"的定义**：
     * 对于 ABONOS/CARGOS 列"不为空"的判断标准：
       - "不为空" = 列中有数值（包括 0.01、0.1、1.00 等任何非零值）
       - "不为空" = 列中有值且不为 null、不为空字符串、不为 0
       - **即使金额很小（如 0.01），只要 ABONOS/CARGOS 列有数值，就必须统计**
       - **必须逐条检查所有交易，不能因为金额小就忽略**
     * 示例：如果 ABONOS 列值为 0.01，这笔交易**必须**被统计
     * 示例：如果 ABONOS 列值为空、null、0 或不存在，则**不**统计
3. **根据"判断逻辑"和"校验规则"执行检查**：
   - **⚠️ 关键：对于"ABONOS列取值不为空"的理解**：
     * "不为空" = 列中有任何数值（包括 0.01、0.1、0.5、1.00 等）
     * "不为空" ≠ 金额大小，只要列中有数值就必须统计
     * **必须逐行检查 Detalle de Movimientos Realizados 部分的每一笔交易**
     * **不能因为金额小（如 0.01）就忽略，这是错误的**
     * **示例说明：如果某笔交易的 ABONOS 列值为 0.01（或任何非零值），这笔交易必须被统计**
   - **⚠️ 关键：对于"CARGOS列取值不为空"的理解**：
     * 同样，只要 CARGOS 列有数值（无论大小），就必须统计
     * 必须逐行检查，不能遗漏任何一笔
4. **关键步骤（必须按顺序执行，每一步都要仔细）**：
   **步骤1**：比较两个数值是否相等
     - 明确写出：数值1 = X，数值2 = Y
     - 明确判断：相等 或 不相等
   
   **步骤2**：根据比较结果（相等/不相等）和"决策结果"确定输出（一致/不一致）
     - 如果比较结果 = "相等"：
       * 查看"决策结果"："如果相等，输出一致"
       * 因此输出 = "一致"
     - 如果比较结果 = "不相等"：
       * 查看"决策结果"："如果不相等，输出不一致"
       * 因此输出 = "不一致"
   
   **步骤3**：根据输出确定 hit 值（这是关键步骤，必须严格遵守）：
     - 如果输出 = "一致" → **hit = False**（合规/未命中）
     - 如果输出 = "不一致" → **hit = True**（违规/命中）
     - **⚠️ 重要：hit 值必须与输出完全对应，不能矛盾**
     - **⚠️ 绝对禁止：不能因为数据提取完整性、内容准确性或其他原因而改变 hit 值**
     - **⚠️ 绝对禁止：不能说"两者相等"但 hit=True，或说"两者不相等"但 hit=False**
     - **⚠️ 如果数据有问题，在 notes 中说明，但 hit 值必须严格按照步骤1-3的逻辑确定**
   
   **步骤4**：在 evidence 中明确说明（必须包含以下所有内容）：
     - 数值1（来自 Comportamiento）：X
     - 数值2（来自 Detalle de Movimientos Realizados）：Y
     - 比较结果：相等/不相等
     - 根据决策结果得出的结论：一致/不一致
     - 对应的 hit 值：False/True
     - **⚠️ 最后验证：evidence 中的结论必须与 hit 值一致**
       * 如果 evidence 说"相等"或"一致"，hit 必须是 False
       * 如果 evidence 说"不相等"或"不一致"，hit 必须是 True
5. **在判断依据（evidence）中必须包含**：
   - 从"Comportamiento"部分提取的具体数值（明确标注来源）
   - 从"Detalle de Movimientos Realizados"部分提取的每笔交易明细（逐条列出）
     * **⚠️ 关键：必须严格按照原始文档中的顺序列出交易，不能改变顺序**
     * **⚠️ 关键：必须按照页面顺序（从第1页到最后一页）和行顺序（从上到下）来列出交易**
     * **⚠️ 关键：必须按照实际数据中出现的顺序，第一条交易应该是原始文档中的第一条符合条件的交易（按照页面和行顺序）**
     * **⚠️ 禁止：不能使用示例中的顺序，必须严格按照实际数据顺序**
     * **⚠️ 禁止：不能按照日期排序、金额排序或其他任何排序方式，必须严格按照原始文档中的出现顺序**
   - 计算过程（如果涉及金额求和或笔数统计）
   - **最终比较结果**：明确说明"相等"或"不相等"
   - **根据决策结果的结论**：明确说明"一致"或"不一致"
   - **hit 值说明**：明确说明为什么 hit=False 或 hit=True
   - **⚠️ 验证清单**：在 evidence 最后，请确认：
     * 是否检查了所有交易行？
     * 是否包含了所有 ABONOS/CARGOS 列有值的交易（包括 0.01、0.1 等小额）？
     * 统计的笔数是否与 Comportamiento 部分一致？
   - **⚠️ 关键：evidence 中的结论必须与 hit 值完全一致**：
     * 如果 evidence 中说"相等"或"一致"，hit 必须是 False
     * 如果 evidence 中说"不相等"或"不一致"，hit 必须是 True
     * **不能出现矛盾：不能说"相等"但 hit=True，或说"不相等"但 hit=False**
6. 评估置信度（confidence）：high / medium / low

## 输出格式要求

请以 JSON 格式输出结果，格式如下：
{{
    "hit": true/false/null,
    "evidence": "判断依据的详细说明（必须包含明细数据）",
    "confidence": "high/medium/low",
    "notes": "补充说明（可选）"
}}

**⚠️ 关键验证步骤（在输出 JSON 之前必须执行）**：
1. **检查 evidence 中的结论**：
   - 如果 evidence 中说"相等"或"一致"或"合规"或"未命中" → hit 必须是 **false**
   - 如果 evidence 中说"不相等"或"不一致"或"违规"或"命中" → hit 必须是 **true**
2. **验证一致性**：
   - 如果 evidence 中说"对应的 hit 值：False"，JSON 中的 hit 必须是 false
   - 如果 evidence 中说"对应的 hit 值：True"，JSON 中的 hit 必须是 true
   - **绝对禁止**：evidence 中说 hit=False，但 JSON 中 hit=True（这是严重错误！）
   - **绝对禁止**：evidence 中说 hit=True，但 JSON 中 hit=False（这是严重错误！）
3. **最终检查**：
   - 在输出 JSON 之前，请再次确认：evidence 中的结论与 JSON 中的 hit 值是否完全一致？
   - 如果不一致，请修正 JSON 中的 hit 值，使其与 evidence 中的结论一致

**重要**：JSON 中的 hit 值必须与 evidence 中的结论完全一致！
- 如果 evidence 中说"一致"或"合规"或"未命中"，hit 必须是 false
- 如果 evidence 中说"不一致"或"违规"或"命中"，hit 必须是 true

## 重要要求

1. **所有判断必须提供明确证据**：不能只给出结论，必须列出支持结论的所有数据
2. **必须列出明细**：
   - 如果是笔数校验，必须列出所有符合条件的交易明细（如：日期、描述、ABONOS/CARGOS列的值）
     * **⚠️ 关键：必须统计所有 ABONOS/CARGOS 列不为空的交易，包括金额为 0.01、0.1 等小额交易**
     * **不能因为金额小就忽略，必须逐条检查每一笔交易**
   - 如果是金额校验，必须列出每笔交易的金额明细，并显示求和过程
     * **⚠️ 关键：必须包含所有 ABONOS/CARGOS 列有值的交易金额，无论金额大小**
3. **数据来源必须明确**：明确指出数据来自"Comportamiento"还是"Detalle de Movimientos Realizados"
4. **零猜测原则**：绝不凭空推断结果，信息不足必须标记为 null
5. **不允许跳过任何数据**：必须检查所有相关数据，不能遗漏
6. **⚠️ 最关键：hit 值的判断逻辑（必须严格遵守）**：
   - **仔细阅读"决策结果"字段**："{rule['decision_result']}"
   - **对于当前规则**：
     * 如果"决策结果"包含"如果相等，输出一致"：
       - 比较结果 = "相等" → 输出 = "一致" → **hit = False**（合规/未命中）
       - 比较结果 = "不相等" → 输出 = "不一致" → **hit = True**（违规/命中）
     * 如果"决策结果"包含"如果不相等，输出不一致"：
       - 比较结果 = "不相等" → 输出 = "不一致" → **hit = True**（违规/命中）
       - 比较结果 = "相等" → 输出 = "一致" → **hit = False**（合规/未命中）
   - **⚠️ 重要提醒**：
     * "一致" = 数据匹配 = 合规 = **hit=False**
     * "不一致" = 数据不匹配 = 违规 = **hit=True**
     * **JSON 中的 hit 值必须与 evidence 中的结论完全一致！**
     * 如果 evidence 中说"一致"，hit 必须是 False
     * 如果 evidence 中说"不一致"，hit 必须是 True

## 示例格式（evidence 应该包含）

对于笔数校验：
- Comportamiento 部分：Depósitos / Abonos (+) 显示 X 笔
- Detalle de Movimientos Realizados 部分：逐条列出所有 ABONOS 列不为空的交易
  **⚠️ 重要：必须统计所有 ABONOS 列有值的交易，包括金额为 0.01、0.1 等小额交易**
  **⚠️ 不能遗漏任何一笔，必须逐条检查每一行交易记录**
  **⚠️ 关键：必须严格按照原始文档中的顺序列出交易，第一条交易应该是原始文档中第一条符合条件的交易**
  **⚠️ 关键：必须按照页面顺序（从第1页到最后一页）和行顺序（从上到下）来列出交易**
  **⚠️ 禁止：不能使用示例中的顺序，必须严格按照实际数据顺序**
  **⚠️ 禁止：不能按照日期排序、金额排序或其他任何排序方式，必须严格按照原始文档中的出现顺序**
  1. 日期: XX/XX, 描述: XXX, ABONOS: XXX（按照原始文档顺序，即使金额很小如 0.01 也要列出）
  2. 日期: XX/XX, 描述: XXX, ABONOS: XXX（按照原始文档顺序）
  ...
  总计: X 笔（必须与 Comportamiento 部分的笔数一致）
- 比较结果：两者是否相等

对于金额校验：
- Comportamiento 部分：Depósitos / Abonos (+) 显示总金额: XXX
- Detalle de Movimientos Realizados 部分：逐条列出所有 ABONOS 列的交易金额
  **⚠️ 关键：必须严格按照原始文档中的顺序列出交易，第一条交易应该是原始文档中第一条符合条件的交易**
  **⚠️ 关键：必须按照页面顺序（从第1页到最后一页）和行顺序（从上到下）来列出交易**
  **⚠️ 禁止：不能使用示例中的顺序，必须严格按照实际数据顺序**
  **⚠️ 禁止：不能按照日期排序、金额排序或其他任何排序方式，必须严格按照原始文档中的出现顺序**
  1. 日期: XX/XX, 描述: XXX, ABONOS: XXX（按照原始文档顺序）
  2. 日期: XX/XX, 描述: XXX, ABONOS: XXX（按照原始文档顺序）
  ...
  求和: XXX + XXX + ... = XXX
- 比较结果：两者是否相等

请开始分析："""
        
        return prompt

