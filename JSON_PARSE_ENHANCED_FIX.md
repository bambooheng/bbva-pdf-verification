# JSON解析错误增强修复说明

## 问题描述

在处理`MSTAR_BBVA_DTL_AMT_SINGLE`规则时，仍然遇到JSON解析错误：
```
处理错误 (ValueError): PARSE_ERROR: ValueError: 未找到 JSON 格式
处理过程中发生异常: ValueError。Provider deepseek 调用失败。
```

## 增强修复方案

### 1. 更激进的JSON提取方法

添加了方法5：尝试查找任何包含大括号的文本块

```python
# 查找所有 { 位置
# 对每个 { 位置，尝试找到匹配的 }
# 检查是否包含必要的字段（如"hit"）
# 尝试解析以验证
```

### 2. 文本信息提取（最后手段）

如果完全无法提取JSON，尝试从文本中提取关键信息：

```python
# 尝试提取hit值
hit_patterns = [
    r'"hit"\s*:\s*(true|false|null)',
    r"'hit'\s*:\s*(True|False|None)",
    r'hit\s*=\s*(true|false|null)',
    r'hit\s*:\s*(true|false|null)',
]

# 尝试提取evidence值
evidence_patterns = [
    r'"evidence"\s*:\s*"([^"]*)"',
    r"'evidence'\s*:\s*'([^']*)'",
]
```

如果提取到任何信息，返回一个合理的结果而不是直接失败。

### 3. 改进错误处理

**修改前**：
- 解析失败后，如果重试次数用完，直接抛出异常
- 导致整个规则处理失败

**修改后**：
- 解析失败后，记录详细的错误信息（包括原始响应前2000字符）
- 如果重试次数用完，返回一个合理的结果（hit=null）
- 确保规则处理不会因为JSON解析失败而完全失败

```python
if parse_attempts >= self.max_parse_retries:
    logger.error(f"Provider {provider} 响应解析失败，已重试 {self.max_parse_retries} 次，返回null结果")
    result = {
        "hit": None,
        "evidence": f"LLM响应解析失败: {error_msg}。原始响应已记录在日志中。",
        "confidence": "low",
        "notes": f"Provider {provider} 返回的响应无法解析为JSON格式。已重试 {self.max_parse_retries} 次。建议检查日志获取完整响应内容。"
    }
    # 保存到缓存（即使是失败的结果）
    cache_key = self._get_cache_key(prompt)
    self._save_to_cache(cache_key, result)
    return result
```

## 修复效果

### 修复前

```
处理错误 (ValueError): PARSE_ERROR: ValueError: 未找到 JSON 格式
处理过程中发生异常: ValueError。Provider deepseek 调用失败。
建议重新运行程序或检查日志获取详细信息。
```

规则处理完全失败，无法继续。

### 修复后

即使JSON解析失败，也会：
1. **返回合理结果**：hit=null, confidence=low
2. **记录详细日志**：原始响应前2000字符
3. **提供错误信息**：在evidence和notes中说明问题
4. **继续处理**：不会因为单个规则的解析失败而中断整个审计流程

## 处理流程

### 正常情况

1. LLM返回JSON格式响应
2. 使用多种方法提取JSON
3. 清理和修复JSON格式
4. 成功解析并返回结果

### 异常情况（修复后）

1. LLM返回非JSON格式响应
2. 尝试多种方法提取JSON（5种方法）
3. 如果仍然失败，尝试从文本中提取关键信息
4. 如果提取到部分信息，返回部分结果
5. 如果完全无法提取，返回null结果（hit=null）
6. 记录详细错误信息到日志

## 日志改进

现在会记录：
- **原始响应前2000字符**：便于调试
- **提取的JSON文本**：如果提取到但无法解析
- **错误详情**：包括错误类型和位置

## 配置建议

如果经常遇到JSON解析问题，可以：

1. **增加重试次数**：
```env
MAX_PARSE_RETRIES=3
```

2. **检查日志**：
查看`logs/app.log`获取完整的LLM响应

3. **优化Prompt**：
在prompt中更明确地要求JSON格式输出

## 注意事项

1. **性能影响**：多种提取方法可能略微增加处理时间，但影响很小
2. **日志大小**：错误日志会记录完整的响应内容，可能较大
3. **结果准确性**：如果返回null结果，需要人工检查日志确认原因

## 更新日志

- **2024-01-XX**：添加更激进的JSON提取方法（方法5）
- **2024-01-XX**：添加文本信息提取功能（最后手段）
- **2024-01-XX**：改进错误处理，确保解析失败时返回合理结果
- **2024-01-XX**：增强日志记录，记录原始响应前2000字符





