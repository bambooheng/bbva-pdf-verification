# 快速部署指南

本文档提供最简化的部署步骤，适用于有经验的研发人员快速上手。详细说明请参考 [DEPLOYMENT.md](DEPLOYMENT.md)。

## 🚀 5 分钟快速部署

### 1. 环境检查

```bash
python --version  # 需要 3.10+
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制示例配置文件并编辑：

```bash
cp config/settings.env.example config/settings.env
```

编辑 `config/settings.env`，至少配置：
- 一个有效的 API Key（OPENAI_API_KEY、DEEPSEEK_API_KEY 或 AUTHORPIC_API_KEY）
- `LLM_PROVIDER`（与 API Key 对应）

### 4. 准备输入文件

将文件放入 `inputs/` 目录：
- 银行流水 JSON 文件（`*_structured.json` 或任意 `.json`）
- 审计规则 Excel 文件（`bbva_llm_rules_verification.xlsx`）

### 5. 运行

```bash
python main.py
```

### 6. 查看结果

结果文件在 `outputs/` 目录：
- `*_audit_report.json` - JSON 格式
- `*_audit_report.md` - Markdown 格式
- `*_audit_report.xlsx` - Excel 格式

## ⚙️ 最小配置示例

`config/settings.env` 最小配置：

```env
DEEPSEEK_API_KEY=sk-your-actual-key-here
LLM_PROVIDER=deepseek
```

其他配置项使用默认值即可。

## ✅ 验证部署

运行以下命令验证配置：

```bash
python -c "from src.config import Config; print('✓ 配置验证通过' if Config.validate() else '✗ 配置验证失败')"
```

## 🔧 常见问题快速解决

| 问题 | 解决方案 |
|------|---------|
| 配置验证失败 | 检查 API Key 是否正确配置 |
| 文件未找到 | 确认输入文件在 `inputs/` 目录 |
| 依赖安装失败 | `pip install --upgrade pip` 后重试 |
| API 调用失败 | 检查网络和 API Key 有效性 |

## 📚 更多信息

- 详细部署文档：`DEPLOYMENT.md`
- 项目说明：`README.md`

---

**提示**：首次部署建议阅读完整的 `DEPLOYMENT.md` 文档。

