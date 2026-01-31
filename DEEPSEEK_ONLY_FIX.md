# 只使用DeepSeek修复说明

## 问题描述

1. **结果不一致问题**：`MSTAR_BBVA_DTL_CNT_CARGOS`规则，之前每次运行结果都为未命中，清除缓存后重新运行为命中
2. **Provider调用失败**：有的规则返回"无法调用任何 LLM Provider"

## 修复方案

### 1. 禁用Fallback，只使用DeepSeek

**修改内容**：
- 添加`ENABLE_FALLBACK`配置项，默认值为`false`
- 当`ENABLE_FALLBACK=false`时，只使用配置的provider（DeepSeek），不使用其他provider作为fallback
- 确保相同输入相同规则，结果完全一致

**配置文件修改**：
```env
# Fallback配置（是否启用备用provider，默认禁用，只使用配置的provider）
ENABLE_FALLBACK=false
```

### 2. 增强重试机制

**修改内容**：
- 当禁用fallback时，即使`FAST_FAILOVER=true`，也会进行完整重试
- 确保DeepSeek调用失败时有足够的重试次数（`MAX_RETRIES`次）
- 避免直接返回"无法调用任何 LLM Provider"

**重试逻辑**：
```python
# 如果禁用fallback，必须重试；如果启用fallback且fast_failover，则快速失败
max_attempts = (self.max_retries + 1) if (not self.enable_fallback or not self.fast_failover) else 1
```

### 3. 改进错误处理

**修改内容**：
- 当禁用fallback时，如果DeepSeek调用失败，直接返回明确的错误信息
- 不再尝试其他provider，避免结果不一致
- 错误信息明确说明已重试的次数和失败原因

## 配置建议

### 确保结果一致性

```env
# LLM Provider配置
LLM_PROVIDER=deepseek

# 禁用fallback，只使用DeepSeek
ENABLE_FALLBACK=false

# 缓存配置（必须启用）
ENABLE_CACHE=true
CACHE_DIR=cache
LLM_TEMPERATURE=0.0

# 重试配置（确保有足够的重试次数）
MAX_RETRIES=5
REQUEST_TIMEOUT=120
```

### 性能优化（可选）

```env
# 如果网络稳定，可以启用fast_failover（但禁用fallback时不影响重试）
FAST_FAILOVER=true
```

## 验证方法

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

2. **Provider验证**：
   - 检查日志，确认只使用DeepSeek，没有尝试其他provider
   - 确认所有规则都使用相同的provider

3. **错误处理验证**：
   - 如果DeepSeek调用失败，应该看到明确的重试日志
   - 不应该出现"无法调用任何 LLM Provider"的错误

## 技术细节

### 缓存机制

- 缓存键只基于prompt的hash，不包含provider
- 确保相同prompt无论何时运行都返回相同结果
- 即使清除缓存后重新运行，如果LLM返回相同结果，应该得到一致的结果

### 重试机制

- 禁用fallback时：`max_attempts = MAX_RETRIES + 1`
- 启用fallback且fast_failover时：`max_attempts = 1`
- 启用fallback但未启用fast_failover时：`max_attempts = MAX_RETRIES + 1`

### 错误处理流程

1. 尝试调用DeepSeek API
2. 如果失败，根据配置进行重试
3. 如果所有重试都失败，返回明确的错误信息
4. 不再尝试其他provider（如果禁用fallback）

## 注意事项

1. **结果一致性**：
   - 启用缓存后，相同输入保证返回相同结果
   - 如果清除缓存后结果不同，可能是LLM本身的问题（模型更新、API负载均衡等）
   - 建议在生产环境中始终启用缓存

2. **Provider选择**：
   - 现在只使用DeepSeek，确保结果的一致性
   - 如果需要使用其他provider，可以修改`LLM_PROVIDER`配置

3. **错误处理**：
   - 如果DeepSeek调用失败，会进行完整重试
   - 如果所有重试都失败，会返回明确的错误信息
   - 不会出现"无法调用任何 LLM Provider"的情况（除非所有provider都未配置）

## 更新日志

- **2024-01-XX**：添加`ENABLE_FALLBACK`配置，默认禁用fallback
- **2024-01-XX**：修改重试逻辑，确保禁用fallback时有足够重试次数
- **2024-01-XX**：改进错误处理，避免"无法调用任何 LLM Provider"错误

