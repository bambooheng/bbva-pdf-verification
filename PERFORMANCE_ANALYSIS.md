# 性能分析与优化建议

## 当前执行缓慢的原因分析

### 1. **LLM API 调用时间长**
- 每条规则需要单独调用一次 LLM API
- 每次 API 调用通常需要 **1-2 分钟**
- 4 条规则 × 1-2 分钟 = **4-8 分钟**的总执行时间

### 2. **网络连接问题**
- 频繁出现 `ConnectionError`，导致重试
- 重试机制：最多重试 5 次，每次等待 4-30 秒
- 如果网络不稳定，单条规则可能需要 **2-3 分钟**甚至更长

### 3. **Prompt 数据量大**
- 优化后的 prompt 要求列出详细明细
- 完整的银行流水数据（可能包含多页）全部发送给 LLM
- Prompt 可能非常大（几万到几十万字符），增加处理时间

### 4. **串行处理**
- 规则是**串行处理**的，不能并行
- 必须等待前一条规则完成才能处理下一条

### 5. **超时设置**
- `REQUEST_TIMEOUT=120` 秒（2分钟）
- 如果网络慢，每次调用最多等待 2 分钟

## 优化方案

### 方案 1: 优化 Prompt 大小（推荐）

**问题**：当前会把所有银行流水数据都发送给 LLM，数据量很大。

**解决方案**：只提取与当前规则相关的数据部分。

```python
# 在 rule_parser.py 中，根据规则类型提取相关数据
# 例如：如果规则涉及 ABONOS，只提取包含 ABONOS 的交易
```

### 方案 2: 并行处理规则

**问题**：规则串行处理，效率低。

**解决方案**：使用多线程或多进程并行处理规则。

```python
# 使用 concurrent.futures 并行处理
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(process_rule, rule): rule for rule in rules}
```

### 方案 3: 使用更快的模型

**问题**：`gpt-4-turbo` 虽然准确，但速度较慢。

**解决方案**：
- 使用 `gpt-3.5-turbo`（更快，但可能准确度略低）
- 或使用 `deepseek-chat`（通常更快且便宜）

### 方案 4: 减少重试次数和超时时间

**问题**：重试次数多（5次），超时时间长（120秒）。

**解决方案**：
```env
MAX_RETRIES=3  # 从 5 减少到 3
REQUEST_TIMEOUT=60  # 从 120 减少到 60
```

### 方案 5: 添加进度显示

**问题**：用户不知道程序是否在运行。

**解决方案**：添加进度条或更详细的日志。

## 快速优化建议（立即可用）

### 1. 切换到更快的模型

编辑 `config/settings.env`：
```env
OPENAI_MODEL=gpt-3.5-turbo  # 从 gpt-4-turbo 改为 gpt-3.5-turbo
```

### 2. 或切换到 DeepSeek

编辑 `config/settings.env`：
```env
LLM_PROVIDER=deepseek
DEEPSEEK_MODEL=deepseek-chat
```

### 3. 减少超时时间

编辑 `config/settings.env`：
```env
REQUEST_TIMEOUT=60  # 从 120 改为 60
MAX_RETRIES=3  # 从 5 改为 3
```

## 预期效果

- **使用 gpt-3.5-turbo**：每条规则约 10-30 秒，总计 1-2 分钟
- **使用 deepseek**：每条规则约 5-15 秒，总计 30 秒-1 分钟
- **并行处理**：4 条规则同时处理，总时间 = 最长单条规则时间

## 注意事项

- 更快的模型可能准确度略低
- 并行处理需要确保 API 有足够的并发配额
- 减少超时时间可能导致网络不稳定时失败率增加

