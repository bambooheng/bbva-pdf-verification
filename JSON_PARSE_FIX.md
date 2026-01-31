# JSON解析错误修复说明

## 问题描述

在处理`MSTAR_BBVA_DTL_AMT_SINGLE`规则时，返回处理错误：
```
处理错误 (ValueError): PARSE_ERROR: ValueError: 未找到 JSON 格式
```

## 根本原因

1. **LLM响应格式不一致**：LLM可能返回多种格式的响应：
   - 纯JSON格式：`{"hit": true, ...}`
   - Markdown代码块：`` ```json {...} ``` ``
   - 通用代码块：`` ``` {...} ``` ``
   - 包含额外文本：`根据分析，结果如下：{"hit": true, ...}`

2. **JSON提取逻辑不够健壮**：原代码只尝试了几种简单的提取方式，无法处理所有情况

3. **JSON格式错误**：LLM可能返回包含语法错误的JSON（如尾随逗号）

## 修复方案

### 1. 多方法JSON提取

实现了多种JSON提取方法，按优先级尝试：

**方法1：查找JSON代码块**
```python
# 查找 ```json ... ``` 格式
if "```json" in response_text:
    # 提取代码块内容
```

**方法2：查找通用代码块**
```python
# 查找 ``` ... ``` 格式
if "```" in response_text:
    # 检查是否包含JSON结构
    if candidate.startswith("{") and candidate.endswith("}"):
        # 提取JSON
```

**方法3：直接查找JSON对象**
```python
# 从第一个 { 开始，找到匹配的最后一个 }
# 使用括号计数确保找到完整的JSON对象
```

**方法4：正则表达式匹配**
```python
# 查找包含 "hit" 字段的JSON对象
# 尝试扩展匹配以包含完整的JSON对象
```

### 2. JSON清理和修复

在解析JSON之前，尝试修复常见的格式错误：

```python
# 移除尾随逗号（在 } 或 ] 之前）
json_text_cleaned = re.sub(r',\s*}', '}', json_text_cleaned)
json_text_cleaned = re.sub(r',\s*]', ']', json_text_cleaned)
```

### 3. 错误处理和日志

改进错误处理，提供更详细的错误信息：

```python
# 记录原始响应（前1000字符）
logger.error(f"JSON 解析失败。原始响应前1000字符:\n{original_response[:1000]}")
# 记录提取的JSON文本（前500字符）
logger.error(f"提取的JSON文本:\n{json_text[:500]}")
```

### 4. 回退机制

如果清理后的JSON无法解析，尝试原始文本：

```python
try:
    result = json.loads(json_text_cleaned)
except json.JSONDecodeError:
    # 尝试原始文本
    try:
        result = json.loads(json_text)
    except json.JSONDecodeError:
        # 记录详细错误信息
        raise ValueError(f"JSON 解析失败: {e}")
```

## 修复效果

修复后，系统能够：

1. **处理多种响应格式**：无论LLM返回什么格式，都能尝试提取JSON
2. **修复常见错误**：自动修复尾随逗号等常见JSON格式错误
3. **提供详细日志**：当解析失败时，记录完整的响应内容，便于调试
4. **提高成功率**：通过多种提取方法和回退机制，大大提高JSON解析的成功率

## 使用示例

### 修复前

如果LLM返回：
```
根据分析，结果如下：
```json
{
  "hit": true,
  "evidence": "...",
  "confidence": "high"
}
```
```

原代码可能无法正确提取JSON。

### 修复后

系统会：
1. 检测到````json`代码块
2. 提取代码块内容
3. 清理可能的格式错误
4. 成功解析JSON

## 技术细节

### JSON提取优先级

1. **JSON代码块**（`` ```json ... ``` ``）：最高优先级
2. **通用代码块**（`` ``` ... ``` ``）：次优先级
3. **直接查找**：从第一个`{`开始，找到匹配的`}`
4. **正则匹配**：查找包含`"hit"`字段的JSON对象

### JSON清理规则

- 移除尾随逗号：`,}` → `}`, `,]` → `]`
- 保留其他格式（如引号、转义字符等）

### 错误处理流程

1. 尝试提取JSON（多种方法）
2. 清理JSON文本
3. 尝试解析清理后的JSON
4. 如果失败，尝试原始JSON文本
5. 如果仍然失败，记录详细错误信息并抛出异常

## 注意事项

1. **性能影响**：多种提取方法可能略微增加处理时间，但影响很小
2. **日志大小**：错误日志会记录完整的响应内容，可能较大
3. **兼容性**：修复后的代码向后兼容，不会影响正常工作的规则

## 更新日志

- **2024-01-XX**：添加多种JSON提取方法
- **2024-01-XX**：添加JSON清理和修复功能
- **2024-01-XX**：改进错误处理和日志记录

