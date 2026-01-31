# BBVA 银行流水审计报告

**生成时间**: 2026-01-31 21:25:02

## 元数据

- **account_number**: 1512353873
- **total_pages**: 7
- **llm_provider**: deepseek
- **llm_model**: deepseek-chat

## 审计摘要

- **总规则数**: 10
- **命中规则数** (违规): 5
- **未命中规则数** (合规): 5
- **无法判断规则数**: 0

### 置信度分布

- **高置信度**: 10
- **中置信度**: 0
- **低置信度**: 0

## 详细审计结果

### 1. 明细交易笔数校验_入账笔数

**规则ID**: `MSTAR_BBVA_DTL_CNT_ABONOS`

**命中状态**: ✅ **命中** (违规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_CNT_ABONOS
规则名称: 明细交易笔数校验_入账笔数

执行步骤与结果：
(Step 1) 从 'Comportamiento' 表格中提取 'Depósitos / Abonos (+)'（入账）对应的总笔数（Total Movimientos Abonos）。
- 执行结果：在提供的 'Comportamiento' 部分，'Depósitos / Abonos (+): 8  22,400.01'，因此数值1（来自Comportamiento的入账总笔数）为 8。

(Step 2) 遍历 'Detalle de Movimientos Realizados'或raw_transaction_data（交易明细）部分的所有交易行。
- 执行结果：明细部分总共有 20 行交易记录。

(Step 3) [关键过滤] 仅统计 'Abonos' 列有有效数值（非空且不为0）的行。如果某行只有 'Cargo' 列有值，必须忽略。
- 执行结果：根据规则，逐行检查明细数据中的 'Abono' 字段，统计其值为有效数值（非空且不为0）的行。符合条件的交易明细如下（按原始顺序列出）：
1. Abono: 1200.0
2. Abono: 1000.0
6. Abono: 700.0
8. Abono: 16000.0
9. Abono: 250.0
10. Abono: 1700.0
11. Abono: 2100.0
16. Abono: 600.0
18. Abono: 800.0
19. Abono: 0.01

(Step 4) 计算符合条件的交易总行数。
- 执行结果：共统计到 10 笔有效 Abonos 交易。因此数值2（来自明细的入账总笔数）为 10。

校验规则：比较1和2是否相等。
- 比较结果：数值1 (8) 不等于 数值2 (10)。

决策结果：如果不相等，输出不一致（异常）。
- 最终结论：入账笔数不一致，存在异常。

hit 值判定理由：根据规则，两个数值不相等，决策结果为“不一致”，因此 hit=true。

**补充说明**: 数据中已明确提供'其中包含有效 Abonos (入账) 的交易数: 10'，与手动统计结果一致，确认了数值2的准确性。数值1来自Comportamiento表格，明确为8。两者确实不相等。

---

### 2. 明细交易笔数校验_出账笔数

**规则ID**: `MSTAR_BBVA_DTL_CNT_CARGOS`

**命中状态**: ✅ **命中** (违规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_CNT_CARGOS
规则名称: 明细交易笔数校验_出账笔数

执行步骤与结果：
(Step 1) 从 'Comportamiento' 表格中提取 'Retiros / Cargos (-)'（出账）对应的总笔数（Total Movimientos Cargos）。
- 数据来源：在提供的 'Comportamiento' 和 'total_movimientos' 部分，均明确列出 'Retiros / Cargos (-)' 的笔数为 12。
- 提取结果：数值1 (来自Comportamiento) = 12。

(Step 2) 遍历 'Detalle de Movimientos Realizados'（交易明细）部分的所有交易行。
- 明细部分总笔数为 20。

(Step 3) [关键过滤] 仅统计 'Cargos' 列有有效数值（非空且不为0）的行。如果某行只有 'Abono' 列有值，必须忽略。
- 根据规则，逐行检查 'Cargo' 字段。
- 有效 Cargos 交易明细如下（按原始顺序列出，共10笔）：
  1. 行3: Cargo:1690.78
  2. 行4: Cargo:500.0
  3. 行5: Cargo:19.0
  4. 行7: Cargo:700.0
  5. 行12: Cargo:350.0
  6. 行13: Cargo:520.0
  7. 行14: Cargo:300.0
  8. 行15: Cargo:1400.0
  9. 行17: Cargo:2100.0
  10. 行20: Cargo:299.0

(Step 4) 计算符合条件的交易总行数。
- 统计结果：数值2 (来自明细统计) = 10。

校验规则：比较数值1和数值2是否相等。
- 数值1 (Comportamiento 出账笔数) = 12
- 数值2 (明细有效Cargos笔数) = 10
- 比较结果：12 ≠ 10，两者不相等。

决策结果：如果不相等，输出不一致（异常）。

结论：明细中统计的有效出账（Cargos）交易笔数（10笔）与Comportamiento中报告的总出账笔数（12笔）不一致。

hit值判定：根据规则，数值不相等 → 输出“不一致” → hit=true。

**补充说明**: 数据中提供的参考值'其中包含有效 Cargos (出账) 的交易数: 10'与手动统计结果一致，确认了明细统计的准确性。Comportamiento中明确报告出账笔数为12，两者存在差异。

---

### 3. 明细交易金额校验_入账金额

**规则ID**: `MSTAR_BBVA_DTL_AMT_ABONOS`

**命中状态**: ✅ **命中** (违规)

**置信度**: HIGH

**判断依据**:

> 【执行步骤说明】
严格按照规则定义的判断逻辑执行：
Step 1: 从 'Comportamiento' 表格中提取 'Depósitos / Abonos (+)' 对应的总金额。提取结果为：22,400.01。
Step 2: 遍历 'Detalle de Movimientos Realizados' 部分。
Step 3: 累加所有 'Abonos' 列的数值，忽略 'Cargo' 列。
Step 4: 确保金额格式转换正确（处理千分位逗号）。明细中金额无千分位逗号，直接累加。

【明细数据与计算过程】
根据规则，列出所有 'Abonos' 列不为空的交易（共10笔，与参考值'有效 Abonos 交易数: 10'一致），并按原始顺序累加：
1. Abono: 1200.0
2. Abono: 1000.0
6. Abono: 700.0
8. Abono: 16000.0
9. Abono: 250.0
10. Abono: 1700.0
11. Abono: 2100.0
16. Abono: 600.0
18. Abono: 800.0
19. Abono: 0.01

求和计算：
1200.0 + 1000.0 + 700.0 + 16000.0 + 250.0 + 1700.0 + 2100.0 + 600.0 + 800.0 + 0.01 = 22350.01

【校验与结论】
数值1 (来自 Comportamiento): 22,400.01
数值2 (来自明细累加): 22,350.01
比较结果：22,400.01 ≠ 22,350.01，两者不相等。

根据校验规则：比较1和2是否相等。
根据决策结果：如果不相等，输出不一致（异常）。
因此，判定为不一致（异常），hit=true。

**补充说明**: 明细累加总额(22,350.01)与Comportamiento中报告的总额(22,400.01)存在49.99的差异。差异可能源于数据提取或原始报告中的错误。

---

### 4. 明细交易金额校验_出账金额

**规则ID**: `MSTAR_BBVA_DTL_AMT_CARGOS`

**命中状态**: ✅ **命中** (违规)

**置信度**: HIGH

**判断依据**:

> 【执行步骤说明】
严格按照规则MSTAR_BBVA_DTL_AMT_CARGOS的判断逻辑执行：
Step 1: 从'Comportamiento'表格中提取'Retiros / Cargos (-)'（出账）对应的总金额。
- 数据来源：Comportamiento部分明确列出：'Retiros / Cargos (-): 12  9,828.78'。
- 提取结果：数值1 = 9828.78。
Step 2 & 3: 遍历'Detalle de Movimientos Realizados'，累加所有'Cargos'列的数值，忽略'Abono'列。
- 数据来源：明细交易列表，共20笔。
- 关键过滤：仅累加'Cargo'字段不为'无'的交易。
- 逐笔明细（按原始顺序列出所有Cargos不为空的交易）：
1. 交易3: Cargo: 1690.78
2. 交易4: Cargo: 500.0
3. 交易5: Cargo: 19.0
4. 交易7: Cargo: 700.0
5. 交易12: Cargo: 350.0
6. 交易13: Cargo: 520.0
7. 交易14: Cargo: 300.0
8. 交易15: Cargo: 1400.0
9. 交易17: Cargo: 2100.0
10. 交易20: Cargo: 299.0
Step 4: 确保金额格式转换正确（处理千分位逗号）。
- 明细中所有金额均为标准数字格式，无需转换。
- 计算过程：数值2 = 1690.78 + 500.0 + 19.0 + 700.0 + 350.0 + 520.0 + 300.0 + 1400.0 + 2100.0 + 299.0 = 7878.78。
- 统计验证：明细中有效Cargos交易数为10笔，与列出的10笔一致。
【校验规则执行】
比较数值1（9828.78）与数值2（7878.78）是否相等。
- 比较结果：9828.78 ≠ 7878.78，两者不相等。
【决策结果与hit判定】
根据规则决策结果：如果不相等，输出不一致（异常）。
因此，输出：不一致。
根据hit值判断逻辑：输出'不一致' → hit=true（违规/命中）。
故判定：hit=true。

**补充说明**: 审计发现：明细交易中Cargos金额总和（7878.78）与Comportamiento中报告的Cargos总金额（9828.78）不一致，差额为1950.00。规则要求严格比对，故判定为违规。；已根据 evidence 结尾的明确结论自动修正 hit 值为 True

---

### 5. 明细交易金额校验_单笔金额

**规则ID**: `MSTAR_BBVA_DTL_AMT_SINGLE`

**命中状态**: ✅ **命中** (违规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_AMT_SINGLE
规则名称: 明细交易金额校验_单笔金额

执行步骤与结果：

Step 1: 保持交易列表的原始顺序。已按提供的20笔交易顺序处理。

Step 2: 确定初始锚点(Balance_1)。
- 检查第一行交易（索引1）：有 'Operacion' 值 1226.31。
- 因此，将 Balance_1 设为 1226.31。计算起点从下一行（索引2）开始。

Step 3 & 4: 寻找下一个锚点并进行区间核算。

轮次1:
- Balance_1 = 1226.31 (来自索引1的 Operacion)。
- 向下遍历，找到下一个有 'Operacion' 或 'SALDO OPERACIÓN' 的行：索引2的 Operacion 为 2226.31，记为 Balance_2。
- 核算区间：从索引2（不含）到索引2（含）？根据规则，区间是 Balance_1 (不含) 到 Balance_2 (含)。Balance_1来自索引1，所以区间应从索引2开始。但Balance_2也在索引2，这意味着区间内没有交易（因为起点和终点是同一行？）。让我们严格遵循规则：
   - Balance_1 (1226.31) 来自索引1。
   - Balance_2 (2226.31) 来自索引2。
   - 区间：索引1（不含）到索引2（含） => 即仅包含索引2这一行。
- 累加区间内的 Cargos 和 Abonos：索引2的 Cargo 为“无”，Abono 为 1000.0。
- 计算：result = Balance_1 - Sum(Cargos) + Sum(Abonos) - Balance_2 = 1226.31 - 0 + 1000.0 - 2226.31 = (1226.31 + 1000.0) - 2226.31 = 2226.31 - 2226.31 = 0.0。
- 结果：result = 0.0。

轮次2:
- 新的 Balance_1 = 2226.31 (来自索引2的 Operacion)。
- 向下遍历，找到下一个有 'Operacion' 的行：索引3的 Operacion 为 535.53，记为 Balance_2。
- 区间：索引2（不含）到索引3（含） => 仅包含索引3这一行。
- 累加：索引3的 Cargo 为 1690.78，Abono 为“无”。
- 计算：result = 2226.31 - 1690.78 + 0 - 535.53 = (2226.31 - 1690.78) - 535.53 = 535.53 - 535.53 = 0.0。
- 结果：result = 0.0。

轮次3:
- 新的 Balance_1 = 535.53 (来自索引3的 Operacion)。
- 向下遍历，找到下一个有 'Operacion' 的行：索引4的 Operacion 为 35.53，记为 Balance_2。
- 区间：索引3（不含）到索引4（含） => 仅包含索引4这一行。
- 累加：索引4的 Cargo 为 500.0，Abono 为“无”。
- 计算：result = 535.53 - 500.0 + 0 - 35.53 = (535.53 - 500.0) - 35.53 = 35.53 - 35.53 = 0.0。
- 结果：result = 0.0。

轮次4:
- 新的 Balance_1 = 35.53 (来自索引4的 Operacion)。
- 向下遍历，找到下一个有 'Operacion' 的行：索引5的 Operacion 为 16.53，记为 Balance_2。
- 区间：索引4（不含）到索引5（含） => 仅包含索引5这一行。
- 累加：索引5的 Cargo 为 19.0，Abono 为“无”。
- 计算：result = 35.53 - 19.0 + 0 - 16.53 = (35.53 - 19.0) - 16.53 = 16.53 - 16.53 = 0.0。
- 结果：result = 0.0。

轮次5:
- 新的 Balance_1 = 16.53 (来自索引5的 Operacion)。
- 向下遍历，找到下一个有 'Operacion' 的行：索引7的 Operacion 为 16.53，记为 Balance_2。
- 区间：索引5（不含）到索引7（含） => 包含索引6和索引7。
- 累加：
  索引6: Cargo 无，Abono 700.0。
  索引7: Cargo 700.0，Abono 无。
  Sum(Cargos) = 700.0, Sum(Abonos) = 700.0。
- 计算：result = 16.53 - 700.0 + 700.0 - 16.53 = (16.53 + 0) - 16.53 = 0.0。
- 结果：result = 0.0。

轮次6:
- 新的 Balance_1 = 16.53 (来自索引7的 Operacion)。
- 向下遍历，找到下一个有 'Operacion' 的行：索引8的 Operacion 为 16016.53，记为 Balance_2。
- 区间：索引7（不含）到索引8（含） => 仅包含索引8这一行。
- 累加：索引8的 Cargo 为“无”，Abono 为 16000.0。
- 计算：result = 16.53 - 0 + 16000.0 - 16016.53 = (16.53 + 16000.0) - 16016.53 = 16016.53 - 16016.53 = 0.0。
- 结果：result = 0.0。

轮次7:
- 新的 Balance_1 = 16016.53 (来自索引8的 Operacion)。
- 向下遍历，找到下一个有 'Operacion' 的行：索引11的 Operacion 为 4990.22，记为 Balance_2。
- 区间：索引8（不含）到索引11（含） => 包含索引9, 10, 11。
- 累加：
  索引9: Cargo 无，Abono 250.0。
  索引10: Cargo 无，Abono 1700.0。
  索引11: Cargo 无，Abono 2100.0。
  Sum(Cargos) = 0, Sum(Abonos) = 250.0 + 1700.0 + 2100.0 = 4050.0。
- 计算：result = 16016.53 - 0 + 4050.0 - 4990.22 = (16016.53 + 4050.0) - 4990.22 = 20066.53 - 4990.22 = 15076.31。
- 结果：result = 15076.31，不为0。

发现不一致，停止后续轮次计算。

校验规则：记录每一个轮次中步骤4中的result值，是否所有的result都为0。
决策结果：如果任意一个轮次中result值不为0，输出不一致（异常）。

结论：在轮次7中，result = 15076.31 ≠ 0，因此明细交易金额校验不一致。

hit值判断：根据决策结果，存在不一致，故 hit = true。

**补充说明**: 在轮次7的核算中，发现余额计算不一致。区间内（索引9至11）的Abonos总和为4050.0，但根据公式 Balance_1 (16016.53) + Sum(Abonos) (4050.0) 应等于 Balance_2 (4990.22) + Sum(Cargos) (0)，即 20066.53 应等于 4990.22，显然不等。这表明在索引9至11之间可能存在未列出的Cargos交易，或者Operacion值（4990.22）有误。根据规则，只要有一个轮次result不为0，即判定为不一致。；已根据 evidence 结尾的明确结论自动修正 hit 值为 True

---

### 6. 交易日期校验_日期一致性

**规则ID**: `MSTAR_BBVA_DATE_CHK_CONS`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DATE_CHK_CONS
规则名称: 交易日期校验_日期一致性

执行步骤：
(Step 1) 获取步骤1中“content”的值中模糊匹配包含“Periodo”的信息。
执行结果：在“=== Periodo 信息 ===”和“=== 客户信息 ===”中均找到“Periodo: DEL 13/03/2025 AL 12/04/2025”。因此，步骤1的日期区间为 [13/03/2025, 12/04/2025]。

(Step 2) 取Detalle de Movimientos Realizados中所有的OPER和LIQ，并计算出其中最小日期和最大日期，分别记为min_date和max_date。
执行结果：
- 列出所有交易的OPER和LIQ日期（共20笔）：
  1. Oper:15/MAR, Liq:18/MAR
  2. Oper:18/MAR, Liq:18/MAR
  3. Oper:20/MAR, Liq:19/MAR
  4. Oper:21/MAR, Liq:21/MAR
  5. Oper:24/MAR, Liq:22/MAR
  6. Oper:02/ABR, Liq:02/ABR
  7. Oper:02/ABR, Liq:02/ABR
  8. Oper:04/ABR, Liq:04/ABR
  9. Oper:06/ABR, Liq:07/ABR
  10. Oper:06/ABR, Liq:07/ABR
  11. Oper:06/ABR, Liq:07/ABR
  12. Oper:07/ABR, Liq:04/ABR
  13. Oper:04/ABR, Liq:04/ABR
  14. Oper:07/ABR, Liq:07/ABR
  15. Oper:07/ABR, Liq:07/ABR
  16. Oper:07/ABR, Liq:07/ABR
  17. Oper:07/ABR, Liq:07/ABR
  18. Oper:08/ABR, Liq:08/ABR
  19. Oper:08/ABR, Liq:08/ABR
  20. Oper:08/ABR, Liq:08/ABR
- 所有日期均属于2025年。
- 最小日期（min_date）：在OPER和LIQ中，最早的日期是“15/MAR”（即2025年3月15日）。
- 最大日期（max_date）：在OPER和LIQ中，最晚的日期是“08/ABR”（即2025年4月8日）。

(Step 3) 校验规则：步骤2中的min_date和max_date是否在步骤1的日期区间范围内？
执行结果：
- 步骤1的日期区间：[13/03/2025, 12/04/2025]
- 步骤2的min_date：15/03/2025。该日期（15/03/2025）晚于或等于区间起始日（13/03/2025），且早于或等于区间结束日（12/04/2025），因此在区间范围内。
- 步骤2的max_date：08/04/2025。该日期（08/04/2025）晚于或等于区间起始日（13/03/2025），且早于或等于区间结束日（12/04/2025），因此在区间范围内。

(Step 4) 决策结果：由于min_date（15/03/2025）和max_date（08/04/2025）均在步骤1的日期区间[13/03/2025, 12/04/2025]范围内，因此输出“一致（无异常）”。

结论：根据校验规则，交易明细中的日期范围完全落在账单声明的周期内，未发现异常。

hit值判定理由：根据决策结果“一致（无异常）”，规则未命中，因此 hit=false。

**补充说明**: 所有日期均基于提供的2025年上下文进行解析。规则仅校验日期范围是否在区间内，不要求完全覆盖整个区间。经核查，所有交易的OPER和LIQ日期均在‘DEL 13/03/2025 AL 12/04/2025’之内。

---

### 7. 交易明细分析_高风险职业

**规则ID**: `MSTAR_BBVA_DTL_ANAL_RISK_OCC`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 步骤1执行结果：已从'Detalle de Movimientos Realizados'中提取所有20笔交易的'DESCRIPCION'（描述）字段。
步骤2执行结果：已将20条描述翻译为中文。翻译结果如下：
1. 向第三方账户支付 BNET 1526485652 tenkiu
2. SPEI 接收 SANTANDER 2626043 转账给 LUIS ALBERTO F 00014180606300288968 2025031840014BMOV0020426172780 ORLANDO GIOVANNI NAVA FERNANDEZ
3. MI ATT A APP PS RFC: CNM 980114PI2 12:22 AUT: 449977
4. 自动取款机取款 MAR21 11:42 BBVA A347 凭证号:5098
5. Google Call of Duty M RFC: 16:43 AUT: 987126
6. 向第三方账户支付 BNET 1512099106 cel abril 25
7. 向第三方账户支付 BNET 1512099106 Lore
8. 工资/养老金支付 BANCOMER SA DE CV GFB
9. SPEI 发送至 AZTECA 0903250Farmacia 00004027665873176359 MBAN01002504070099171983 Ofelia Alejandra Jimenez
10. 自动取款机取款 ABR06 18:59 BBVA A350 凭证号:3399
11. 向第三方账户支付 BNET 1512099106 fumigacion
12. MERPAGO*CALZADO RFC: MAG 2105031W3 20:38 AUT: 565479
13. MERPAGO*CREMERIA RFC: MAG 2105031W3 21:08 AUT: 086359
14. SPEI 发送至 AZTECA 0903250Gabriel 00004831121200462522 MBAN01002504070052292416 Bruno Gabriel Garcia Solares
15. 向第三方账户支付 BNET 1512099106 Lore
16. 向第三方账户支付 BNET 1512099106 devoluc
17. SPEI 发送至 Mercado Pago 0903250Fumilgacion y lavado 00722969010507777070 MBAN01002504070053798296 Fernando Zavala
18. 向第三方账户支付 BNET 1512099106 dev
19. SPEI 接收 TP 1612800Prestamo 00646180501400000001 20250408175612A1612800CEP CREDITO365 SAPI DE CV
20. MSFT STORE RFC: MME 910620Q85 19:28 AUT: 837070

校验规则执行结果：逐条检查上述20条中文描述，判断是否命中以下任意关键词：
- 现金密集型业务；
- 小型零售商和街头摊贩（如露天市场摊贩）；
- 夜总会；
- 酒吧；
- 娱乐场所经营者；
- 灰色；
- 非法行业关联者；
- 未注册或非正式的安保服务提供商；
- 涉嫌贷款翻转或文件造假的汽车贷款经纪人或中介；
- 可能与贩毒或有组织犯罪相关的幌子企业（如虚假奢侈品转售店、空壳运输公司）；
- 欺诈高发行业；
- 不受监管的汽车经销商或中介，尤其是推广 “零首付” 优惠的或收入不规律或无法核实的自雇人士；
- 在汽车金融行业工作的个人；
- 独立或未注册的汽车维修店员工。

检查结论：所有20条中文描述均未包含上述任何关键词。描述内容主要为：第三方支付、工资入账、SPEI转账、自动取款机取款、游戏/软件消费、商店消费（鞋店、乳品店、微软商店）、支付给特定个人（如Farmacia, Gabriel, Fernando Zavala）以及一笔小额贷款入账。这些描述未指向任何规则定义的高风险职业或业务类型。

决策结果：根据规则，全部描述均未命中关键词，输出“正常”。

最终判定：hit=false（规则未命中，交易描述合规）。

**补充说明**: 已严格按照判断逻辑、校验规则和决策结果执行。所有交易描述已翻译并检查，未发现与高风险职业相关的关键词。

---

### 8. 交易明细分析_快进快出

**规则ID**: `MSTAR_BBVA_DTL_ANAL_FAST_IO`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_ANAL_FAST_IO
规则名称: 交易明细分析_快进快出

执行步骤与结果：
步骤1：已取Detalle de Movimientos Realizados中所有20条记录，并按OPER日期升序排序（数据已按此顺序提供）。
步骤2：统计所有记录中ABONOS取值不为空的总记录数。根据数据中提供的参考值，'有效 Abonos (入账) 的交易数'为10。因此，total_cargo_cnt = 10。
步骤3-6：开始逐轮次查找并计算。

轮次分析：
1. 起始行（第1条）：ABONOS1 = 1200.0， OPER1 = 15/MAR。向下查找CARGOS列值为1200.0的记录。未找到。本轮无匹配，result不计数。
2. 起始行（第2条）：ABONOS1 = 1000.0， OPER1 = 18/MAR。向下查找CARGOS列值为1000.0的记录。未找到。本轮无匹配，result不计数。
3. 起始行（第6条）：ABONOS1 = 700.0， OPER1 = 02/ABR。向下查找CARGOS列值为700.0的记录。找到第7条，CARGOS = 700.0， OPER2 = 02/ABR。OPER1与OPER2为同一天，间隔天数result = 0。result <= 1， result_total计数加1。
4. 起始行（第8条）：ABONOS1 = 16000.0， OPER1 = 04/ABR。向下查找CARGOS列值为16000.0的记录。未找到。本轮无匹配，result不计数。
5. 起始行（第9条）：ABONOS1 = 250.0， OPER1 = 06/ABR。向下查找CARGOS列值为250.0的记录。未找到。本轮无匹配，result不计数。
6. 起始行（第10条）：ABONOS1 = 1700.0， OPER1 = 06/ABR。向下查找CARGOS列值为1700.0的记录。未找到。本轮无匹配，result不计数。
7. 起始行（第11条）：ABONOS1 = 2100.0， OPER1 = 06/ABR。向下查找CARGOS列值为2100.0的记录。找到第17条，CARGOS = 2100.0， OPER2 = 07/ABR。OPER1 (06/ABR) 与 OPER2 (07/ABR) 间隔天数result = 1。result <= 1， result_total计数加1。
8. 起始行（第16条）：ABONOS1 = 600.0， OPER1 = 07/ABR。向下查找CARGOS列值为600.0的记录。未找到。本轮无匹配，result不计数。
9. 起始行（第18条）：ABONOS1 = 800.0， OPER1 = 08/ABR。向下查找CARGOS列值为800.0的记录。未找到。本轮无匹配，result不计数。
10. 起始行（第19条）：ABONOS1 = 0.01， OPER1 = 08/ABR。向下查找CARGOS列值为0.01的记录。未找到。本轮无匹配，result不计数。

校验规则执行：
1. 记录每个轮次中result值。符合条件（result <= 1）的轮次为：轮次3 (result=0) 和 轮次7 (result=1)。因此，result_total = 2。
2. 计算ratio = result_total / total_cargo_cnt = 2 / 10 = 0.2。

决策结果：
ratio = 0.2， 小于等于0.8。因此，输出“未命中快进快出（无异常）”。

结论：
根据规则逻辑，ratio <= 0.8，判定为未命中异常。

**补充说明**: 已严格按照规则定义的判断逻辑、校验规则和决策结果执行。所有ABONOS不为空的交易均已作为起始行处理，并查找了对应的CARGOS交易。计算过程清晰，结果明确。

---

### 9. 交易明细分析_异常备注

**规则ID**: `MSTAR_BBVA_DTL_ANAL_ABN_REM`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_ANAL_ABN_REM
规则名称: 交易明细分析_异常备注

执行步骤（严格按照判断逻辑）：
步骤1：获取解析后Detalle de Movimientos Realizados部分的description对应的所有的值。
执行结果：已从提供的20笔交易明细中提取所有‘描述’字段的值，共20个。

校验规则（严格按照校验规则）：
判断DESCRIPCION对应的所有的值是否包含以下任意关键词：Apuesta，médico / médic，juego。
执行过程：
1. 逐条检查20笔交易的描述字段。
2. 未发现任何描述包含关键词“Apuesta”。
3. 未发现任何描述包含关键词“médico”或“médic”。
4. 未发现任何描述包含关键词“juego”。

决策结果（严格按照决策结果）：
命中任意一个关键词，输出异常；全部都没命中，输出正常。
执行结果：所有20条描述均未命中指定的任意一个关键词。

结论：根据规则逻辑，未发现异常备注。
判定理由：所有交易描述均不包含规则指定的关键词（Apuesta, médico / médic, juego），因此规则未命中（hit=false）。

**补充说明**: 已完整检查所有20笔交易的描述字段，未发现违规关键词。

---

### 10. 交易时间校验_特殊时间段交易

**规则ID**: `MSTAR_BBVA_TIME_CHK_SPECIAL`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_TIME_CHK_SPECIAL
规则名称: 交易时间校验_特殊时间段交易

执行步骤：
步骤1：遍历‘Detalle de Movimientos Realizados’中的20条记录，从‘描述’字段提取时间。
- 记录1: "PAGO CUENTA DE TERCERO BNET 1526485652 tenkiu" -> 无时间，跳过。
- 记录2: "SPEI RECIBIDOSANTANDER 2626043TRANSFERENCIA A LUIS ALBERTO F 00014180606300288968 2025031840014BMOV0020426172780 ORLANDO GIOVANNI NAVA FERNANDEZ" -> 无时间，跳过。
- 记录3: "MI ATT A APP PS RFC: CNM 980114PI2 12:22 AUT: 449977" -> 提取时间: 12:22。
- 记录4: "RETIRO CAJERO AUTOMATICO MAR21 11:42 BBVA A347 FOLIO:5098" -> 提取时间: 11:42。
- 记录5: "Google Call of Duty M RFC: 16:43 AUT: 987126" -> 提取时间: 16:43。
- 记录6: "PAGO CUENTA DE TERCERO BNET 1512099106 cel abril 25" -> 无时间，跳过。
- 记录7: "PAGO CUENTA DE TERCERO BNET 1512099106 Lore" -> 无时间，跳过。
- 记录8: "PAGO DE NOMINA PENSIONES BANCOMER SA DE CV GFB" -> 无时间，跳过。
- 记录9: "SPEI ENVIADO AZTECA 0903250Farmacia 00004027665873176359 MBAN01002504070099171983 Ofelia Alejandra Jimenez" -> 无时间，跳过。
- 记录10: "RETIRO CAJERO AUTOMATICO ABR06 18:59 BBVA A350 FOLIO:3399" -> 提取时间: 18:59。
- 记录11: "PAGO CUENTA DE TERCERO BNET 1512099106 fumigacion" -> 无时间，跳过。
- 记录12: "MERPAGO*CALZADO RFC: MAG 2105031W3 20:38 AUT: 565479" -> 提取时间: 20:38。
- 记录13: "MERPAGO*CREMERIA RFC: MAG 2105031W3 21:08 AUT: 086359" -> 提取时间: 21:08。
- 记录14: "SPEI ENVIADO AZTECA 0903250Gabriel 00004831121200462522 MBAN01002504070052292416 Bruno Gabriel Garcia Solares" -> 无时间，跳过。
- 记录15: "PAGO CUENTA DE TERCERO BNET 1512099106 Lore" -> 无时间，跳过。
- 记录16: "PAGO CUENTA DE TERCERO BNET 1512099106 devoluc" -> 无时间，跳过。
- 记录17: "SPEI ENVIADO Mercado Pago 0903250Fumilgacion y lavado 00722969010507777070 MBAN01002504070053798296 Fernando Zavala" -> 无时间，跳过。
- 记录18: "PAGO CUENTA DE TERCERO BNET 1512099106 dev" -> 无时间，跳过。
- 记录19: "SPEI RECIBIDOSTP 1612800Prestamo 00646180501400000001 20250408175612A1612800CEP CREDITO365 SAPI DE CV" -> 无时间，跳过。
- 记录20: "MSFT STORE RFC: MME 910620Q85 19:28 AUT: 837070" -> 提取时间: 19:28。
步骤2：将提取到的时间放入集合：{'12:22', '11:42', '16:43', '18:59', '20:38', '21:08', '19:28'}。
步骤3：统计集合中处于02:00至05:00（含两端）的时间数量。
- 检查每个时间：
  * 12:22 -> 不在02:00-05:00区间。
  * 11:42 -> 不在02:00-05:00区间。
  * 16:43 -> 不在02:00-05:00区间。
  * 18:59 -> 不在02:00-05:00区间。
  * 20:38 -> 不在02:00-05:00区间。
  * 21:08 -> 不在02:00-05:00区间。
  * 19:28 -> 不在02:00-05:00区间。
- 统计结果：count = 0。

校验规则：判断 count 是否大于 10。
- 计算：count = 0， 0 > 10 为假。

决策结果：根据规则，如果 count <= 10，输出“正常”。
- 结论：交易时间正常。

最终判定：规则未命中，hit=false。

**补充说明**: 已严格按照判断逻辑、校验规则和决策结果执行。所有提取到的时间均不在02:00-05:00区间内，count为0，未超过阈值10，因此判定为正常。

---
