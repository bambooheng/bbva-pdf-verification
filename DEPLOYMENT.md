# BBVA 银行流水审计系统 - 部署文档

## 📋 目录

- [项目概述](#项目概述)
- [系统要求](#系统要求)
- [环境准备](#环境准备)
- [安装步骤](#安装步骤)
- [配置说明](#配置说明)
- [目录结构](#目录结构)
- [运行方法](#运行方法)
- [输出说明](#输出说明)
- [故障排除](#故障排除)
- [安全注意事项](#安全注意事项)
- [维护建议](#维护建议)
- [附录](#附录)

---

## 项目概述

BBVA 银行流水审计系统是一个基于 Python 的自动化审计程序，主要功能包括：

- 接收已 OCR 解析并结构化的 BBVA 银行流水 JSON 数据
- 结合用户提供的 Excel 格式的"审计规则清单"
- 逐条执行合规性检查
- 调用大模型（DeepSeek / OpenAI / Authorpic）进行智能判断
- 输出每条规则的审核结果及判断依据

### 核心特性

- ✅ **文件读取**：支持加载 JSON 流水和 Excel 审计规则
- ✅ **规则解析**：将 Excel 中的规则转换为内部可执行对象
- ✅ **智能判断**：调用大模型进行语义级匹配与推理
- ✅ **全覆盖审计**：确保所有规则都被执行，不允许遗漏
- ✅ **不确定处理**：若信息不足导致无法判断，返回 hit: null 并注明原因
- ✅ **日志记录**：记录关键流程、LLM 请求/响应、异常信息
- ✅ **错误处理**：对文件缺失、格式错误等情况有容错机制
- ✅ **结果导出**：支持导出为 JSON、Markdown 和 Excel 报告
- ✅ **并行处理**：支持多线程并行处理，提高审计效率
- ✅ **缓存机制**：支持结果缓存，确保结果一致性

---

## 系统要求

### 操作系统

- **Windows**: Windows 10 或更高版本
- **Linux**: Ubuntu 18.04+ / CentOS 7+ / 其他主流 Linux 发行版
- **macOS**: macOS 10.14+ 

### Python 环境

- **Python 版本**: Python 3.10 或更高版本（推荐 3.10+）
- **pip**: 最新版本

### 硬件要求

- **CPU**: 2 核或以上（推荐 4 核）
- **内存**: 4GB 或以上（推荐 8GB）
- **磁盘空间**: 至少 500MB 可用空间
- **网络**: 需要稳定的互联网连接（用于调用 LLM API）

### 依赖服务

- 需要访问以下 LLM 服务之一：
  - OpenAI API (可选)
  - DeepSeek API (可选)
  - Authorpic API (可选)

---

## 环境准备

### 1. 检查 Python 版本

```bash
python --version
# 或
python3 --version
```

确保版本为 Python 3.10 或更高。

### 2. 创建虚拟环境（推荐）

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 升级 pip

```bash
python -m pip install --upgrade pip
```

---

## 安装步骤

### 步骤 1: 获取项目代码

将项目文件复制到目标部署目录，例如：

```bash
# 假设项目已解压到部署目录
cd /path/to/bbva-pdf-verification_部署版本
```

### 步骤 2: 安装依赖包

在项目根目录下执行：

```bash
pip install -r requirements.txt
```

**依赖包列表：**
- `numpy<2.0.0` - 数值计算
- `pandas>=2.0.0` - 数据处理
- `openpyxl>=3.1.0` - Excel 文件操作
- `python-dotenv>=1.0.0` - 环境变量管理
- `requests>=2.31.0` - HTTP 请求
- `tenacity>=8.2.0` - 重试机制

### 步骤 3: 验证安装

```bash
python -c "import pandas, openpyxl, dotenv, requests, tenacity; print('所有依赖安装成功')"
```

### 步骤 4: 配置环境变量

#### 4.1 创建配置文件

确保 `config/settings.env` 文件存在。如果不存在，可以复制示例文件：

```bash
# 如果存在示例文件
cp config/settings.env.example config/settings.env
```

#### 4.2 编辑配置文件

编辑 `config/settings.env` 文件，配置以下内容：

```env
# ============================================
# API Keys（必须配置至少一个）
# ============================================
OPENAI_API_KEY=sk-your-openai-key-here
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
AUTHORPIC_API_KEY=sk-your-authorpic-key-here

# ============================================
# LLM Provider 选择（必须）
# 可选值: openai, deepseek, authorpic
# ============================================
LLM_PROVIDER=deepseek

# ============================================
# 文件路径配置
# ============================================
# 输入 JSON 文件路径（支持通配符，如 inputs/*.json）
INPUT_JSON_PATH=inputs/*.json
# 审计规则 Excel 文件路径
RULES_XLSX_PATH=inputs/bbva_llm_rules_verification.xlsx
# 输出文件路径（程序会自动根据输入文件名生成）
OUTPUT_REPORT_PATH=outputs/audit_report.json
OUTPUT_MARKDOWN_PATH=outputs/audit_report.md
OUTPUT_EXCEL_PATH=outputs/audit_report.xlsx

# ============================================
# 日志配置
# ============================================
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# ============================================
# LLM 配置
# ============================================
# 模型名称
OPENAI_MODEL=gpt-4-turbo
DEEPSEEK_MODEL=deepseek-chat
AUTHORPIC_MODEL=authorpic-model

# 重试配置
MAX_RETRIES=5              # API 调用最大重试次数
MAX_PARSE_RETRIES=1        # JSON 解析最大重试次数
REQUEST_TIMEOUT=120        # 请求超时时间（秒）

# ============================================
# 性能优化配置
# ============================================
PARALLEL_PROCESSING=true   # 是否启用并行处理
MAX_WORKERS=4              # 最大工作线程数（建议设置为 CPU 核心数）

# ============================================
# 缓存配置
# ============================================
ENABLE_CACHE=true          # 是否启用缓存
CACHE_DIR=cache            # 缓存目录
LLM_TEMPERATURE=0.0        # LLM 温度参数（0.0 表示确定性输出）

# ============================================
# Fallback 配置
# ============================================
ENABLE_FALLBACK=true       # 是否启用备用 provider（当主 provider 失败时）
```

**重要提示：**
- 必须配置至少一个有效的 API Key
- `LLM_PROVIDER` 必须与已配置的 API Key 对应
- API Key 不要包含引号，直接填写密钥值

### 步骤 5: 准备输入文件

#### 5.1 创建必要的目录

程序会自动创建以下目录（如果不存在）：
- `inputs/` - 输入文件目录
- `outputs/` - 输出文件目录
- `logs/` - 日志文件目录
- `cache/` - 缓存目录（如果启用缓存）

也可以手动创建：

```bash
mkdir -p inputs outputs logs cache
```

#### 5.2 准备输入文件

将以下文件放入 `inputs/` 目录：

1. **银行流水 JSON 文件**
   - 文件名格式：`*_structured.json` 或任意 `.json` 文件
   - 文件必须包含以下结构：
     ```json
     {
       "metadata": {
         "account_number": "账户号",
         "total_pages": 页数
       },
       "pages": [
         // 页面数据
       ]
     }
     ```

2. **审计规则 Excel 文件**
   - 文件名：`bbva_llm_rules_verification.xlsx`（或根据配置修改）
   - 必须包含以下列：
     - `Rule ID` - 规则唯一标识符（如 MSTAR_RULE_BBVA_001）
     - `Rule Name` - 规则名称（如"交易笔数校验_入账笔数"）
     - `Condition Logic` - 判断逻辑（详细的检查步骤说明）
     - `校验规则` - 比较规则（如"比较1和2是否相等"）
     - `决策结果` - 预期结果（如"如果相等，输出一致；如果不相等，输出不一致"）

### 步骤 6: 验证配置

运行配置验证：

```bash
python -c "from src.config import Config; print('配置验证:', '通过' if Config.validate() else '失败')"
```

如果验证失败，请检查：
- API Key 是否正确配置
- API Key 是否有效
- `LLM_PROVIDER` 是否与 API Key 匹配

---

## 配置说明

### 环境变量详解

#### API Keys

| 变量名 | 说明 | 是否必需 | 示例 |
|--------|------|---------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 使用 OpenAI 时必需 | `sk-proj-...` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 使用 DeepSeek 时必需 | `sk-...` |
| `AUTHORPIC_API_KEY` | Authorpic API 密钥 | 使用 Authorpic 时必需 | `sk-ant-api03-...` |

#### LLM Provider

| 变量名 | 说明 | 可选值 | 默认值 |
|--------|------|--------|--------|
| `LLM_PROVIDER` | 选择使用的 LLM 服务 | `openai`, `deepseek`, `authorpic` | `deepseek` |

#### 文件路径

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `INPUT_JSON_PATH` | 输入 JSON 文件路径（支持通配符） | `inputs/bank_statement.json` |
| `RULES_XLSX_PATH` | 审计规则 Excel 文件路径 | `inputs/audit_rules.xlsx` |
| `OUTPUT_REPORT_PATH` | 输出 JSON 报告路径 | `outputs/audit_report.json` |
| `OUTPUT_MARKDOWN_PATH` | 输出 Markdown 报告路径 | `outputs/audit_report.md` |
| `OUTPUT_EXCEL_PATH` | 输出 Excel 报告路径 | `outputs/audit_report.xlsx` |

#### 日志配置

| 变量名 | 说明 | 可选值 | 默认值 |
|--------|------|--------|--------|
| `LOG_LEVEL` | 日志级别 | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` |
| `LOG_FILE` | 日志文件路径 | 任意路径 | `logs/app.log` |

#### LLM 配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_MODEL` | OpenAI 模型名称 | `gpt-4-turbo` |
| `DEEPSEEK_MODEL` | DeepSeek 模型名称 | `deepseek-chat` |
| `AUTHORPIC_MODEL` | Authorpic 模型名称 | `authorpic-model` |
| `MAX_RETRIES` | API 调用最大重试次数 | `5` |
| `MAX_PARSE_RETRIES` | JSON 解析最大重试次数 | `1` |
| `REQUEST_TIMEOUT` | 请求超时时间（秒） | `120` |

#### 性能配置

| 变量名 | 说明 | 可选值 | 默认值 |
|--------|------|--------|--------|
| `PARALLEL_PROCESSING` | 是否启用并行处理 | `true`, `false` | `true` |
| `MAX_WORKERS` | 最大工作线程数 | 正整数 | `4` |

#### 缓存配置

| 变量名 | 说明 | 可选值 | 默认值 |
|--------|------|--------|--------|
| `ENABLE_CACHE` | 是否启用缓存 | `true`, `false` | `true` |
| `CACHE_DIR` | 缓存目录 | 任意路径 | `cache` |
| `LLM_TEMPERATURE` | LLM 温度参数 | 0.0-2.0 | `0.0` |

#### Fallback 配置

| 变量名 | 说明 | 可选值 | 默认值 |
|--------|------|--------|--------|
| `ENABLE_FALLBACK` | 是否启用备用 provider | `true`, `false` | `true` |

---

## 目录结构

```
bbva-pdf-verification_部署版本/
│
├── main.py                          # 主程序入口
├── requirements.txt                 # Python 依赖包列表
├── README.md                        # 项目说明文档
├── DEPLOYMENT.md                    # 部署文档（本文件）
│
├── config/                          # 配置文件目录
│   └── settings.env                 # 环境变量配置文件（需配置）
│
├── src/                             # 源代码目录
│   ├── __init__.py
│   ├── config.py                    # 配置管理模块
│   ├── data_loader.py               # 数据加载模块
│   ├── rule_parser.py               # 规则解析模块
│   ├── llm_judge.py                 # LLM 判断模块
│   ├── audit_engine.py              # 审计引擎核心模块
│   └── report_generator.py          # 报告生成模块
│
├── prompts/                         # 提示词目录
│   └── bbva_pdf_verification_prompt.md  # LLM 提示词模板
│
├── inputs/                          # 输入文件目录（需准备）
│   ├── *.json                       # 银行流水 JSON 文件
│   └── bbva_llm_rules_verification.xlsx  # 审计规则 Excel 文件
│
├── outputs/                         # 输出文件目录（自动创建）
│   ├── *_audit_report.json          # JSON 格式报告
│   ├── *_audit_report.md            # Markdown 格式报告
│   └── *_audit_report.xlsx          # Excel 格式报告
│
├── logs/                            # 日志文件目录（自动创建）
│   └── app.log                      # 应用日志文件
│
└── cache/                           # 缓存目录（自动创建，如果启用缓存）
    └── *.json                       # 缓存文件（JSON 格式）
```

---

## 运行方法

### 基本运行

在项目根目录下执行：

```bash
python main.py
```

### 运行流程

1. **程序启动**
   - 加载配置文件
   - 验证配置有效性
   - 初始化日志系统

2. **数据加载**
   - 加载银行流水 JSON 文件
   - 加载审计规则 Excel 文件
   - 解析规则为内部对象

3. **执行审计**
   - 遍历所有审计规则
   - 对每条规则调用 LLM 进行判断
   - 记录判断结果和依据

4. **生成报告**
   - 生成 JSON 格式报告
   - 生成 Markdown 格式报告
   - 生成 Excel 格式报告

5. **输出结果**
   - 在控制台显示摘要信息
   - 将详细报告保存到 `outputs/` 目录

### 运行示例

```bash
$ python main.py

============================================================
BBVA 银行流水审计系统启动
============================================================
2024-01-01 10:00:00 - __main__ - INFO - 加载银行流水: inputs/*.json
2024-01-01 10:00:00 - __main__ - INFO - 加载审计规则: inputs/bbva_llm_rules_verification.xlsx
2024-01-01 10:00:01 - __main__ - INFO - 正在加载数据...
2024-01-01 10:00:02 - __main__ - INFO - 开始执行审计...
2024-01-01 10:05:30 - __main__ - INFO - 审计完成: 共处理 50 条规则
2024-01-01 10:05:30 - __main__ - INFO - 命中: 12, 未命中: 35, 无法判断: 3
2024-01-01 10:05:30 - __main__ - INFO - 正在生成报告...
============================================================
审计报告生成完成！
JSON 报告: outputs/BBVA_MAR-ABR造假1-MSN20250609098_audit_report.json
Markdown 报告: outputs/BBVA_MAR-ABR造假1-MSN20250609098_audit_report.md
Excel 报告: outputs/BBVA_MAR-ABR造假1-MSN20250609098_audit_report.xlsx
============================================================
```

### 批量处理

如果 `INPUT_JSON_PATH` 配置为通配符（如 `inputs/*.json`），程序会自动处理所有匹配的 JSON 文件。

---

## 输出说明

### 输出文件命名规则

输出文件名基于输入 JSON 文件名自动生成：

- 输入文件：`BBVA_MAR-ABR造假1-MSN20250609098_structured.json`
- 输出文件：
  - `BBVA_MAR-ABR造假1-MSN20250609098_audit_report.json`
  - `BBVA_MAR-ABR造假1-MSN20250609098_audit_report.md`
  - `BBVA_MAR-ABR造假1-MSN20250609098_audit_report.xlsx`

### JSON 报告格式

```json
{
  "metadata": {
    "generated_at": "2024-01-01T10:05:30",
    "account_number": "账户号",
    "total_pages": 10,
    "llm_provider": "deepseek",
    "llm_model": "deepseek-chat",
    "total_rules": 50
  },
  "summary": {
    "total_rules": 50,
    "hit_count": 12,
    "not_hit_count": 35,
    "unknown_count": 3
  },
  "results": [
    {
      "rule_id": "MSTAR_RULE_BBVA_001",
      "rule_name": "交易笔数校验_入账笔数",
      "hit": true,
      "evidence": "1金额为5000，2金额为10000，不相等",
      "confidence": "high",
      "notes": "补充说明（可选）"
    }
  ]
}
```

### Markdown 报告格式

Markdown 报告包含：
- 审计摘要
- 规则执行结果表格
- 详细判断依据

### Excel 报告格式

Excel 报告包含：
- 摘要工作表
- 详细结果工作表
- 每条规则的完整信息

---

## 故障排除

### 问题 1: Python 版本不兼容

**症状：**
```
SyntaxError: invalid syntax
```

**解决方案：**
- 确保使用 Python 3.10 或更高版本
- 检查虚拟环境中的 Python 版本

### 问题 2: 依赖包安装失败

**症状：**
```
ERROR: Could not find a version that satisfies the requirement
```

**解决方案：**
- 升级 pip: `python -m pip install --upgrade pip`
- 使用国内镜像源：
  ```bash
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```

### 问题 3: API Key 未配置或无效

**症状：**
```
错误: 请配置 DEEPSEEK_API_KEY
配置验证: 失败
```

**解决方案：**
1. 检查 `config/settings.env` 文件是否存在
2. 确认 API Key 已正确填写（无引号、无多余空格）
3. 验证 API Key 是否有效（可在对应服务商网站测试）
4. 确认 `LLM_PROVIDER` 与 API Key 匹配

### 问题 4: 文件未找到

**症状：**
```
FileNotFoundError: [Errno 2] No such file or directory: 'inputs/bank_statement.json'
```

**解决方案：**
1. 检查 `INPUT_JSON_PATH` 配置是否正确
2. 确认输入文件存在于指定路径
3. 检查文件路径中的中文字符是否正确编码
4. 如果使用通配符，确认至少有一个匹配的文件

### 问题 5: Excel 格式错误

**症状：**
```
KeyError: 'Rule ID'
```

**解决方案：**
1. 确认 Excel 文件包含所有必需的列：
   - `Rule ID`
   - `Rule Name`
   - `Condition Logic`
   - `校验规则`
   - `决策结果`
2. 检查列名是否完全匹配（区分大小写）
3. 确认第一行是表头，不是数据行

### 问题 6: LLM API 调用失败

**症状：**
```
requests.exceptions.RequestException
API 调用失败，已重试 X 次
```

**解决方案：**
1. 检查网络连接
2. 验证 API Key 是否有效
3. 检查 API 服务是否可用
4. 查看 `logs/app.log` 获取详细错误信息
5. 如果持续失败，考虑启用 `ENABLE_FALLBACK=true` 使用备用 provider

### 问题 7: 内存不足

**症状：**
```
MemoryError
```

**解决方案：**
1. 减少 `MAX_WORKERS` 数量
2. 设置 `PARALLEL_PROCESSING=false` 禁用并行处理
3. 增加系统内存
4. 分批处理大型 JSON 文件

### 问题 8: 编码问题（Windows）

**症状：**
```
UnicodeDecodeError
控制台中文乱码
```

**解决方案：**
- 程序已自动处理 Windows 控制台编码问题
- 如果仍有问题，设置环境变量：
  ```powershell
  $env:PYTHONIOENCODING="utf-8"
  ```

### 问题 9: 权限错误

**症状：**
```
PermissionError: [Errno 13] Permission denied
```

**解决方案：**
1. 检查文件/目录权限
2. 确认有写入权限（对于 outputs、logs、cache 目录）
3. 在 Linux/macOS 上，可能需要使用 `sudo`（不推荐）或修改目录权限

### 问题 10: 缓存问题

**症状：**
- 结果不一致
- 使用了旧的缓存数据

**解决方案：**
1. 清除缓存目录：`rm -rf cache/*`（Linux/macOS）或删除 `cache` 目录（Windows）
2. 设置 `ENABLE_CACHE=false` 禁用缓存
3. 定期清理缓存文件

---

## 安全注意事项

### 1. API Key 安全

⚠️ **重要：不要将 API Key 提交到版本控制系统**

- 确保 `config/settings.env` 已添加到 `.gitignore`
- 不要在代码中硬编码 API Key
- 定期轮换 API Key
- 使用环境变量或密钥管理服务（生产环境推荐）

### 2. 文件权限

- 限制 `config/settings.env` 文件的访问权限
- 在 Linux/macOS 上：
  ```bash
  chmod 600 config/settings.env
  ```

### 3. 网络安全

- 确保 API 调用使用 HTTPS
- 在生产环境中考虑使用代理或 VPN
- 监控 API 调用频率，避免超出限制

### 4. 数据安全

- 输入文件可能包含敏感信息，妥善保管
- 输出文件同样包含敏感信息，注意访问控制
- 定期清理不需要的输入/输出文件
- 考虑对敏感数据进行加密存储

### 5. 日志安全

- 日志文件可能包含敏感信息，注意访问控制
- 定期清理或归档日志文件
- 在生产环境中考虑使用日志管理服务

---

## 维护建议

### 1. 定期更新依赖

```bash
# 检查过时的包
pip list --outdated

# 更新所有包（谨慎操作）
pip install --upgrade -r requirements.txt
```

### 2. 监控日志

- 定期查看 `logs/app.log`
- 关注错误和警告信息
- 监控 API 调用失败率

### 3. 清理缓存

```bash
# 定期清理缓存（建议每周一次）
rm -rf cache/*
```

### 4. 备份配置

- 定期备份 `config/settings.env`
- 备份审计规则 Excel 文件
- 备份重要的输出报告

### 5. 性能优化

- 根据实际 CPU 核心数调整 `MAX_WORKERS`
- 如果内存充足，可以增加 `MAX_WORKERS`
- 如果网络不稳定，增加 `MAX_RETRIES` 和 `REQUEST_TIMEOUT`

### 6. 监控 API 使用

- 定期检查 API 使用量
- 设置使用量告警
- 优化提示词以减少 token 消耗

---

## 附录

### A. 环境变量配置模板

创建 `config/settings.env.example` 作为模板：

```env
# API Keys
OPENAI_API_KEY=sk-xxxxxx
DEEPSEEK_API_KEY=sk-xxxxxx
AUTHORPIC_API_KEY=sk-xxxxxx

# LLM Provider 选择: openai, deepseek, authorpic
LLM_PROVIDER=deepseek

# 文件路径配置
INPUT_JSON_PATH=inputs/*.json
RULES_XLSX_PATH=inputs/bbva_llm_rules_verification.xlsx
OUTPUT_REPORT_PATH=outputs/audit_report.json
OUTPUT_MARKDOWN_PATH=outputs/audit_report.md
OUTPUT_EXCEL_PATH=outputs/audit_report.xlsx

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# LLM 配置
OPENAI_MODEL=gpt-4-turbo
DEEPSEEK_MODEL=deepseek-chat
AUTHORPIC_MODEL=authorpic-model
MAX_RETRIES=5
MAX_PARSE_RETRIES=1
REQUEST_TIMEOUT=120

# 性能优化配置
PARALLEL_PROCESSING=true
MAX_WORKERS=4

# 缓存配置
ENABLE_CACHE=true
CACHE_DIR=cache
LLM_TEMPERATURE=0.0

# Fallback配置
ENABLE_FALLBACK=true
```

### B. 快速部署检查清单

- [ ] Python 3.10+ 已安装
- [ ] 虚拟环境已创建并激活
- [ ] 依赖包已安装
- [ ] `config/settings.env` 已配置
- [ ] API Key 已填写并验证
- [ ] `LLM_PROVIDER` 已正确设置
- [ ] 输入文件已准备（JSON 和 Excel）
- [ ] 配置验证通过
- [ ] 测试运行成功

### C. 常用命令

```bash
# 验证配置
python -c "from src.config import Config; print('配置验证:', '通过' if Config.validate() else '失败')"

# 检查依赖
pip list

# 查看日志（最后 50 行）
tail -n 50 logs/app.log

# 清理缓存
rm -rf cache/*

# 清理输出
rm -rf outputs/*

# 清理日志
rm -f logs/app.log
```

### D. 联系支持

如遇到问题，请提供以下信息：

1. Python 版本：`python --version`
2. 操作系统版本
3. 错误日志：`logs/app.log` 中的相关错误
4. 配置文件（隐藏敏感信息）：`config/settings.env` 的结构（不包含实际 API Key）
5. 输入文件格式说明（不包含实际数据）

---

## 版本信息

- **文档版本**: 1.0
- **最后更新**: 2024-01-01
- **适用项目版本**: 部署版本

---

**祝部署顺利！** 🚀

