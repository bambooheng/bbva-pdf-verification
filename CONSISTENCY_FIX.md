# 结果一致性修复说明

## 问题描述

多次运行程序时，同一份报告的同一条规则可能产生不一致的结果。

## 根本原因

1. **LLM的非确定性**：即使temperature设置为0.1，LLM仍然可能因为内部随机性、API负载均衡或模型更新而产生不同的结果
2. **缺少缓存机制**：每次运行都重新调用LLM，即使输入完全相同
3. **数据提取顺序**：虽然代码中有排序逻辑，但在某些边界情况下可能产生细微差异

## 解决方案

### 1. 添加缓存机制

- **实现方式**：基于prompt、provider和model的hash值生成缓存键
- **缓存位置**：`cache/` 目录（可配置）
- **缓存内容**：完整的LLM判断结果（hit, evidence, confidence, notes）
- **优势**：相同输入保证返回相同结果，避免重复调用LLM

### 2. 降低Temperature参数

- **修改前**：temperature = 0.1
- **修改后**：temperature = 0.0（可配置）
- **优势**：最大程度减少LLM的随机性

### 3. 确保数据提取的确定性

- **改进**：使用稳定的排序算法，确保相同坐标的元素保持原始顺序
- **实现**：在排序键中添加`id()`作为辅助键，保证排序的稳定性

## 配置选项

在 `config/settings.env` 中添加了以下配置：

```env
# 缓存配置（用于确保结果一致性）
ENABLE_CACHE=true          # 是否启用缓存（默认：true）
CACHE_DIR=cache           # 缓存目录（默认：cache）
LLM_TEMPERATURE=0.0        # LLM温度参数（默认：0.0，推荐值：0.0-0.1）
```

## 使用方法

### 启用缓存（推荐）

保持默认配置即可，缓存会自动启用：
- 首次运行：正常调用LLM并缓存结果
- 后续运行：相同输入直接从缓存读取，确保结果一致

### 禁用缓存

如果需要每次都重新调用LLM（例如测试不同模型版本），可以设置：
```env
ENABLE_CACHE=false
```

### 清除缓存

如果需要清除所有缓存并重新生成结果：
```bash
# Windows
rmdir /s /q cache

# Linux/Mac
rm -rf cache
```

## 注意事项

1. **缓存依赖**：缓存基于prompt的hash值，如果规则或数据发生变化，会自动生成新的缓存
2. **磁盘空间**：缓存文件会占用一定磁盘空间，建议定期清理旧缓存
3. **版本控制**：建议将`cache/`目录添加到`.gitignore`，避免提交缓存文件
4. **Temperature设置**：
   - `0.0`：最大确定性，推荐用于生产环境
   - `0.1`：轻微随机性，可用于需要一定变化的场景
   - `>0.5`：不推荐用于审计场景，随机性过大

## 验证方法

1. **运行两次相同输入**：
   ```bash
   python main.py
   python main.py
   ```
   两次运行的结果应该完全一致

2. **检查缓存**：
   - 查看`cache/`目录，应该包含缓存文件
   - 第二次运行时，日志中应该显示"从缓存加载结果"

3. **对比结果**：
   - 比较两次运行的输出JSON文件
   - 所有规则的hit值、evidence、confidence应该完全相同

## 技术细节

### 缓存键生成

```python
cache_key = sha256(f"{provider}:{model}:{prompt}")
```

### 缓存文件格式

```json
{
  "hit": true/false/null,
  "evidence": "...",
  "confidence": "high/medium/low",
  "notes": "..."
}
```

### 排序稳定性

使用Python的`sorted()`函数，通过添加`id()`作为辅助键确保稳定性：
```python
sorted_elements = sorted(layout_elements, key=lambda e: (get_y_position(e), id(e)))
```

## 性能影响

- **首次运行**：无影响（正常调用LLM）
- **后续运行**：显著提升（从缓存读取，几乎瞬间完成）
- **磁盘I/O**：轻微增加（读写缓存文件）
- **内存占用**：无显著影响

## 故障排除

### 问题：缓存未生效

**可能原因**：
1. `ENABLE_CACHE=false`
2. 缓存目录权限问题
3. prompt内容发生变化（导致hash不同）

**解决方法**：
1. 检查配置文件中的`ENABLE_CACHE`设置
2. 检查`cache/`目录的读写权限
3. 查看日志确认是否从缓存加载

### 问题：结果仍然不一致

**可能原因**：
1. 缓存被禁用
2. 数据文件或规则文件发生变化
3. LLM API返回了不同的结果（即使temperature=0）

**解决方法**：
1. 确认`ENABLE_CACHE=true`且`LLM_TEMPERATURE=0.0`
2. 确认输入文件未发生变化
3. 清除缓存后重新运行，如果仍然不一致，可能是LLM API的问题

## 重要修复（最新）

### 修复1：缓存机制优化

**问题**：清除缓存后，同一规则的结果从"未命中"变成了"命中"，说明缓存机制存在问题。

**原因**：
- 原缓存键包含provider和model，导致使用不同provider时缓存键不同
- 第一次运行可能使用备用provider A，第二次运行主provider可用，缓存键不同，重新调用LLM得到不同结果

**修复**：
- 缓存键现在**只基于prompt的hash**，不包含provider和model
- 确保相同prompt无论使用哪个provider都返回相同结果
- 添加了`_try_load_from_any_cache`方法，尝试从任何可能的缓存中加载

### 修复2：确保至少尝试所有provider

**问题**：有些规则返回"无法调用任何 LLM Provider"，这是不应该发生的。

**原因**：
- 当`fast_failover`启用时，如果所有provider都在冷却期，会跳过所有provider
- 导致返回"无法调用任何 LLM Provider"错误

**修复**：
- 即使provider在冷却期，也会在最后强制尝试一次
- 记录所有尝试的provider，确保至少尝试一次每个provider
- 改进错误信息，明确显示已尝试的provider列表

## 更新日志

- **2024-01-XX**：修复缓存机制，确保相同prompt得到相同结果
- **2024-01-XX**：修复"无法调用任何LLM Provider"问题，确保至少尝试所有provider
- **2024-01-XX**：添加缓存机制和temperature配置
- **2024-01-XX**：优化数据提取的排序稳定性

