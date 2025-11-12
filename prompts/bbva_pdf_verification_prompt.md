## 任务目标

开发一个基于 Python 的自动化审计程序，接收已 OCR 解析并结构化的 BBVA 银行流水 JSON 数据，结合用户提供的 Excel 格式的“审计规则清单”，逐条执行合规性检查，并输出每条规则的审核结果及判断依据。

## 输入数据

### 1. `bank_statement.json`
包含经过 OCR 和结构化处理的银行流水数据，示例如下：

```
{
  "metadata": {
    "document_type": null,
    "bank": null,
    "account_number": "2960296619",
    "period": null,
    "total_pages": 9
  },
  "pages": [
    {
      "page_number": 1,
      "layout_elements": [
        {
          "type": "image",
          "content": {
            "index": 0,
            "xref": 5,
            "ext": "png",
            "width": 2550,
            "height": 3300
          },
          "bbox": {
            "x": 0.0,
            "y": 0.75,
            "width": 612.0,
            "height": 792.0,
            "page": 0
          },
          "confidence": 1.0,
          "semantic_type": "unknown",
          "raw_text": null,
          "font_size": null,
          "font_name": null,
          "font_flags": null,
          "color": null,
          "alignment": null,
          "line_spacing": null,
          "char_spacing": null,
          "lines": null
        }
      ],
      "page_width": 612.0,
      "page_height": 792.0
    },
    {
      
    }
  },
  "validation_metrics": {
    "extraction_completeness": 98.7603305785124,
    "position_accuracy": 0.0,
    "content_accuracy": 95.5,
    "discrepancy_report": [
      {
        "type": "pixel_difference",
        "location": null,
        "original_value": null,
        "extracted_value": null,
        "severity": "high",
        "description": "Page 1 has 22.68% pixel differences"
      },
      {
        "type": "pixel_difference",
        "location": null,
        "original_value": null,
        "extracted_value": null,
        "severity": "high",
        "description": "Page 2 has 18.60% pixel differences"
      },
      {
        "type": "pixel_difference",
        "location": null,
        "original_value": null,
        "extracted_value": null,
        "severity": "high",
        "description": "Page 3 has 13.30% pixel differences"
      },
      {
        "type": "pixel_difference",
        "location": null,
        "original_value": null,
        "extracted_value": null,
        "severity": "high",
        "description": "Page 4 has 12.88% pixel differences"
      },
      {
        "type": "pixel_difference",
        "location": null,
        "original_value": null,
        "extracted_value": null,
        "severity": "medium",
        "description": "Page 5 has 3.54% pixel differences"
      },
      {
        "type": "pixel_difference",
        "location": null,
        "original_value": null,
        "extracted_value": null,
        "severity": "high",
        "description": "Page 6 has 10.11% pixel differences"
      },
      {
        "type": "pixel_difference",
        "location": null,
        "original_value": null,
        "extracted_value": null,
        "severity": "high",
        "description": "Page 7 has 14.46% pixel differences"
      },
      {
        "type": "pixel_difference",
        "location": null,
        "original_value": null,
        "extracted_value": null,
        "severity": "high",
        "description": "Page 8 has 11.23% pixel differences"
      },
      {
        "type": "pixel_difference",
        "location": null,
        "original_value": null,
        "extracted_value": null,
        "severity": "high",
        "description": "Page 9 has 13.61% pixel differences"
      }
    ]
  }
}
```

### 2. audit_rules.xlsx
Excel 文件，字段说明如下：

| 字段名 |	说明   |
|-------- |------|
| Rule ID |	规则唯一标识符（如 MSTAR_BBVA_DTL_CNT_ABONOS）   |
| Rule Name |	规则名称（如“明细交易笔数校验_入账笔数”）   |
| Condition Logic |	判断逻辑（如1.1、取 Comportamiento 中 Depósitos / Abonos (+) 的笔数；2.Detalle de Movimientos Realizados部分：取交易明细 ABONOS 列的所有交易笔数计数求和）   |
| 校验规则 |	比较1和2是否相等   |
| 决策结果 |  如果相等，输出一致（无异常）；如果不相等，输出不一致（异常）   |

## 输出要求

生成一份详细的审计报告，支持 JSON 和 Markdown 格式。每条规则需包含以下信息：
| 字段名 |	说明   |
|-------- |------|
| Rule ID |	规则ID   |
| Rule Name |	规则名称|
| hit	| 是否命中：如果相等，输出"无异常";如果不等，输出"异常";其他输出"无法判断"
| evidence	| 判断依据（引用具体交易或说明原因）
| confidence	| 置信度：high / medium / low
| notes	| 补充说明（可选）

### 示例输出片段（JSON）
{
  "rule_id": "MSTAR_BBVA_DTL_CNT_ABONOS）",
  "rule_name": "明细交易笔数校验_入账笔数",
  "hit": 无异常,
  "evidence": "1.Comportamiento 中 Depósitos / Abonos (+) 的笔数为5；2.交易明细 ABONOS 列不为空的为5;二者相等",
  "confidence": "high"
}

## 功能需求
  - **文件读取**：支持加载 JSON 流水和 Excel 审计规则；
  - **规则解析**：将 Excel 中的规则转换为内部可执行对象；
  - **智能判断**：调用大模型（DeepSeek / OpenAI / Authorpic）进行语义级匹配与推理；
  - **全覆盖审计**：确保所有规则都被执行，不允许遗漏；
  - **不确定处理**：若信息不足导致无法判断，返回 hit: null 并注明原因；
  - **日志记录**：记录关键流程、LLM 请求/响应、异常信息；
  - **错误处理**：对文件缺失、格式错误等情况有容错机制；
  - **结果导出**：支持导出为 JSON 和 Markdown 报告。

## 技术栈与工具
  - **语言**：Python 3.10+
  - **核心库**：
      pandas：读取 Excel
      openpyxl：操作 Excel 文件
      json, os, logging：标准库
      requests：调用大模型 API
      tenacity：API 调用重试机制
  - **大模型支持**：
      OpenAI (gpt-4-turbo)
      DeepSeek (deepseek-chat)
      Authorpic（自定义模型）
  - **安全配置**：通过 .env 文件管理 API Key，禁止硬编码

## 模块化项目结构
```
  bbva-audit-system/
  │
  ├── main.py                     # 主入口
  ├── config/
  │   └── settings.env            # 存放 API keys 和路径配置
  ├── src/
  │   ├── data_loader.py          # 加载 JSON 和 Excel
  │   ├── rule_parser.py          # 解析审计规则
  │   ├── llm_judge.py            # 调用大模型判断是否命中
  │   ├── audit_engine.py         # 控制整体审计流程
  │   └── report_generator.py     # 生成最终报告
  ├── inputs/
  │   ├── bank_statement.json     # 示例流水
  │   └── audit_rules.xlsx        # 示例规则表
  ├── outputs/
  │   └── audit_report.md         # 输出报告
  ├── logs/
  │   └── app.log                 # 日志文件
  ├── requirements.txt            # 依赖包
  └── README.md                   # 使用说明
```
## 安全建议：.env 示例
  - **OPENAI_API_KEY**=sk-xxxxxx
  - **DEEPSEEK_API_KEY**=ds-xxxxxx
  - **AUTHORPIC_API_KEY**=ap-xxxxxx
  - **LLM_PROVIDER**=openai
  - **INPUT_JSON_PATH**=inputs/bank_statement.json
  - **RULES_XLSX_PATH**=inputs/audit_rules.xlsx
  - **OUTPUT_REPORT_PATH**=outputs/audit_report.json

## 设计原则
  - **模块化**：各功能独立封装，便于维护与测试
  - **可配置化**：路径、模型、参数均可外部配置
  - **可追溯性**：保留 LLM 的 prompt 与 response 快照，用于审计回溯
  - **扩展性强**：未来可接入其他银行、国际反洗钱标准（如 FATF）
  - **零猜测原则**：绝不凭空推断结果，信息不足必须标记为“无法判断”

## 附加要求
  - **所有判断必须提供明确证据**
  - **不允许跳过任何一条规则**
  - **若某条规则因数据缺失无法评估，必须标注原因**
  - **支持多轮迭代优化，可通过日志分析改进规则表达**
