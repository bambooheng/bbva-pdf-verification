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
        
        prompt_data_section = bank_statement_text
        
        # 构建详细的审核逻辑说明
        condition_logic = rule.get('condition_logic', '').strip()
        validation_rule = rule.get('validation_rule', '').strip()
        decision_result = rule.get('decision_result', '').strip()
        
        # 强调必须严格按照审核逻辑执行
        audit_logic_emphasis = ""
        if condition_logic or validation_rule:
            audit_logic_emphasis = f"""
## ⚠️ 重要：必须严格按照以下审核逻辑执行

**判断逻辑（必须严格执行）**：
{condition_logic if condition_logic else "（未提供）"}

**校验规则（必须严格执行）**：
{validation_rule if validation_rule else "（未提供）"}

**决策结果（必须严格执行）**：
{decision_result if decision_result else "（未提供）"}

**执行要求**：
- 必须严格按照上述"判断逻辑"中的步骤执行，不得跳过任何步骤
- 必须严格按照"校验规则"进行比较和判断
- 必须严格按照"决策结果"的逻辑输出结果
- 如果上述逻辑中有明确的步骤说明，必须逐条执行，不得自行简化或修改
"""
        
        prompt = f"""你是一个严格遵守审计规范的银行审计系统，必须准确、可追溯、零猜测地完成任务。

## 审计规则

规则ID: {rule['rule_id']}
规则名称: {rule['rule_name']}

{audit_logic_emphasis}

{hit_logic_explanation}

## 已提取的数据

- 下方内容已按原始文档的页面顺序和行顺序整理，请直接使用：
{prompt_data_section}

## 必须完成的任务

1. **严格按照"判断逻辑"执行**：必须按照上述"判断逻辑"中的步骤逐条执行，不得跳过或修改任何步骤。
2. **严格按照"校验规则"执行**：必须按照上述"校验规则"进行比较和判断，不得自行简化。
3. **严格按照"决策结果"执行**：必须按照上述"决策结果"的逻辑输出结果。
4. 仅依赖上述数据核对 Comportamiento 与 Detalle de Movimientos Realizados 的相关数值和交易。
5. 若为笔数校验：逐条列出所有 ABONOS/CARGOS 列不为空的交易，顺序必须与原文一致。
6. 若为金额校验：逐条列出所有相关交易金额，并展示完整求和过程。
7. "列不为空"指任意非零、非空数值（包括 0.01 等小额），不得遗漏。
8. 写清楚数值1（来自 Comportamiento）与数值2（来自 Detalle），说明比较结果，并依据决策规则推导输出。
9. 输出"一致"→ hit=False；输出"不一致"→ hit=True；若数据不足→ hit=null，并在 evidence 说明原因。
10. evidence 必须包含：数据来源、逐笔明细（按原始顺序）、计算过程、比较结论以及 hit 判定理由。
11. 禁止调整顺序或猜测；如信息缺失影响判断，必须写明并返回 hit=null。
12. **在evidence中必须明确说明：你是如何按照"判断逻辑"和"校验规则"执行的，每一步的执行结果是什么。**

## 输出格式（⚠️ 严格要求：只允许以下 JSON 格式）

**你必须严格按照以下格式输出，不要添加任何其他内容：**

{{
  "hit": true/false/null,
  "evidence": "...",
  "confidence": "high/medium/low",
  "notes": "..."
}}

**⚠️ 重要要求（必须严格遵守）：**
1. **只能输出JSON格式**：不能输出任何JSON以外的内容（无说明、无Markdown、无代码块标记、无```json```、无```等）。
2. **直接输出JSON对象**：直接输出 `{{"hit": ..., "evidence": ..., "confidence": ..., "notes": ...}}`，不要用代码块包裹。
3. **不要添加任何前缀或后缀**：不要在JSON前后添加任何文字说明、解释或标记。
4. **evidence字段**：可使用 `\\n` 表示换行，但禁止使用Markdown/HTML列表格式。
5. **hit值逻辑**：如果evidence表示"相等/一致/合规"，则hit必须为false；表示"不相等/不一致/违规"，则hit必须为true。
6. **数据不足处理**：若证据不足，请返回hit=null，并在evidence中写明原因。
7. **必须使用中文**：evidence和notes字段的内容必须全部使用中文输出，不得使用英文或其他语言。

**错误示例（禁止）：**
```
根据分析，结果如下：
```json
{{"hit": true, ...}}
```
```

**正确示例（必须）：**
```
{{"hit": true, "evidence": "...", "confidence": "high", "notes": ""}}
```

## 输出前自检

- 是否严格按照"判断逻辑"中的步骤执行？
- 是否严格按照"校验规则"进行比较和判断？
- 是否严格按照"决策结果"的逻辑输出结果？
- 是否列出全部相关交易且顺序与原文一致？
- 是否展示所有计算步骤与比较结果？
- hit 是否与 evidence 描述完全一致？
- 若无法判断，是否给出 hit=null 并说明原因？
- **是否在evidence中明确说明了如何按照"判断逻辑"和"校验规则"执行的？**

请现在开始分析并输出 JSON："""
        
        return prompt

