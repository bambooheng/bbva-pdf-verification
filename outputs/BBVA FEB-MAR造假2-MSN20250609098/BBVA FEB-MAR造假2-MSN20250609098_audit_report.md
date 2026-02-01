# BBVA 银行流水审计报告

**生成时间**: 2026-02-01 10:39:06

## 元数据

- **account_number**: 1512353873
- **total_pages**: 8
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

执行步骤（严格按照判断逻辑）：
(Step 1) 从 'Comportamiento' 表格中提取 'Depósitos / Abonos (+)'（入账）对应的总笔数（Total Movimientos Abonos）。
- 执行结果：在提供的 'Comportamiento' 部分，'Depósitos / Abonos (+): 7  18,552.00'，因此数值1（来自Comportamiento的总笔数）为 7。

(Step 2) 遍历 'Detalle de Movimientos Realizados'或raw_transaction_data（交易明细）部分的所有交易行。
- 执行结果：明细部分总共有 28 行交易记录。

(Step 3) [关键过滤] 仅统计 'Abonos' 列有有效数值（非空且不为0）的行。如果某行只有 'Cargo' 列有值，必须忽略。
- 执行结果：根据明细数据，逐行检查 'ABONOS' 字段。
- 符合条件的交易明细（Abonos列有有效数值）如下（共17笔）：
  1. 行7: ABONOS:2.0
  2. 行8: ABONOS:600.0
  3. 行10: ABONOS:400.0
  4. 行13: ABONOS:1000.0
  5. 行15: ABONOS:200.0
  6. 行17: ABONOS:199.0
  7. 行18: ABONOS:16000.0
  8. 行19: ABONOS:2100.0
  9. 行20: ABONOS:454.0
  10. 行21: ABONOS:350.0
  11. 行22: ABONOS:275.0
  12. 行23: ABONOS:120.0
  13. 行24: ABONOS:221.0
  14. 行25: ABONOS:65.0
  15. 行26: ABONOS:100.0
  16. 行27: ABONOS:1000.0
  17. 行28: ABONOS:808.0

(Step 4) 计算符合条件的交易总行数。
- 执行结果：统计上述列表，符合条件的交易总行数（数值2，来自明细统计）为 17。

校验规则（严格按照校验规则）：
比较1和2是否相等。
- 数值1（Comportamiento 总笔数）: 7
- 数值2（明细统计 Abonos 笔数）: 17
- 比较结果：7 ≠ 17，两者不相等。

决策结果（严格按照决策结果）：
如果不相等，输出不一致（异常）。
- 最终判定：不一致（异常）。

hit值判定（严格按照逻辑）：
由于两个数值不相等，输出“不一致”，因此 hit=true（违规/命中）。

补充说明：
1. 数据中提供的参考值 '其中包含有效 Abonos (入账) 的交易数: 17' 与手动统计结果一致，确认了数值2的准确性。
2. 规则仅关注笔数是否一致，不涉及金额或其他指标。尽管明细中存在余额连续性检查失败的情况，但这不影响当前笔数校验规则的判定。

**补充说明**: Comportamiento 中记录的 Abonos 交易笔数（7笔）与交易明细中实际统计的有效 Abonos 交易笔数（17笔）存在显著差异，判定为不一致。规则执行严格遵循了定义的步骤和逻辑。

---

### 2. 明细交易笔数校验_出账笔数

**规则ID**: `MSTAR_BBVA_DTL_CNT_CARGOS`

**命中状态**: ✅ **命中** (违规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_CNT_CARGOS
规则名称: 明细交易笔数校验_出账笔数

执行步骤（严格按照判断逻辑）：
(Step 1) 从 'Comportamiento' 表格中提取 'Retiros / Cargos (-)'（出账）对应的总笔数（Total Movimientos Cargos）。
- 执行结果：在 'Comportamiento' 部分找到 'Retiros / Cargos (-): 21  12,229.31'，在 'total_movimientos' 部分找到 'total_movimientos_cargos: 21'。两者一致，确认数值1为 21。
(Step 2) 遍历 'Detalle de Movimientos Realizados'（交易明细）部分的所有交易行。
- 执行结果：明细部分总共有 28 行交易记录。
(Step 3) [关键过滤] 仅统计 'Cargos' 列有有效数值（非空且不为0）的行。如果某行只有 'Abono' 列有值，必须忽略。
- 执行结果：逐行检查明细，筛选出 'Cargos' 列有数值（非'无'）的行。符合条件的交易明细如下（共11笔）：
1. CARGOS:222.0
2. CARGOS:800.0
3. CARGOS:300.0
4. CARGOS:122.4
5. CARGOS:299.0
6. CARGOS:874.0
9. CARGOS:600.0
11. CARGOS:2268.91
12. CARGOS:400.0
14. CARGOS:1000.0
16. CARGOS:1.0
(Step 4) 计算符合条件的交易总行数。
- 执行结果：统计上述列表，符合条件的交易总行数为 11。此数值与数据中提供的参考值'其中包含有效 Cargos (出账) 的交易数: 11'一致。确认数值2为 11。

校验规则（严格按照校验规则）：
比较1和2是否相等。
- 数值1 (来自Comportamiento/total_movimientos): 21
- 数值2 (来自明细统计): 11
- 比较结果：21 ≠ 11，两者不相等。

决策结果（严格按照决策结果）：
如果不相等，输出不一致（异常）。

结论：明细中统计的有效出账交易笔数（11笔）与总览中报告的总出账交易笔数（21笔）不一致。

hit值判定理由：根据规则，两个数值不相等，输出“不一致”，因此 hit=true。

**补充说明**: 数据中提供的参考值'其中包含有效 Cargos (出账) 的交易数: 11'与手动统计结果一致，确认了数值2的准确性。数值1在文档中多处（Comportamiento和total_movimientos）均明确为21，确认了数值1的准确性。

---

### 3. 明细交易金额校验_入账金额

**规则ID**: `MSTAR_BBVA_DTL_AMT_ABONOS`

**命中状态**: ✅ **命中** (违规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_AMT_ABONOS
规则名称: 明细交易金额校验_入账金额

执行步骤（严格按照判断逻辑）：
(Step 1) 从 'Comportamiento' 表格中提取 'Depósitos / Abonos (+)'（入账）对应的总金额。
执行结果：从数据中提取到 'Depósitos / Abonos (+): 7  18,552.00'。数值1 = 18552.00。
(Step 2) 遍历 'Detalle de Movimientos Realizados' 或raw_transaction_data部分。
执行结果：已遍历提供的28笔交易明细。
(Step 3) [关键过滤] 累加所有 'Abonos' 列的数值。忽略 'Cargo' 列的数值。
执行结果：根据明细，逐笔累加所有非“无”的Abonos金额。明细如下（共17笔）：
1. 无
2. 无
3. 无
4. 无
5. 无
6. 无
7. 2.0
8. 600.0
9. 无
10. 400.0
11. 无
12. 无
13. 1000.0
14. 无
15. 200.0
16. 无
17. 199.0
18. 16000.0
19. 2100.0
20. 454.0
21. 350.0
22. 275.0
23. 120.0
24. 221.0
25. 65.0
26. 100.0
27. 1000.0
28. 808.0
(Step 4) 确保金额格式转换正确（处理千分位逗号）。
执行结果：明细中金额均为数字格式，无需转换。
求和计算：2.0 + 600.0 + 400.0 + 1000.0 + 200.0 + 199.0 + 16000.0 + 2100.0 + 454.0 + 350.0 + 275.0 + 120.0 + 221.0 + 65.0 + 100.0 + 1000.0 + 808.0 = 21894.0。数值2 = 21894.0。

校验规则（严格按照校验规则）：比较数值1和数值2是否相等。
比较结果：数值1 (18552.00) 不等于 数值2 (21894.00)。

决策结果（严格按照决策结果）：两个数值不相等，输出“不一致”（异常）。

最终判定：根据规则，hit值在“不一致”时为true。因此，hit=true。

**补充说明**: 系统提供的参考值'有效 Abonos 交易数: 17'与手动统计的Abonos交易笔数一致。'Comportamiento'中的入账总金额(18552.00)与明细累加结果(21894.00)存在显著差异。差异金额为3342.00。此规则仅关注入账总金额是否一致，不涉及其他异常。

---

### 4. 明细交易金额校验_出账金额

**规则ID**: `MSTAR_BBVA_DTL_AMT_CARGOS`

**命中状态**: ✅ **命中** (违规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_AMT_CARGOS
规则名称: 明细交易金额校验_出账金额

执行步骤与结果：
(Step 1) 从 'Comportamiento' 表格中提取 'Retiros / Cargos (-)'（出账）对应的总金额。
- 提取结果：数值1 = 12,229.31

(Step 2) 遍历 'Detalle de Movimientos Realizados' 或raw_transaction_data部分。
- 已遍历提供的28条明细交易记录。

(Step 3) [关键过滤] 累加所有 'Cargos' 列的数值。忽略 'Abono' 列的数值。
- 根据数据说明，明细中包含有效 Cargos (出账) 的交易数为 11 笔。
- 按原始顺序提取并累加所有非“无”的 Cargos 金额：
  1. 222.0
  2. 800.0
  3. 300.0
  4. 122.4
  5. 299.0
  6. 874.0
  7. 600.0 (行9)
  8. 2268.91
  9. 400.0 (行12)
  10. 1000.0 (行14)
  11. 1.0 (行16)
- 求和计算：222.0 + 800.0 + 300.0 + 122.4 + 299.0 + 874.0 + 600.0 + 2268.91 + 400.0 + 1000.0 + 1.0 = 6887.31
- 提取结果：数值2 = 6,887.31

(Step 4) 确保金额格式转换正确（处理千分位逗号）。
- 数值1 (12,229.31) 已转换为 12229.31。
- 数值2 (6,887.31) 已转换为 6887.31。

校验规则：比较1和2是否相等。
- 数值1 (12229.31) 与 数值2 (6887.31) 不相等。

决策结果：如果不相等，输出不一致（异常）。
- 结论：明细交易中累加的 Cargos 总额 (6,887.31) 与 Comportamiento 中报告的 Cargos 总额 (12,229.31) 不一致。

hit 值判定：由于两个数值不相等，根据规则，输出“不一致”，因此 hit=true。

**补充说明**: 明细中Cargos交易笔数（11笔）与Comportamiento中报告的Cargos交易笔数（21笔）存在显著差异，这解释了金额不一致的原因。但本规则仅校验金额，因此基于金额不相等判定为命中。

---

### 5. 明细交易金额校验_单笔金额

**规则ID**: `MSTAR_BBVA_DTL_AMT_SINGLE`

**命中状态**: ✅ **命中** (违规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_AMT_SINGLE
规则名称: 明细交易金额校验_单笔金额

执行步骤与结果：
1. 保持交易列表原始顺序：已按提供的28笔交易原始顺序处理。
2. 确定初始锚点(Balance_1)：第1行交易有'OPERACIÓN'值4662.42，将其记为Balance_1。计算起点从第2行开始。
3. 寻找下一个锚点(Balance_2)并迭代核算：按照规则逻辑，遍历列表，找到下一个有'OPERACIÓN'或'SALDO OPERACIÓN'的行作为Balance_2，然后计算区间内Cargos和Abonos的累加和，并验证公式 result = Balance_1 - Sum(Cargos) + Sum(Abonos) - Balance_2 是否为0。

详细核算轮次（共13轮）：
- 轮次1 (行1->3): Balance_1=4662.42, Balance_2=3562.42, Sum(Cargos)=222.0+800.0=1022.0, Sum(Abonos)=0, result=4662.42-1022.0+0-3562.42=0.0 -> 通过。
- 轮次2 (行3->6): Balance_1=3562.42, Balance_2=2267.02, Sum(Cargos)=300.0+122.4+299.0+874.0=1595.4, Sum(Abonos)=0, result=3562.42-1595.4+0-2267.02=0.0 -> 通过。
- 轮次3 (行6->8): Balance_1=2267.02, Balance_2=2869.02, Sum(Cargos)=0, Sum(Abonos)=2.0+600.0=602.0, result=2267.02-0+602.0-2869.02=0.0 -> 通过。
- 轮次4 (行8->11): Balance_1=2869.02, Balance_2=400.11, Sum(Cargos)=600.0+2268.91=2868.91, Sum(Abonos)=400.0, result=2869.02-2868.91+400.0-400.11=0.0 -> 通过。
- 轮次5 (行11->12): Balance_1=400.11, Balance_2=0.11, Sum(Cargos)=400.0, Sum(Abonos)=0, result=400.11-400.0+0-0.11=0.0 -> 通过。
- 轮次6 (行12->14): Balance_1=0.11, Balance_2=0.11, Sum(Cargos)=1000.0, Sum(Abonos)=1000.0, result=0.11-1000.0+1000.0-0.11=0.0 -> 通过。
- 轮次7 (行14->15): Balance_1=0.11, Balance_2=200.11, Sum(Cargos)=0, Sum(Abonos)=200.0, result=0.11-0+200.0-200.11=0.0 -> 通过。
- 轮次8 (行15->17): Balance_1=200.11, Balance_2=0.11, Sum(Cargos)=1.0, Sum(Abonos)=199.0, result=200.11-1.0+199.0-0.11=398.0 -> 不通过。
- 轮次9 (行17->19): Balance_1=0.11, Balance_2=2719.31, Sum(Cargos)=0, Sum(Abonos)=16000.0+2100.0=18100.0, result=0.11-0+18100.0-2719.31=15380.8 -> 不通过。
- 轮次10 (行19->20): Balance_1=2719.31, Balance_2=2265.31, Sum(Cargos)=0, Sum(Abonos)=454.0, result=2719.31-0+454.0-2265.31=908.0 -> 不通过。
- 轮次11 (行20->25): Balance_1=2265.31, Balance_2=1934.31, Sum(Cargos)=0, Sum(Abonos)=350.0+275.0+120.0+221.0+65.0=1031.0, result=2265.31-0+1031.0-1934.31=1362.0 -> 不通过。
- 轮次12 (行25->27): Balance_1=1934.31, Balance_2=834.31, Sum(Cargos)=0, Sum(Abonos)=100.0+1000.0=1100.0, result=1934.31-0+1100.0-834.31=2200.0 -> 不通过。
- 轮次13 (行27->28): Balance_1=834.31, Balance_2=26.31, Sum(Cargos)=0, Sum(Abonos)=808.0, result=834.31-0+808.0-26.31=1616.0 -> 不通过。

校验规则：检查所有轮次的result值是否为0。
决策结果：由于轮次8、9、10、11、12、13的result值不为0，因此输出不一致（异常）。

结论：存在多个区间的余额连续性校验失败，明细交易金额与记录的余额不匹配。

**补充说明**: 系统提供的内部计算结论（FAIL DETECTED）与手动执行规则逻辑的结果一致，确认存在异常。

---

### 6. 交易日期校验_日期一致性

**规则ID**: `MSTAR_BBVA_DATE_CHK_CONS`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 执行步骤1：从提供的数据中获取模糊匹配包含'Periodo'的信息。找到内容：'Periodo: DEL 13/02/2025 AL 12/03/2025'。解析得到日期区间为：[DEL 13/02/2025, AL 12/03/2025]。
执行步骤2：从'Detalle de Movimientos Realizados'中提取所有交易的OPER和LIQ日期。明细共28笔，交易笔数少于30笔，因此列出所有日期明细如下：
1. Oper:13/FEB, Liq:13/FEB
2. Oper:15/FEB, Liq:17/FEB
3. Oper:15/FEB, Liq:17/FEB
4. Oper:17/FEB, Liq:14/FEB
5. Oper:17/FEB, Liq:14/FEB
6. Oper:17/FEB, Liq:15/FEB
7. Oper:20/FEB, Liq:20/FEB
8. Oper:20/FEB, Liq:20/FEB
9. Oper:21/FEB, Liq:21/FEB
10. Oper:21/FEB, Liq:21/FEB
11. Oper:21/FEB, Liq:20/FEB
12. Oper:22/FEB, Liq:24/FEB
13. Oper:25/FEB, Liq:25/FEB
14. Oper:25/FEB, Liq:25/FEB
15. Oper:27/FEB, Liq:27/FEB
16. Oper:02/MAR, Liq:03/MAR
17. Oper:02/MAR, Liq:03/MAR
18. Oper:04/MAR, Liq:04/MAR
19. Oper:04/MAR, Liq:04/MAR
20. Oper:06/MAR, Liq:05/MAR
21. Oper:07/MAR, Liq:07/MAR
22. Oper:07/MAR, Liq:07/MAR
23. Oper:07/MAR, Liq:07/MAR
24. Oper:07/MAR, Liq:07/MAR
25. Oper:07/MAR, Liq:07/MAR
26. Oper:08/MAR, Liq:10/MAR
27. Oper:08/MAR, Liq:10/MAR
28. Oper:10/MAR, Liq:10/MAR
计算最小日期（min_date）：从所有OPER和LIQ日期中找出最早日期。OPER最早为13/FEB（2025-02-13），LIQ最早为13/FEB（2025-02-13）。因此min_date = 13/FEB/2025。
计算最大日期（max_date）：从所有OPER和LIQ日期中找出最晚日期。OPER最晚为10/MAR（2025-03-10），LIQ最晚为10/MAR（2025-03-10）。因此max_date = 10/MAR/2025。
执行校验规则：判断步骤2中的min_date（13/FEB/2025）和max_date（10/MAR/2025）是否都在步骤1的日期区间[DEL 13/02/2025, AL 12/03/2025]范围内。
比较结果：min_date（13/02/2025）等于区间起始日（13/02/2025），在区间内。max_date（10/03/2025）早于区间结束日（12/03/2025），在区间内。
决策结果：min_date和max_date均在步骤1的日期区间范围内，因此输出“一致（无异常）”。
判定理由：根据规则，只要min_date和max_date在区间内即判定为一致。当前规则仅校验日期一致性，不要求日期完全覆盖整个区间。因此hit=false。

**补充说明**: 规则仅校验交易明细中的最小和最大日期是否在报告声明的Periodo区间内。经核对，明细日期范围[13/FEB/2025, 10/MAR/2025]完全落在[13/02/2025, 12/03/2025]之内，符合规则要求。系统自动进行的余额连续性检查发现多处失败，但这属于其他规则（如金额连续性）的校验范围，根据'严禁跨规则连坐'原则，不影响本日期一致性规则的判定。

---

### 7. 交易明细分析_高风险职业

**规则ID**: `MSTAR_BBVA_DTL_ANAL_RISK_OCC`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 步骤1执行结果：已从'Detalle de Movimientos Realizados'中提取所有28笔交易的'描述'字段。
步骤2执行结果：已将28条描述翻译为中文。翻译后的描述主要涉及：药店消费（FARM SAN PABLO, FARM DEL AHORRO）、ATM取款、餐厅消费（TOKS）、软件商店消费（MSFT STORE）、SPEI转账（接收和发送，涉及个人、公司如ATMX TECNOLOGIA、MERCADO PAGO、DIGITAL DECK SAPI DE CV等）、话费支付（MI ATT A APP PS）、工资入账（PAGO DE NOMINA PENSIONES）、第三方账户支付（PAGO CUENTA DE TERCERO）。
校验规则执行结果：将翻译后的所有描述与规则定义的高风险职业关键词列表逐一比对。关键词列表包括：现金密集型业务；小型零售商和街头摊贩；夜总会；酒吧；娱乐场所经营者；灰色；非法行业关联者；未注册或非正式的安保服务提供商；涉嫌贷款翻转或文件造假的汽车贷款经纪人或中介；可能与贩毒或有组织犯罪相关的幌子企业；欺诈高发行业；不受监管的汽车经销商或中介；收入不规律或无法核实的自雇人士；在汽车金融行业工作的个人；独立或未注册的汽车维修店员工。
比对结论：所有28条翻译后的描述均未包含上述任意关键词。交易描述主要为日常消费、工资、个人间转账及与正规公司的交易，未发现与高风险职业相关的描述。
决策结果：由于未命中任何关键词，输出为“正常”。

**补充说明**: 规则仅检查交易描述（DESCRIPCION）是否包含特定高风险职业关键词。分析基于提供的28条交易描述，未发现匹配项。余额连续性检查失败等其他数据异常不属于本规则校验范围，不影响本规则判定。

---

### 8. 交易明细分析_快进快出

**规则ID**: `MSTAR_BBVA_DTL_ANAL_FAST_IO`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_ANAL_FAST_IO
规则名称: 交易明细分析_快进快出

执行步骤与结果：
步骤1：已取Detalle de Movimientos Realizados中所有28条记录，并按OPER日期升序排序（数据已按此顺序提供）。
步骤2：统计所有记录中ABONOS取值不为空的总记录数。根据数据中提供的参考值‘有效 Abonos (入账) 交易数: 17’，因此 total_cargo_cnt = 17。
步骤3-6：按照规则逻辑，从第一条记录开始，逐一查找ABONOS不为空的行作为起始行，并寻找其最近的下一个CARGOS值与ABONOS1相等的记录，计算OPER日期间隔天数(result)。

具体轮次分析（因总交易笔数28笔，Abonos交易17笔，符合‘少于30笔’的条件，列出所有用于计算的交易明细）：
1. 起始行(第7行): ABONOS1=2.0, OPER1=20/FEB。向下查找CARGOS=2.0的记录，未找到。本轮无匹配，result不计算，不计入result_total。
2. 起始行(第8行): ABONOS1=600.0, OPER1=20/FEB。向下查找CARGOS=600.0的记录，找到第9行，CARGOS=600.0, OPER2=21/FEB。OPER1(20/FEB)与OPER2(21/FEB)间隔天数为1天。result=1 <=1，result_total计数加1。
3. 起始行(第10行): ABONOS1=400.0, OPER1=21/FEB。向下查找CARGOS=400.0的记录，找到第12行，CARGOS=400.0, OPER2=22/FEB。间隔天数为1天。result=1 <=1，result_total计数加1。
4. 起始行(第13行): ABONOS1=1000.0, OPER1=25/FEB。向下查找CARGOS=1000.0的记录，找到第14行，CARGOS=1000.0, OPER2=25/FEB。间隔天数为0天。result=0 <=1，result_total计数加1。
5. 起始行(第15行): ABONOS1=200.0, OPER1=27/FEB。向下查找CARGOS=200.0的记录，未找到。本轮无匹配，不计入。
6. 起始行(第17行): ABONOS1=199.0, OPER1=02/MAR。向下查找CARGOS=199.0的记录，未找到。本轮无匹配，不计入。
7. 起始行(第18行): ABONOS1=16000.0, OPER1=04/MAR。向下查找CARGOS=16000.0的记录，未找到。本轮无匹配，不计入。
8. 起始行(第19行): ABONOS1=2100.0, OPER1=04/MAR。向下查找CARGOS=2100.0的记录，未找到。本轮无匹配，不计入。
9. 起始行(第20行): ABONOS1=454.0, OPER1=06/MAR。向下查找CARGOS=454.0的记录，未找到。本轮无匹配，不计入。
10. 起始行(第21行): ABONOS1=350.0, OPER1=07/MAR。向下查找CARGOS=350.0的记录，未找到。本轮无匹配，不计入。
11. 起始行(第22行): ABONOS1=275.0, OPER1=07/MAR。向下查找CARGOS=275.0的记录，未找到。本轮无匹配，不计入。
12. 起始行(第23行): ABONOS1=120.0, OPER1=07/MAR。向下查找CARGOS=120.0的记录，未找到。本轮无匹配，不计入。
13. 起始行(第24行): ABONOS1=221.0, OPER1=07/MAR。向下查找CARGOS=221.0的记录，未找到。本轮无匹配，不计入。
14. 起始行(第25行): ABONOS1=65.0, OPER1=07/MAR。向下查找CARGOS=65.0的记录，未找到。本轮无匹配，不计入。
15. 起始行(第26行): ABONOS1=100.0, OPER1=08/MAR。向下查找CARGOS=100.0的记录，未找到。本轮无匹配，不计入。
16. 起始行(第27行): ABONOS1=1000.0, OPER1=08/MAR。向下查找CARGOS=1000.0的记录，未找到。本轮无匹配，不计入。
17. 起始行(第28行): ABONOS1=808.0, OPER1=10/MAR。向下查找CARGOS=808.0的记录，未找到。本轮无匹配，不计入。

校验规则执行：
1. 记录每个轮次中result值。符合result<=1的轮次有：轮次2(600.0)、轮次3(400.0)、轮次4(1000.0)。因此 result_total = 3。
2. 计算 ratio = result_total / total_cargo_cnt = 3 / 17 ≈ 0.1765。

决策结果执行：
规则要求：如果ratio > 0.8，输出“命中快进快出（异常）”；如果ratio <= 0.8，输出“未命中快进快出（无异常）”。
计算得 ratio ≈ 0.1765 <= 0.8，因此应输出“未命中快进快出（无异常）”。

hit值判断：
根据决策结果，规则未命中（无异常），因此 hit = false。

注意：在分析过程中，发现数据存在余额连续性检查失败的情况，但根据关键原则，本规则仅关注快进快出比例，不因其他异常而改变当前规则的判定。因此，判定结果严格基于本规则的计算。

**补充说明**: 严格按照规则定义的逻辑执行。计算出的快进快出比例(0.1765)未超过阈值0.8，因此判定为无异常。尽管数据存在其他不一致（如余额校验失败），但根据‘严禁跨规则连坐’原则，不影响本规则的判定。；已根据 evidence 结尾的明确结论自动修正 hit 值为 False

---

### 9. 交易明细分析_异常备注

**规则ID**: `MSTAR_BBVA_DTL_ANAL_ABN_REM`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_ANAL_ABN_REM
规则名称: 交易明细分析_异常备注

执行步骤（严格按照判断逻辑）：
1. 获取解析后Detalle de Movimientos Realizados部分的description对应的所有的值。
   - 已从提供的28笔交易明细中提取所有“描述”字段的值。

校验规则（严格按照校验规则）：
2. 判断所有描述值是否包含以下任意关键词：Apuesta，médico / médic，juego。
   - 对28条描述逐一进行关键词匹配检查。
   - 检查结果：未在任何一条描述中发现关键词“Apuesta”、“médico”、“médic”或“juego”。

决策结果（严格按照决策结果）：
3. 命中任意一个关键词，输出异常；全部都没命中，输出正常。
   - 由于所有描述均未命中关键词，因此输出“正常”。

关键交易明细（总笔数28笔，少于30笔，列出所有描述用于复核）：
1. FARM SAN PABLO RFC: PPL 961114GZ1 10:45 AUT: 534131
2. RETIRO CAJERO AUTOMATICO FEB15 14:13 BBVA B023 FOLIO:8526
3. RETIRO CAJERO AUTOMATICO FEB15 14:15 BBVA B023 FOLIO:8530
4. FARM DEL AHORRO RFC: CFC 110121742 18:19 AUT: 619962
5. MSFT STORE RFC: MME 910620Q85 17:08 AUT: 940435
6. TOKS RC SAN MIGUEL RFC: RTO 840921RE4 16:51 AUT: 343999
7. SPEI RECIBIDOMercado Pago 1234567MERCADO*PAGO 00722969010622928160 CPO102907595674 LUIS ALBERTO FERNANDEZ GARCIA
8. SPEI RECIBIDOTRANSFER 0697909Payment 00684180093000000007 2025022090684AWS093B2257DF9B0C ATMX TECNOLOGIA S.A. DE C.V.
9. SPEI ENVIADO AZTECA 0502250viaje 00004027665820229061 MBAN01002502210055790025 Fernando Trejo Peña
10. SPEI RECIBIDOAZTECA 2247230pago 00127180013023782852 250224070027657453I HERNANDEZ PALACIO OMAR EDGAR
11. MI ATT A APP PS RFC: CNM 980114PI2 03:24 AUT: 277353
12. SPEI ENVIADO AZTECA 0502250m 00004027665873176359 MBAN01002502240062208836 Ofelia Alejandra Jimenez
13. SPEI RECIBIDOBANAMEX 0250225transf 00002180701851485541 085901592990305657 OMAR EDGAR,HERNANDEZ/PALACIO
14. SPEI ENVIADO TRANSFER 0502250pago prestamo 25 02 2025 00684180093021753922 MBAN01002502250071057470 Yeye Cash
15. SPEI RECIBIDOAZTECA 2247230acta 00127180013692821607 250227010109232653I JIMENEZ FERNANDEZ OFELIA ALEJANDRA
16. SPEI ENVIADO AZTECA 0502250prueba 00004831121200462522 MBAN01002503030098623680 Bruno Gabriel Garcia Solares
17. SPEI ENVIADO AZTECA 0502250brunito 00004831121200462522 MBAN01002503030098639775 Bruno Gabriel Garcia Solares
18. PAGO DE NOMINA PENSIONES BANCOMER SA DE CV GFB
19. SPEI ENVIADO BANORTE 0502250colegMar25AaronFdz5toAzul 00072180006515343764 MBAN01002503040055267526 Abraham Lincoln SC
20. FARM SAN PABLO RFC: PPL 961114GZ1 14:04 AUT: 439763
21. SPEI RECIBIDOSTP 0140714Prestamo Cozmo 0140714 00646180502800000008 Cozmo00294536 DIGITAL DECK SAPI DE CV SOFOM ENR
22. PAGO CUENTA DE TERCERO BNET 1526105946 viaje
23. SPEI ENVIADO INBURSA 0502250viaje 00005399759406093376 MBAN01002503070069692550 Jorge Garcia
24. PAGO CUENTA DE TERCERO BNET 1598088118 viaje
25. PAGO CUENTA DE TERCERO BNET 1533862302 compra
26. SPEI ENVIADO AZTECA 0502250A 00004027665873176359 MBAN01002503100074029764 Ofelia Alejandra Jimenez
27. SPEI ENVIADO AZTECA 0502250Bien 00004831121200462522 MBAN01002503100074422200 Bruno Gabriel Garcia Solares
28. SPEI ENVIADO STP 05022500140714 00646180502800713654 MBAN01002503110081925204 Digital Deck SAPI de CV SOFOM ENR

比较结论：
- 所有28笔交易的描述字段均不包含关键词“Apuesta”、“médico / médic”或“juego”。
- 根据决策结果，全部未命中，输出“正常”。

hit判定理由：
- 规则要求检查描述是否包含特定异常关键词。经检查，未发现任何匹配项，因此规则未命中（合规/一致）。
- 根据规则定义，hit=false 表示规则未命中。

**补充说明**: 已严格按照判断逻辑、校验规则和决策结果执行。所有交易描述均不包含规则指定的异常关键词。

---

### 10. 交易时间校验_特殊时间段交易

**规则ID**: `MSTAR_BBVA_TIME_CHK_SPECIAL`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_TIME_CHK_SPECIAL
规则名称: 交易时间校验_特殊时间段交易

执行步骤说明：
步骤1：遍历Detalle de Movimientos Realizados的28条记录，从描述(description)中提取时间。
- 记录1: "FARM SAN PABLO RFC: PPL 961114GZ1 10:45 AUT: 534131" -> 提取时间: 10:45
- 记录2: "RETIRO CAJERO AUTOMATICO FEB15 14:13 BBVA B023 FOLIO:8526" -> 提取时间: 14:13
- 记录3: "RETIRO CAJERO AUTOMATICO FEB15 14:15 BBVA B023 FOLIO:8530" -> 提取时间: 14:15
- 记录4: "FARM DEL AHORRO RFC: CFC 110121742 18:19 AUT: 619962" -> 提取时间: 18:19
- 记录5: "MSFT STORE RFC: MME 910620Q85 17:08 AUT: 940435" -> 提取时间: 17:08
- 记录6: "TOKS RC SAN MIGUEL RFC: RTO 840921RE4 16:51 AUT: 343999" -> 提取时间: 16:51
- 记录7: "SPEI RECIBIDOMercado Pago 1234567MERCADO*PAGO 00722969010622928160 CPO102907595674 LUIS ALBERTO FERNANDEZ GARCIA" -> 无时间，跳过
- 记录8: "SPEI RECIBIDOTRANSFER 0697909Payment 00684180093000000007 2025022090684AWS093B2257DF9B0C ATMX TECNOLOGIA S.A. DE C.V." -> 无时间，跳过
- 记录9: "SPEI ENVIADO AZTECA 0502250viaje 00004027665820229061 MBAN01002502210055790025 Fernando Trejo Peña" -> 无时间，跳过
- 记录10: "SPEI RECIBIDOAZTECA 2247230pago 00127180013023782852 250224070027657453I HERNANDEZ PALACIO OMAR EDGAR" -> 无时间，跳过
- 记录11: "MI ATT A APP PS RFC: CNM 980114PI2 03:24 AUT: 277353" -> 提取时间: 03:24
- 记录12: "SPEI ENVIADO AZTECA 0502250m 00004027665873176359 MBAN01002502240062208836 Ofelia Alejandra Jimenez" -> 无时间，跳过
- 记录13: "SPEI RECIBIDOBANAMEX 0250225transf 00002180701851485541 085901592990305657 OMAR EDGAR,HERNANDEZ/PALACIO" -> 无时间，跳过
- 记录14: "SPEI ENVIADO TRANSFER 0502250pago prestamo 25 02 2025 00684180093021753922 MBAN01002502250071057470 Yeye Cash" -> 无时间，跳过
- 记录15: "SPEI RECIBIDOAZTECA 2247230acta 00127180013692821607 250227010109232653I JIMENEZ FERNANDEZ OFELIA ALEJANDRA" -> 无时间，跳过
- 记录16: "SPEI ENVIADO AZTECA 0502250prueba 00004831121200462522 MBAN01002503030098623680 Bruno Gabriel Garcia Solares" -> 无时间，跳过
- 记录17: "SPEI ENVIADO AZJECA 0502250brunito 00004831121200462522 MBAN01002503030098639775 Bruno Gabriel Garcia Solares" -> 无时间，跳过
- 记录18: "PAGO DE NOMINA PENSIONES BANCOMER SA DE CV GFB" -> 无时间，跳过
- 记录19: "SPEI ENVIADO BANORTE 0502250colegMar25AaronFdz5toAzul 00072180006515343764 MBAN01002503040055267526 Abraham Lincoln SC" -> 无时间，跳过
- 记录20: "FARM SAN PABLO RFC: PPL 961114GZ1 14:04 AUT: 439763" -> 提取时间: 14:04
- 记录21: "SPEI RECIBIDOSTP 0140714Prestamo Cozmo 0140714 00646180502800000008 Cozmo00294536 DIGITAL DECK SAPI DE CV SOFOM ENR" -> 无时间，跳过
- 记录22: "PAGO CUENTA DE TERCERO BNET 1526105946 viaje" -> 无时间，跳过
- 记录23: "SPEI ENVIADO INBURSA 0502250viaje 00005399759406093376 MBAN01002503070069692550 Jorge Garcia" -> 无时间，跳过
- 记录24: "PAGO CUENTA DE TERCERO BNET 1598088118 viaje" -> 无时间，跳过
- 记录25: "PAGO CUENTA DE TERCERO BNET 1533862302 compra" -> 无时间，跳过
- 记录26: "SPEI ENVIADO AZTECA 0502250A 00004027665873176359 MBAN01002503100074029764 Ofelia Alejandra Jimenez" -> 无时间，跳过
- 记录27: "SPEI ENVIADO AZTECA 0502250Bien 00004831121200462522 MBAN01002503100074422200 Bruno Gabriel Garcia Solares" -> 无时间，跳过
- 记录28: "SPEI ENVIADO STP 05022500140714 00646180502800713654 MBAN01002503110081925204 Digital Deck SAPI de CV SOFOM ENR" -> 无时间，跳过

步骤2：将提取到的时间放入集合。提取到的时间有：10:45, 14:13, 14:15, 18:19, 17:08, 16:51, 03:24, 14:04。

步骤3：统计处于2点至5点（包括2点和5点，24小时制）的交易笔数。
- 检查每个时间：
  * 10:45 -> 不在2-5点区间
  * 14:13 -> 不在2-5点区间
  * 14:15 -> 不在2-5点区间
  * 18:19 -> 不在2-5点区间
  * 17:08 -> 不在2-5点区间
  * 16:51 -> 不在2-5点区间
  * 03:24 -> 在2-5点区间内，计数+1
  * 14:04 -> 不在2-5点区间
- 统计结果：count = 1

校验规则：判断 count 是否大于 10。
- 当前 count = 1，1 <= 10。

决策结果：根据规则，count <= 10 输出“正常”。

结论：交易时间正常，未发现异常。

hit值判定：根据决策结果“正常”，判定为未命中规则，hit=false。

**补充说明**: 严格按照规则定义的步骤执行。从28条交易记录中，仅提取到8条包含明确时间的记录。其中只有1条记录（第11条，时间03:24）处于2点至5点的特殊时间段内。统计笔数count=1，未超过规则设定的阈值10，因此判定为合规。

---
