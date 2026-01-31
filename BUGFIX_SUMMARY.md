# 问题修复总结

## 问题1：同一规则结果不一致

### 问题描述
`MSTAR_BBVA_DTL_CNT_CARGOS`规则，之前每次运行结果都为未命中，清除缓存后重新运行为命中。同样的报告同样的规则产生不同结果。

### 根本原因
1. **缓存键设计问题**：原缓存键包含`provider`和`model`，导致：
   - 第一次运行使用备用provider A，缓存键为`providerA:model:prompt`
   - 第二次运行主provider可用，缓存键为`providerB:model:prompt`
   - 缓存键不同，重新调用LLM，可能得到不同结果

2. **LLM的非确定性**：即使temperature=0，LLM在不同时间、不同实例可能返回不同结果

### 修复方案
1. **修改缓存键生成逻辑**：
   - 缓存键现在**只基于prompt的hash**，不包含provider和model
   - 确保相同prompt无论使用哪个provider都返回相同结果
   - 代码位置：`src/llm_judge.py` 的 `_get_cache_key` 方法

2. **添加统一缓存查找**：
   - 添加`_try_load_from_any_cache`方法，尝试从任何可能的缓存中加载
   - 确保即使provider不同，也能找到相同的缓存结果

### 验证方法
1. 运行两次相同输入，结果应该完全一致
2. 清除缓存后运行，结果应该与有缓存时一致（前提是LLM返回相同结果）
3. 检查日志，确认是否从缓存加载

---

## 问题2：无法调用任何LLM Provider

### 问题描述
有的规则在运行时候命中状态为"无法判断"，判断依据为"无法调用任何 LLM Provider"。

### 根本原因
1. **fast_failover机制问题**：
   - 当`FAST_FAILOVER=true`时，如果provider在冷却期，会跳过该provider
   - 如果所有provider都在冷却期，会跳过所有provider
   - 导致返回"无法调用任何 LLM Provider"错误

2. **错误处理不完善**：
   - 没有强制尝试机制，即使所有provider都在冷却期也应该至少尝试一次
   - 错误信息不够明确，没有显示已尝试的provider列表

### 修复方案
1. **强制尝试机制**：
   - 即使provider在冷却期，也会在最后强制尝试一次
   - 记录所有被跳过的provider，在正常provider都失败后强制尝试
   - 代码位置：`src/llm_judge.py` 的 `judge` 方法

2. **改进错误处理**：
   - 记录所有尝试的provider（`attempted_providers`）
   - 记录所有被跳过的provider（`providers_skipped_due_to_cooldown`）
   - 改进错误信息，明确显示已尝试的provider列表

3. **确保至少尝试一次**：
   - 即使所有provider都在冷却期，也会强制尝试一次
   - 避免直接返回"无法调用任何LLM Provider"错误

### 验证方法
1. 模拟所有provider都在冷却期的情况，应该强制尝试而不是直接失败
2. 检查日志，确认所有provider都被尝试过
3. 验证错误信息是否明确显示已尝试的provider列表

---

## 技术细节

### 缓存键生成（修复后）

```python
def _get_cache_key(self, prompt: str, provider: str = None, model: str = None) -> str:
    # 只基于prompt生成缓存键，确保相同输入无论使用哪个provider都返回相同结果
    return hashlib.sha256(prompt.encode('utf-8')).hexdigest()
```

### Provider尝试逻辑（修复后）

```python
# 记录已尝试的provider，确保至少尝试一次每个provider
attempted_providers = set()
providers_skipped_due_to_cooldown = []

for provider in providers_to_try:
    # 如果fast_failover启用且provider在冷却期，先跳过但记录
    if self.fast_failover and not self._provider_available(provider):
        providers_skipped_due_to_cooldown.append(provider)
        continue
    
    attempted_providers.add(provider)
    # ... 尝试调用 ...

# 如果所有正常provider都失败，强制尝试冷却期中的provider
if providers_skipped_due_to_cooldown:
    for skipped_provider in providers_skipped_due_to_cooldown:
        # 强制尝试一次
        ...
```

---

## 配置建议

### 确保结果一致性

```env
# 缓存配置（必须启用）
ENABLE_CACHE=true
CACHE_DIR=cache

# LLM温度参数（设置为0以提高确定性）
LLM_TEMPERATURE=0.0

# 重试配置（确保有足够的重试次数）
MAX_RETRIES=5
MAX_PARSE_RETRIES=2
```

### 避免Provider调用失败

```env
# 如果网络不稳定，可以禁用fast_failover
FAST_FAILOVER=false

# 或者增加重试次数
MAX_RETRIES=5
REQUEST_TIMEOUT=120
```

---

## 注意事项

1. **缓存依赖**：
   - 缓存基于prompt的hash，如果规则或数据发生变化，会自动生成新的缓存
   - 清除缓存后，相同输入应该得到相同结果（前提是LLM返回相同结果）

2. **Provider降级**：
   - 系统会自动尝试备用provider
   - 即使所有provider都在冷却期，也会强制尝试一次
   - 如果所有provider都失败，会返回明确的错误信息

3. **结果一致性**：
   - 启用缓存后，相同输入保证返回相同结果
   - 如果清除缓存后结果不同，可能是LLM本身的问题（模型更新、API负载均衡等）
   - 建议在生产环境中始终启用缓存

---

## 测试建议

1. **一致性测试**：
   ```bash
   # 第一次运行
   python main.py
   
   # 第二次运行（应该从缓存加载，结果完全一致）
   python main.py
   
   # 清除缓存后运行（应该与第一次结果一致）
   rm -rf cache
   python main.py
   ```

2. **Provider失败测试**：
   - 临时禁用所有API Key，验证错误处理
   - 模拟网络故障，验证重试机制
   - 验证强制尝试机制是否生效

3. **日志检查**：
   - 检查是否从缓存加载
   - 检查provider尝试顺序
   - 检查错误信息是否明确

