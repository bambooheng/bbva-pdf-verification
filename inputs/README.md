# 输入文件说明

本目录用于存放审计系统所需的输入文件。

## 必需文件

### 1. bank_statement.json

银行流水 JSON 文件，包含经过 OCR 和结构化处理的银行流水数据。

**文件结构要求**：
- 必须包含 `metadata` 字段（至少包含 `account_number`）
- 必须包含 `pages` 数组
- 可选：`validation_metrics` 字段

**示例位置**：`bank_statement.json.example`

### 2. audit_rules.xlsx

Excel 格式的审计规则清单。

**必需列**：
- `Rule ID`: 规则唯一标识符（如 MSTAR_RULE_BBVA_001）
- `Rule Name`: 规则名称（如"交易笔数校验_入账笔数"）
- `Condition Logic`: 判断逻辑（详细的检查步骤说明）
- `校验规则`: 比较规则（如"比较1和2是否相等"）
- `决策结果`: 预期结果（如"如果相等，输出一致；如果不相等，输出不一致"）

**示例格式**：

| Rule ID | Rule Name | Condition Logic | 校验规则 | 决策结果 |
|---------|-----------|----------------|---------|---------|
| MSTAR_RULE_BBVA_001 | 交易笔数校验_入账笔数 | 1.取Comportamiento中Depósitos / Abonos (+)所在行的第一个数为笔数；2.Detalle de Movimientos Realizados部分：交易明细ABONOS列取值不为空的交易总笔数； | 比较1和2是否相等 | 如果相等，输出一致；如果不相等，输出不一致； |

## 注意事项

- 请确保文件名与 `config/settings.env` 中配置的路径一致
- Excel 文件的第一行必须是表头
- Rule ID 和 Rule Name 不能为空，否则该规则会被跳过
- 建议使用 UTF-8 编码保存 Excel 文件以避免中文乱码



