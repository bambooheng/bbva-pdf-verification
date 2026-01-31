# Periodo日期区间提取修复说明

## 问题描述

对于"交易日期校验_日期一致性"规则，LLM无法获取到页面1和页面2的layout_elements的content内容，导致无法提取"Periodo"日期区间。

**错误信息**：
```
数据状态：在"已提取的数据"中，未提供inputs的.json文件内容，也未提供页面1和页面2的layout_elements的content内容。因此，无法执行步骤1，无法获取规则中指定的"Periodo"日期区间。

结论：由于缺少执行规则步骤1所必需的数据（即页面1和页面2的原始文本内容），无法完成"交易日期校验_日期一致性"的审计判断。
```

## 根本原因

1. **数据提取不完整**：`get_relevant_text_content`方法只提取了`raw_text`字段，没有提取`layout_elements`的`content`字段
2. **页面过滤问题**：对于需要页面1和页面2内容的规则，没有特别处理这些页面
3. **规则识别不足**：没有检测规则是否需要"Periodo"或"日期区间"信息

## 修复方案

### 1. 添加规则类型检测

检测规则是否需要页面1和页面2的完整内容：
- 检测`condition_logic`或`validation_rule`中是否包含"periodo"、"日期区间"等关键词
- 检测`rule_name`中是否包含"日期一致性"、"交易日期校验"等关键词

```python
need_page1_page2 = (
    'periodo' in condition_logic or 'periodo' in validation_rule or
    '页面1' in condition_logic or '页面2' in condition_logic or
    'page 1' in condition_logic or 'page 2' in condition_logic or
    '日期区间' in condition_logic or '日期区间' in validation_rule or
    '日期一致性' in rule_name or '交易日期校验' in rule_name
)
```

### 2. 完整提取页面1和页面2内容

当检测到需要页面1和页面2内容时：
- 明确提取这些页面的所有`layout_elements`
- 提取每个元素的`raw_text`字段
- 提取每个元素的`content`字段（如果存在）
- 提取每个元素的`type`字段
- 按照y坐标排序，保持原始顺序

```python
if need_page1_page2:
    for page in pages:
        page_num = page.get('page_number')
        if page_num in [1, 2]:
            # 提取所有layout_elements的完整信息
            for element in sorted_elements:
                # 提取raw_text
                # 提取content字段
                # 提取type字段
```

### 3. 格式化输出

将提取的内容格式化为易读的文本格式：
```
=== 页面 1 完整内容（包含layout_elements的raw_text和content） ===
元素 1: raw_text: ... | content: {...} | type: ...
元素 2: raw_text: ... | content: {...} | type: ...
```

## 修复效果

修复后，对于需要"Periodo"信息的规则：
1. **完整数据提取**：页面1和页面2的所有layout_elements内容（包括raw_text和content）都会被提取
2. **明确标识**：提取的内容会明确标识为"页面1完整内容"和"页面2完整内容"
3. **结构化输出**：每个元素的信息以结构化格式输出，便于LLM解析

## 使用示例

### 规则要求示例

```
步骤1：从inputs的.json文件中获取页面1和页面2的layout_elements的content内容，并从中模糊匹配包含"Periodo"的信息以提取日期区间。
步骤2：从"Detalle de Movimientos Realizados"中提取所有OPER和LIQ日期，计算最小日期(min_date)和最大日期(max_date)。
校验规则：判断min_date和max_date是否在步骤1提取的日期区间内。
```

### 提取的数据格式

修复后，LLM会收到如下格式的数据：

```
=== 页面 1 完整内容（包含layout_elements的raw_text和content） ===
元素 1: raw_text: BBVA MEXICO | type: text
元素 2: raw_text: Periodo: 01/JUN - 31/JUL | type: text
元素 3: raw_text: ... | content: {index: 0, xref: 5, ext: png, width: 2550, height: 3300} | type: image
...

=== 页面 2 完整内容（包含layout_elements的raw_text和content） ===
元素 1: raw_text: ...
...
```

## 技术细节

### 检测逻辑

系统会检测以下关键词来判断是否需要页面1和页面2的完整内容：
- `periodo`（不区分大小写）
- `日期区间`
- `页面1`、`页面2`
- `page 1`、`page 2`
- `日期一致性`
- `交易日期校验`

### 提取逻辑

1. **排序**：按照bbox的y坐标排序，保持原始文档顺序
2. **提取字段**：
   - `raw_text`：文本内容
   - `content`：结构化内容（可能是字典或字符串）
   - `type`：元素类型
3. **格式化**：将提取的信息格式化为易读的文本格式

### 性能影响

- **内存占用**：轻微增加（只对页面1和页面2进行完整提取）
- **处理时间**：几乎无影响（只对特定规则进行额外处理）
- **Prompt大小**：可能增加（但只对需要的规则）

## 注意事项

1. **规则命名**：建议在规则名称或条件逻辑中包含"日期区间"、"Periodo"等关键词，以便系统自动识别
2. **数据完整性**：确保JSON文件包含页面1和页面2的完整layout_elements数据
3. **Content字段**：如果layout_elements的content字段为空或不存在，系统仍会提取raw_text和type字段

## 更新日志

- **2024-01-XX**：添加页面1和页面2完整内容提取功能
- **2024-01-XX**：支持提取layout_elements的content字段
- **2024-01-XX**：添加规则类型自动检测功能

