# 快速开始指南

## 5 分钟快速上手

### 步骤 1: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 2: 配置 API Key

```bash
# Windows PowerShell
Copy-Item config\settings.env.example config\settings.env

# Linux/Mac
cp config/settings.env.example config/settings.env
```

然后编辑 `config/settings.env`，填入你的 API Key：

```env
OPENAI_API_KEY=sk-your-key-here
LLM_PROVIDER=openai
```

### 步骤 3: 准备输入文件

1. 将银行流水 JSON 文件放到 `inputs/bank_statement.json`
2. 将审计规则 Excel 文件放到 `inputs/audit_rules.xlsx`

**Excel 文件必须包含以下列**：
- Rule ID
- Rule Name
- Condition Logic
- 校验规则
- 决策结果

### 步骤 4: 运行审计

```bash
python main.py
```

### 步骤 5: 查看结果

- JSON 报告：`outputs/audit_report.json`
- Markdown 报告：`outputs/audit_report.md`
- 日志文件：`logs/app.log`

## 常见问题

### Q: 提示"未配置 API Key"？

A: 检查 `config/settings.env` 文件是否存在，并且 API Key 已正确填写（不是示例值）。

### Q: 提示"文件未找到"？

A: 确保 `inputs/` 目录下存在：
- `bank_statement.json`
- `audit_rules.xlsx`

### Q: Excel 文件读取失败？

A: 确保 Excel 文件包含所有必需的列，并且使用 `.xlsx` 格式（不是 `.xls`）。

### Q: LLM API 调用失败？

A: 
1. 检查网络连接
2. 验证 API Key 是否有效
3. 查看 `logs/app.log` 获取详细错误信息

## 支持的 LLM 提供商

### OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxx
OPENAI_MODEL=gpt-4-turbo
```

### DeepSeek

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=ds-xxxxxx
DEEPSEEK_MODEL=deepseek-chat
```

### Authorpic

```env
LLM_PROVIDER=authorpic
AUTHORPIC_API_KEY=ap-xxxxxx
AUTHORPIC_MODEL=authorpic-model
```

**注意**：Authorpic 的 API 端点可能需要根据实际文档进行调整（编辑 `src/llm_judge.py` 中的 `_call_authorpic` 方法）。

## 下一步

- 查看 `README.md` 了解详细功能
- 查看 `inputs/README.md` 了解输入文件格式要求
- 查看 `logs/app.log` 了解系统运行详情



