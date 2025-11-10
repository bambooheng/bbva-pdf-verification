# BBVA 银行流水审计系统

基于 Python 的自动化审计程序，接收已 OCR 解析并结构化的 BBVA 银行流水 JSON 数据，结合用户提供的 Excel 格式的"审计规则清单"，逐条执行合规性检查，并输出每条规则的审核结果及判断依据。

## 功能特性

- ✅ **文件读取**：支持加载 JSON 流水和 Excel 审计规则
- ✅ **规则解析**：将 Excel 中的规则转换为内部可执行对象
- ✅ **智能判断**：调用大模型（DeepSeek / OpenAI / Authorpic）进行语义级匹配与推理
- ✅ **全覆盖审计**：确保所有规则都被执行，不允许遗漏
- ✅ **不确定处理**：若信息不足导致无法判断，返回 hit: null 并注明原因
- ✅ **日志记录**：记录关键流程、LLM 请求/响应、异常信息
- ✅ **错误处理**：对文件缺失、格式错误等情况有容错机制
- ✅ **结果导出**：支持导出为 JSON 和 Markdown 报告

## 项目结构

```
bbva-pdf-verification/
│
├── main.py                     # 主入口
├── config/
│   └── settings.env.example    # 配置文件示例
├── src/
│   ├── __init__.py
│   ├── config.py               # 配置管理
│   ├── data_loader.py          # 加载 JSON 和 Excel
│   ├── rule_parser.py          # 解析审计规则
│   ├── llm_judge.py            # 调用大模型判断是否命中
│   ├── audit_engine.py         # 控制整体审计流程
│   └── report_generator.py     # 生成最终报告
├── inputs/
│   ├── bank_statement.json     # 示例流水（需用户提供）
│   └── audit_rules.xlsx        # 示例规则表（需用户提供）
├── outputs/
│   ├── audit_report.json       # JSON 格式报告
│   └── audit_report.md         # Markdown 格式报告
├── logs/
│   └── app.log                 # 日志文件
├── requirements.txt            # 依赖包
└── README.md                   # 使用说明
```

## 安装步骤

1. **克隆或下载项目**

```bash
cd bbva-pdf-verification
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **配置环境变量**

复制配置文件模板并填入真实的 API Key：

```bash
cp config/settings.env.example config/settings.env
```

编辑 `config/settings.env`，填入以下信息：

```env
# API Keys
OPENAI_API_KEY=sk-your-openai-key-here
DEEPSEEK_API_KEY=ds-your-deepseek-key-here
AUTHORPIC_API_KEY=ap-your-authorpic-key-here

# LLM Provider 选择: openai, deepseek, authorpic
LLM_PROVIDER=openai

# 文件路径配置（根据需要修改）
INPUT_JSON_PATH=inputs/bank_statement.json
RULES_XLSX_PATH=inputs/audit_rules.xlsx
OUTPUT_REPORT_PATH=outputs/audit_report.json
OUTPUT_MARKDOWN_PATH=outputs/audit_report.md
```

## 使用方法

1. **准备输入文件**

   - 将银行流水 JSON 文件放置在 `inputs/bank_statement.json`
   - 将审计规则 Excel 文件放置在 `inputs/audit_rules.xlsx`

2. **Excel 规则表格式**

   Excel 文件必须包含以下列：

   | 字段名 | 说明 |
   |--------|------|
   | Rule ID | 规则唯一标识符（如 MSTAR_RULE_BBVA_001） |
   | Rule Name | 规则名称（如"交易笔数校验_入账笔数"） |
   | Condition Logic | 判断逻辑（详细的检查步骤说明） |
   | 校验规则 | 比较规则（如"比较1和2是否相等"） |
   | 决策结果 | 预期结果（如"如果相等，输出一致；如果不相等，输出不一致"） |

3. **运行审计程序**

```bash
python main.py
```

4. **查看结果**

   - JSON 报告：`outputs/audit_report.json`
   - Markdown 报告：`outputs/audit_report.md`
   - 日志文件：`logs/app.log`

## 输出格式

每条规则的审计结果包含以下字段：

| 字段名 | 说明 | 示例值 |
|--------|------|--------|
| Rule ID | 规则ID | MSTAR_RULE_BBVA_001 |
| Rule Name | 规则名称 | 交易笔数校验_入账笔数 |
| hit | 是否命中 | true / false / null |
| evidence | 判断依据 | "1金额为5000，2金额为10000，不相等" |
| confidence | 置信度 | high / medium / low |
| notes | 补充说明 | （可选） |

### JSON 报告示例

```json
{
  "metadata": {
    "generated_at": "2024-01-01T12:00:00",
    "total_rules": 10
  },
  "summary": {
    "total_rules": 10,
    "hit_count": 2,
    "not_hit_count": 7,
    "unknown_count": 1
  },
  "results": [
    {
      "rule_id": "MSTAR_RULE_BBVA_001",
      "rule_name": "交易笔数校验_入账笔数",
      "hit": true,
      "evidence": "1金额为5000，2金额为10000，不相等",
      "confidence": "high"
    }
  ]
}
```

## 支持的 LLM 提供商

- **OpenAI**: GPT-4 Turbo, GPT-3.5 Turbo 等
- **DeepSeek**: DeepSeek Chat 模型
- **Authorpic**: 自定义模型（需根据实际 API 文档调整）

## 设计原则

- **模块化**：各功能独立封装，便于维护与测试
- **可配置化**：路径、模型、参数均可外部配置
- **可追溯性**：保留 LLM 的 prompt 与 response 快照，用于审计回溯
- **扩展性强**：未来可接入其他银行、国际反洗钱标准（如 FATF）
- **零猜测原则**：绝不凭空推断结果，信息不足必须标记为"无法判断"

## 注意事项

- ⚠️ **所有判断必须提供明确证据**
- ⚠️ **不允许跳过任何一条规则**
- ⚠️ **若某条规则因数据缺失无法评估，必须标注原因**
- ⚠️ **确保 API Key 安全，不要将 settings.env 提交到版本控制系统**

## 故障排除

### 问题：API Key 未配置

**解决方案**：检查 `config/settings.env` 文件是否存在，并确保 API Key 已正确填写。

### 问题：文件未找到

**解决方案**：检查 `inputs/` 目录下是否存在 `bank_statement.json` 和 `audit_rules.xlsx` 文件。

### 问题：Excel 格式错误

**解决方案**：确保 Excel 文件包含所有必需的列：Rule ID, Rule Name, Condition Logic, 校验规则, 决策结果。

### 问题：LLM API 调用失败

**解决方案**：
- 检查网络连接
- 验证 API Key 是否有效
- 查看 `logs/app.log` 获取详细错误信息
- 系统会自动重试最多 3 次

## 许可证

本项目仅供内部使用。

## 联系方式

如有问题或建议，请联系开发团队。



