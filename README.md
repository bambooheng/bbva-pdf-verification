# BBVA 银行流水审计系统 (BBVA Audit Engine)

基于 Python 的自动化审计程序，接收已 OCR 解析并结构化的 BBVA 银行流水 JSON 数据，结合用户提供的 Excel 格式的"审计规则清单"，逐条执行合规性检查，并输出每条规则的审核结果及判断依据。

## 📖 文档导航

- **快速部署**：查看 [QUICK_START.md](QUICK_START.md)（5分钟快速上手）
- **详细部署文档**：查看 [DEPLOYMENT.md](DEPLOYMENT.md)（完整部署指南）
- **项目说明**：本文档

## ✨ 核心特性

- **🚀 零代码规则适配**：完全由 Excel 定义规则逻辑，支持 Rolling Balance、跨表数据比对、时间序列分析等复杂场景。
- **🧠 智能 LLM 判决**：内置 DeepSeek / OpenAI / Authorpic 多模型支持，具备“最后匹配原则”智能修正机制，精准识别 LLM 的自然语言结论。
- **🔍 深度数据挖掘**：
    - **通用数据加载**：自动识别 JSON 中的任意 Section 数据，无需硬编码白名单。
    - **高精度余额提取**：自动区分 `Saldo Operación` (账面余额) 与 `Saldo Liquidación` (起息日余额)，确保算术逻辑严谨。
    - **严谨的 Rolling Balance**：针对滚动余额校验规则，强制执行“逐行计算、绝不省略”策略。
- **🛡️ 健壮性设计**：
    - **自动容错**：自动处理缺失字段、格式错误的日期/金额。
    - **结果自修正**：自动检测 LLM 文本结论与 JSON 字段的不一致并进行修正。
    - **全覆盖审计**：确保所有规则都被执行，不允许遗漏。

## 📂 项目结构

```
bbva-pdf-verification/
│
├── main.py                     # 🚀 启动入口
├── config/
│   └── settings.env.example    # 配置文件模板
├── src/                        # 🧠 核心源码
│   ├── data_loader.py          # 通用数据加载 (支持任意 Section)
│   ├── rule_parser.py          # 规则解析 & Prompt 构建 (含强制 Rolling Logic)
│   ├── llm_judge.py            # LLM 判决引擎 (含自修正机制)
│   ├── audit_engine.py         # 流程编排
│   └── report_generator.py     # 报告生成 (Excel/JSON/Markdown)
├── inputs/                     # 📥 输入目录
│   ├── *.json                  # 银行流水数据 (支持通配符自动加载最新文件)
│   └── *.xlsx                  # 审计规则表
├── outputs/                    # 📤 输出目录
│   └── *_audit_report.xlsx     # 最终 Excel 审计报告
├── logs/                       # 📝 日志目录
│   └── app.log                 # 详细运行日志
└── requirements.txt            # 依赖清单
```

## 🛠️ 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

复制 `config/settings.env.example` 为 `config/settings.env`，并填入 API Key：

```ini
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxxxxxx
# 可选: INPUT_JSON_PATH=inputs/*.json (自动处理 inputs 目录下最新的 json)
```

### 3. 运行审计

```bash
python main.py
```

### 4. 查看报告

运行完成后，请在 `outputs/` 目录下查看生成的 Excel 报告。报告中详细记录了：
- **Hit**: 是否违规 (True=违规/不一致, False=合规/一致)
- **Evidence**: 详细的判断依据 (包含计算过程)
- **Confidence**: 置信度

## 🧩 关键逻辑说明

### 1. Rolling Balance (滚动余额) 校验
针对 `MSTAR_BBVA_DTL_AMT_SINGLE` 等规则，系统会自动识别 `Rolling` 或 `Balance` 关键词，并强制 Prompt 指令：**“严禁省略任何一行交易，必须展示每一步的计算结果”**。这杜绝了 LLM 偷懒只做首尾校验的问题。

### 2. Hit 状态智能修正
系统采用**“最后匹配原则” (Last Match Wins)**。即使 LLM 输出的 JSON 字段有误，只要其文本 Evidence 中明确写了“输出：不一致”或“hit=true”，系统会自动将状态修正为 **True (违规)**，确保人工阅读结论与系统判定一致。

### 3. 通用数据加载
不再限制 JSON 的 Section 类型。无论是 `account_summary`, `client_info` 还是未来新增的 `risk_analysis` 模块，都会直接进入 LLM 的上下文，彻底解决“Periodo 信息找不到”等问题。


