# BBVA 银行流水审计报告

**生成时间**: 2026-01-31 21:44:47

## 元数据

- **account_number**: 2960296619
- **total_pages**: 9
- **llm_provider**: deepseek
- **llm_model**: deepseek-chat

## 审计摘要

- **总规则数**: 10
- **命中规则数** (违规): 0
- **未命中规则数** (合规): 10
- **无法判断规则数**: 0

### 置信度分布

- **高置信度**: 10
- **中置信度**: 0
- **低置信度**: 0

## 详细审计结果

### 1. 明细交易笔数校验_入账笔数

**规则ID**: `MSTAR_BBVA_DTL_CNT_ABONOS`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 【执行步骤说明】
严格按照规则定义的判断逻辑执行：
Step 1: 从 'Comportamiento' 表格中提取 'Depósitos / Abonos (+)' 对应的总笔数。数据中明确给出：'Depósitos / Abonos (+): 5  233,768.72'，因此数值1 = 5。
Step 2: 遍历 'Detalle de Movimientos Realizados' 部分的所有交易行。数据中明确给出总笔数为35。
Step 3: 关键过滤：仅统计 'Abonos' 列有有效数值（非空且不为0）的行。数据中已提供参考值：'其中包含有效 Abonos (入账) 的交易数: 5'。为严格遵循步骤，逐条核对明细：
  1. 交易3: Abono:24360.0 (有效)
  2. 交易10: Abono:24360.0 (有效)
  3. 交易20: Abono:49618.72 (有效)
  4. 交易26: Abono:24940.0 (有效)
  5. 交易32: Abono:110490.0 (有效)
  其余30笔交易的 'Abonos' 列为'无'或空，均被忽略。
Step 4: 计算符合条件的交易总行数。经统计，符合条件的交易共5笔。因此数值2 = 5。

【校验规则执行】
比较数值1（来自Comportamiento）与数值2（来自明细统计）是否相等。
数值1 = 5
数值2 = 5
两者相等。

【决策结果】
根据规则，如果相等，输出“一致”（无异常）。

【hit值判定】
根据规则，'一致'对应 hit=false（合规/未命中）。

**补充说明**: 数据中已提供预计算的'有效 Abonos (入账) 的交易数: 5'，与手动逐条核对结果完全一致，验证过程可靠。

---

### 2. 明细交易笔数校验_出账笔数

**规则ID**: `MSTAR_BBVA_DTL_CNT_CARGOS`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_CNT_CARGOS
规则名称: 明细交易笔数校验_出账笔数

执行步骤（严格按照判断逻辑）：
(Step 1) 从 'Comportamiento' 表格中提取 'Retiros / Cargos (-)'（出账）对应的总笔数（Total Movimientos Cargos）。
- 执行结果：在提供的 'Comportamiento' 和 'total_movimientos' 数据中，均明确显示 'Retiros / Cargos (-)' 的总笔数为 30。
- 数值1 (来自Comportamiento/total_movimientos): 30

(Step 2) 遍历 'Detalle de Movimientos Realizados'（交易明细）部分的所有交易行。
- 执行结果：明细部分共列出 35 笔交易。

(Step 3) [关键过滤] 仅统计 'Cargos' 列有有效数值（非空且不为0）的行。如果某行只有 'Abono' 列有值，必须忽略。
- 执行结果：根据数据中提供的参考值 '其中包含有效 Cargos (出账) 的交易数: 30'，确认过滤后符合条件的交易笔数为 30。
- 为便于人工复核，列出所有 30 笔有效 Cargos 交易的金额明细（按原始顺序）：
1. Cargo: 7200.0
2. Cargo: 500.0
4. Cargo: 4000.0
5. Cargo: 12000.0
6. Cargo: 3000.0
7. Cargo: 300.0
8. Cargo: 1700.0
9. Cargo: 1500.0
11. Cargo: 1000.0
12. Cargo: 7000.0
13. Cargo: 2000.0
14. Cargo: 2500.0
15. Cargo: 11000.0
16. Cargo: 634.27
17. Cargo: 1000.0
18. Cargo: 535.0
19. Cargo: 1000.0
21. Cargo: 1000.0
22. Cargo: 1000.0
23. Cargo: 20000.0
24. Cargo: 23000.0
25. Cargo: 1400.0
27. Cargo: 3200.0
28. Cargo: 600.0
29. Cargo: 11000.0
30. Cargo: 1000.0
31. Cargo: 1200.0
33. Cargo: 12000.0
34. Cargo: 5500.0
35. Cargo: 2000.0

(Step 4) 计算符合条件的交易总行数。
- 执行结果：经统计，上述列出的有效 Cargos 交易共 30 笔。
- 数值2 (来自明细统计): 30

校验规则（严格按照校验规则）：比较数值1和数值2是否相等。
- 比较结果：数值1 (30) 等于 数值2 (30)。

决策结果（严格按照决策结果）：如果相等，输出一致（无异常）。
- 最终结论：明细中的出账交易笔数与 Comportamiento 中报告的总笔数一致。

hit 值判定理由：根据规则定义，两个数值相等，输出“一致”，因此 hit=false（合规/未命中）。

**补充说明**: 数据充足，逻辑清晰，判定明确。

---

### 3. 明细交易金额校验_入账金额

**规则ID**: `MSTAR_BBVA_DTL_AMT_ABONOS`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_AMT_ABONOS
规则名称: 明细交易金额校验_入账金额

执行步骤（严格按照判断逻辑）：
(Step 1) 从 'Comportamiento' 表格中提取 'Depósitos / Abonos (+)'（入账）对应的总金额。
执行结果：从数据中提取到 'Depósitos / Abonos (+): 5  233,768.72'，总金额为 233,768.72。
(Step 2) 遍历 'Detalle de Movimientos Realizados' 或raw_transaction_data部分。
执行结果：已遍历提供的35笔交易明细。
(Step 3) [关键过滤] 累加所有 'Abonos' 列的数值。忽略 'Cargo' 列的数值。
执行结果：根据数据提示，有效 Abonos (入账) 的交易数为 5。现列出所有 Abonos 不为空的交易明细（共5笔）：
1. 交易3: Abono: 24360.0
2. 交易10: Abono: 24360.0
3. 交易20: Abono: 49618.72
4. 交易26: Abono: 24940.0
5. 交易32: Abono: 110490.0
(Step 4) 确保金额格式转换正确（处理千分位逗号）。
执行结果：明细中金额均为数字格式，无需转换。

计算过程（严格按照校验规则）：
数值1（来自 Comportamiento）: 233,768.72
数值2（来自 Detalle 累加）: 24360.0 + 24360.0 + 49618.72 + 24940.0 + 110490.0 = 233,768.72

比较结果：数值1 (233,768.72) 与 数值2 (233,768.72) 相等。

决策结果（严格按照决策结果）：
两个数值相等，输出“一致”（无异常）。

最终判定：根据规则，一致 = 合规 = hit=false。

**补充说明**: 数据完整，计算过程清晰，结果明确。

---

### 4. 明细交易金额校验_出账金额

**规则ID**: `MSTAR_BBVA_DTL_AMT_CARGOS`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_AMT_CARGOS
规则名称: 明细交易金额校验_出账金额

执行步骤（严格按照判断逻辑）：
(Step 1) 从 'Comportamiento' 表格中提取 'Retiros / Cargos (-)'（出账）对应的总金额。
执行结果：从数据中提取到 'Retiros / Cargos (-): 30  139,769.27'，因此数值1 = 139769.27。
(Step 2) 遍历 'Detalle de Movimientos Realizados' 或raw_transaction_data部分。
执行结果：已遍历提供的35条明细交易记录。
(Step 3) [关键过滤] 累加所有 'Cargos' 列的数值。忽略 'Abono' 列的数值。
执行结果：根据数据，有效 Cargos (出账) 的交易数为30笔。现列出所有30笔Cargos金额明细（按原始顺序）：
1. 7200.0
2. 500.0
4. 4000.0
5. 12000.0
6. 3000.0
7. 300.0
8. 1700.0
9. 1500.0
11. 1000.0
12. 7000.0
13. 2000.0
14. 2500.0
15. 11000.0
16. 634.27
17. 1000.0
18. 535.0
19. 1000.0
21. 1000.0
22. 1000.0
23. 20000.0
24. 23000.0
25. 1400.0
27. 3200.0
28. 600.0
29. 11000.0
30. 1000.0
31. 1200.0
33. 12000.0
34. 5500.0
35. 2000.0
(Step 4) 确保金额格式转换正确（处理千分位逗号）。
执行结果：明细中所有金额均为数字格式，无需转换。对上述30笔金额求和：7200.0 + 500.0 + 4000.0 + 12000.0 + 3000.0 + 300.0 + 1700.0 + 1500.0 + 1000.0 + 7000.0 + 2000.0 + 2500.0 + 11000.0 + 634.27 + 1000.0 + 535.0 + 1000.0 + 1000.0 + 1000.0 + 20000.0 + 23000.0 + 1400.0 + 3200.0 + 600.0 + 11000.0 + 1000.0 + 1200.0 + 12000.0 + 5500.0 + 2000.0 = 139769.27。因此数值2 = 139769.27。

校验规则（严格按照校验规则）：比较1和2是否相等。
比较结果：数值1 (139769.27) 等于 数值2 (139769.27)。

决策结果（严格按照决策结果）：如果相等，输出一致（无异常）。
最终结论：明细交易中Cargos金额总和与Comportamiento中报告的出账总金额一致。

hit值判定理由：根据规则，两个数值相等，输出“一致”，因此 hit=false。

**补充说明**: 数据完整，计算过程清晰，结果明确。

---

### 5. 明细交易金额校验_单笔金额

**规则ID**: `MSTAR_BBVA_DTL_AMT_SINGLE`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_AMT_SINGLE
规则名称: 明细交易金额校验_单笔金额

执行步骤与结果：
1. 保持交易列表的原始顺序：已严格按照提供的35笔交易顺序处理。
2. 确定初始锚点(Balance_1)：第一行交易有 'Operacion' 值 5183.2，将其记为 Balance_1。计算起点从下一行（第2笔）开始。
3. 寻找下一个锚点(Balance_2)并迭代核算：按照规则逻辑，遍历列表，找到所有包含 'Operacion' 或 'Saldo' 值的行作为锚点，进行区间核算。
   - 锚点1 (Balance_1): 第1行，Operacion=5183.2
   - 锚点2 (Balance_2): 第2行，Operacion=4683.2
     区间：第2行（从Balance_1的下一行开始）到第2行（包含Balance_2）。
     计算：Sum(Cargos)=500.0, Sum(Abonos)=0.0
     result = 5183.2 - 500.0 + 0.0 - 4683.2 = 0.0
   - 锚点3 (Balance_2): 第4行，Operacion=25043.2
     区间：第3行到第4行。
     计算：Sum(Cargos)=4000.0, Sum(Abonos)=24360.0
     result = 4683.2 - 4000.0 + 24360.0 - 25043.2 = 0.0
   - 锚点4 (Balance_2): 第7行，Operacion=9743.2
     区间：第5行到第7行。
     计算：Sum(Cargos)=12000.0+3000.0+300.0=15300.0, Sum(Abonos)=0.0
     result = 25043.2 - 15300.0 + 0.0 - 9743.2 = 0.0
   - 锚点5 (Balance_2): 第8行，Operacion=8043.2
     区间：第8行（注意：第8行本身是锚点，但根据规则，区间包含Balance_2，因此需检查其自身Cargo/Abono对余额的影响。此处第8行Cargo=1700.0，但Operacion=8043.2，Saldo=9743.2。计算逻辑应为：Balance_1(9743.2) - Cargo(1700.0) = 8043.2，与Operacion一致，result应为0。为清晰，按规则公式计算：区间为第8行。Sum(Cargos)=1700.0, Sum(Abonos)=0.0。result = 9743.2 - 1700.0 + 0.0 - 8043.2 = 0.0）
   - 锚点6 (Balance_2): 第9行，Operacion=6543.2
     区间：第9行。
     计算：Sum(Cargos)=1500.0, Sum(Abonos)=0.0
     result = 8043.2 - 1500.0 + 0.0 - 6543.2 = 0.0
   - 锚点7 (Balance_2): 第14行，Operacion=18403.2
     区间：第10行到第14行。
     计算：Sum(Cargos)=1000.0+7000.0+2000.0+2500.0=12500.0, Sum(Abonos)=24360.0
     result = 6543.2 - 12500.0 + 24360.0 - 18403.2 = 0.0
   - 锚点8 (Balance_2): 第16行，Operacion=6768.93
     区间：第15行到第16行。
     计算：Sum(Cargos)=11000.0+634.27=11634.27, Sum(Abonos)=0.0
     result = 18403.2 - 11634.27 + 0.0 - 6768.93 = 0.0
   - 锚点9 (Balance_2): 第19行，Operacion=4233.93
     区间：第17行到第19行。
     计算：Sum(Cargos)=1000.0+535.0+1000.0=2535.0, Sum(Abonos)=0.0
     result = 6768.93 - 2535.0 + 0.0 - 4233.93 = 0.0
   - 锚点10 (Balance_2): 第23行，Operacion=31852.65
     区间：第20行到第23行。
     计算：Sum(Cargos)=1000.0+1000.0+20000.0=22000.0, Sum(Abonos)=49618.72
     result = 4233.93 - 22000.0 + 49618.72 - 31852.65 = 0.0
   - 锚点11 (Balance_2): 第24行，Operacion=8852.65
     区间：第24行。
     计算：Sum(Cargos)=23000.0, Sum(Abonos)=0.0
     result = 31852.65 - 23000.0 + 0.0 - 8852.65 = 0.0
   - 锚点12 (Balance_2): 第25行，Operacion=7452.65
     区间：第25行。
     计算：Sum(Cargos)=1400.0, Sum(Abonos)=0.0
     result = 8852.65 - 1400.0 + 0.0 - 7452.65 = 0.0
   - 锚点13 (Balance_2): 第27行，Operacion=29192.65
     区间：第26行到第27行。
     计算：Sum(Cargos)=3200.0, Sum(Abonos)=24940.0
     result = 7452.65 - 3200.0 + 24940.0 - 29192.65 = 0.0
   - 锚点14 (Balance_2): 第30行，Operacion=16592.65
     区间：第28行到第30行。
     计算：Sum(Cargos)=600.0+11000.0+1000.0=12600.0, Sum(Abonos)=0.0
     result = 29192.65 - 12600.0 + 0.0 - 16592.65 = 0.0
   - 锚点15 (Balance_2): 第32行，Operacion=125882.65
     区间：第31行到第32行。
     计算：Sum(Cargos)=1200.0, Sum(Abonos)=110490.0
     result = 16592.65 - 1200.0 + 110490.0 - 125882.65 = 0.0
   - 锚点16 (Balance_2): 第35行，Operacion=106382.65
     区间：第33行到第35行。
     计算：Sum(Cargos)=12000.0+5500.0+2000.0=19500.0, Sum(Abonos)=0.0
     result = 125882.65 - 19500.0 + 0.0 - 106382.65 = 0.0
4. 校验规则：记录每一个轮次中步骤4的result值。所有轮次的result值均为0。
5. 决策结果：因为所有的result值都为0，所以输出一致（无异常）。

结论：所有锚点区间内的交易金额核算结果均为0，明细交易金额连续且正确。因此，规则未命中（合规/一致）。

**补充说明**: 已严格按照规则定义的判断逻辑、校验规则和决策结果执行。所有核算结果均为0，判定为一致。

---

### 6. 交易日期校验_日期一致性

**规则ID**: `MSTAR_BBVA_DATE_CHK_CONS`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 执行步骤1：从数据中获取模糊匹配包含'Periodo'的信息。找到内容：'DEL 21/06/2025 AL 20/07/2025'。解析得到日期区间为：[开始日期 21/06/2025, 结束日期 20/07/2025]。
执行步骤2：从'Detalle de Movimientos Realizados'中提取所有交易的OPER和LIQ日期。共35笔交易。计算所有日期中的最小日期(min_date)和最大日期(max_date)。
明细如下（按原始顺序列出所有交易的OPER和LIQ日期）：
1. Oper:21/JUN, Liq:23/JUN
2. Oper:24/JUN, Liq:24/JUN
3. Oper:26/JUN, Liq:26/JUN
4. Oper:26/JUN, Liq:26/JUN
5. Oper:27/JUN, Liq:27/JUN
6. Oper:27/JUN, Liq:27/JUN
7. Oper:27/JUN, Liq:27/JUN
8. Oper:28/JUN, Liq:30/JUN
9. Oper:02/JUL, Liq:02/JUL
10. Oper:03/JUL, Liq:03/JUL
11. Oper:03/JUL, Liq:03/JUL
12. Oper:03/JUL, Liq:03/JUL
13. Oper:03/JUL, Liq:03/JUL
14. Oper:03/JUL, Liq:03/JUL
15. Oper:04/JUL, Liq:04/JUL
16. Oper:04/JUL, Liq:04/JUL
17. Oper:06/JUL, Liq:07/JUL
18. Oper:06/JUL, Liq:07/JUL
19. Oper:06/JUL, Liq:07/JUL
20. Oper:07/JUL, Liq:07/JUL
21. Oper:07/JUL, Liq:07/JUL
22. Oper:07/JUL, Liq:07/JUL
23. Oper:07/JUL, Liq:07/JUL
24. Oper:08/JUL, Liq:08/JUL
25. Oper:09/JUL, Liq:09/JUL
26. Oper:10/JUL, Liq:10/JUL
27. Oper:10/JUL, Liq:10/JUL
28. Oper:11/JUL, Liq:11/JUL
29. Oper:11/JUL, Liq:11/JUL
30. Oper:11/JUL, Liq:14/JUL
31. Oper:17/JUL, Liq:17/JUL
32. Oper:17/JUL, Liq:17/JUL
33. Oper:18/JUL, Liq:18/JUL
34. Oper:18/JUL, Liq:18/JUL
35. Oper:18/JUL, Liq:18/JUL
计算得出：最小日期(min_date)为21/JUN（对应21/06/2025），最大日期(max_date)为18/JUL（对应18/07/2025）。
执行校验规则：判断步骤2中的min_date（21/06/2025）和max_date（18/07/2025）是否都在步骤1的日期区间[21/06/2025, 20/07/2025]范围内。
比较结果：min_date（21/06/2025）等于区间开始日期（21/06/2025），在区间内。max_date（18/07/2025）早于区间结束日期（20/07/2025），在区间内。因此，min_date和max_date均在步骤1的日期区间范围内。
决策结果：根据规则，步骤2中的min_date和max_date在步骤1的日期区间范围内，输出“一致（无异常）”。
结论：日期一致性校验通过，无异常。

**补充说明**: 规则仅校验交易明细中的最小和最大日期是否在Periodo声明的区间内。经核查，明细日期范围[21/JUN, 18/JUL]完全落在[21/06/2025, 20/07/2025]之内，符合规则要求。

---

### 7. 交易明细分析_高风险职业

**规则ID**: `MSTAR_BBVA_DTL_ANAL_RISK_OCC`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 步骤1：取出Detalle de Movimientos Realizados中所有交易的DESCRIPCION（描述）字段。
已提取所有35笔交易的描述，按原始顺序列出如下：
1. RETIRO CAJERO AUTOMATICO JUN21 11:25 BBVA 9340 FOLIO:8584
2. PAGO TARJETA DE CREDITO CUENTA: BMOV
3. SPEI RECIBIDOSANTANDER 5292262PAGO ALMA RUTH CORONA HUERTA 00014811655024495195 20250626400140BET0000452922620 AS INTERMODAL SA DE CV
4. PAGO TARJETA DE CREDITO CUENTA: BMOV
5. RETIRO CAJERO AUTOMATICO JUN27 10:24 BBVA 9340 FOLIO:1557
6. PAGO TARJETA DE CREDITO CUENTA: BMOV
7. PAGO TARJETA DE CREDITO CUENTA: BMOV
8. RETIRO CAJERO AUTOMATICO JUN28 09:10 BBVA 6728 FOLIO:1767
9. PAGO CUENTA DE TERCERO BNET 1500027883 letra carro
10. SPEI RECIBIDOSANTANDER 4039985PAGO AS ALMA RUTH CORONA HUERT 00014811655024495195 20250703400140BET0000440399850 AS INTERMODAL SA DE CV
11. PAGO TARJETA DE CREDITO CUENTA: BMOV
12. RETIRO CAJERO AUTOMATICO JUL03 11:07 BBVA 4990 FOLIO:9573
13. SPEI ENVIADO BANCOPPEL 0906250xx 00004169160884848251 MBAN01002507030050050219 Jose Luis Aguilar
14. PAGO CUENTA DE TERCERO BNET 1503166940 xx
15. RETIRO CAJERO AUTOMATICO JUL04 12:29 BBVA C516 FOLIO:3411
16. PAGO TARJETA DE CREDITO CUENTA: BMOV
17. PAGO CUENTA DE TERCERO BNET 1189291784 viaje
18. PAGO CUENTA DE TERCERO BNET 1500027883 Tatis
19. SPEI ENVIADO BANCOPPEL 0906250xx 00004169160884848251 MBAN01002507070066119322 Jose Luis Aguilar
20. PAGO DE NOMINA 0000300047226CP000101400
21. PAGO CUENTA DE TERCERO BNET 1523845844 Transf a JOSE ROBE
22. RETIRO CAJERO AUTOMATICO JUL07 15:01 BBVA 4990 FOLIO:1760
23. SPEI ENVIADO BANAMEX 0906250xx 00002385701804309013 MBAN01002507070069476101 Luis Alberto Corona Huerta
24. SPEI ENVIADO BANORTE 0906250xx 00004189143112330074 MBAN01002507080072879181 Alma
25. SPEI ENVIADO BANCOPPEL 0906250xx 00004169160884848251 MBAN01002507090076354176 Jose Luis Aguilar
26. SPEI RECIBIDOSANTANDER 6274788PAGO AS ALMA RUTH CORONA HUERT 00014811655024495195 20250710400140BET0000462747880 AS INTERMODAL SA DE CV
27. RETIRO CAJERO AUTOMATICO JUL10 20:05 BBVA E934 FOLIO:6021
28. PAGO CUENTA DE TERCERO BNET 1189291784 xx
29. RETIRO CAJERO AUTOMATICO JUL11 21:00 BBVA 9340 FOLIO:8887
30. RETIRO SIN TARJETA
31. RETIRO CAJERO AUTOMATICO JUL17 12:46 BBVA 9340 FOLIO:1908
32. SPEI RECIBIDOSANTANDER 8409055PAGO AS ALMA RUTH CORONA HUERT 00014811655024495195 20250717400140BET0000484090550 AS INTERMODAL SA DE CV
33. RETIRO CAJERO AUTOMATICO JUL18 10:23 BBVA 7690 FOLIO:3685
34. SPEI ENVIADO BANAMEX 0906250xx 00002385701804309013 MBAN01002507180070127319 Luis Alberto Corona Huerta
35. PAGO CUENTA DE TERCERO BNET 1500027883 xx

步骤2：将上述所有描述翻译成中文。
已翻译所有描述，按原始顺序列出如下：
1. 自动取款机取款 JUN21 11:25 BBVA 9340 凭证号:8584
2. 信用卡还款 账户: BMOV
3. SPEI 收款 SANTANDER 5292262 付款 ALMA RUTH CORONA HUERTA ... AS INTERMODAL SA DE CV
4. 信用卡还款 账户: BMOV
5. 自动取款机取款 JUN27 10:24 BBVA 9340 凭证号:1557
6. 信用卡还款 账户: BMOV
7. 信用卡还款 账户: BMOV
8. 自动取款机取款 JUN28 09:10 BBVA 6728 凭证号:1767
9. 向第三方账户付款 BNET 1500027883 汽车贷款
10. SPEI 收款 SANTANDER 4039985 付款 AS ALMA RUTH CORONA HUERT ... AS INTERMODAL SA DE CV
11. 信用卡还款 账户: BMOV
12. 自动取款机取款 JUL03 11:07 BBVA 4990 凭证号:9573
13. SPEI 发送 BANCOPPEL ... Jose Luis Aguilar
14. 向第三方账户付款 BNET 1503166940 xx
15. 自动取款机取款 JUL04 12:29 BBVA C516 凭证号:3411
16. 信用卡还款 账户: BMOV
17. 向第三方账户付款 BNET 1189291784 旅行
18. 向第三方账户付款 BNET 1500027883 Tatis
19. SPEI 发送 BANCOPPEL ... Jose Luis Aguilar
20. 工资支付 0000300047226CP000101400
21. 向第三方账户付款 BNET 1523845844 转账给 JOSE ROBE
22. 自动取款机取款 JUL07 15:01 BBVA 4990 凭证号:1760
23. SPEI 发送 BANAMEX ... Luis Alberto Corona Huerta
24. SPEI 发送 BANORTE ... Alma
25. SPEI 发送 BANCOPPEL ... Jose Luis Aguilar
26. SPEI 收款 SANTANDER 6274788 付款 AS ALMA RUTH CORONA HUERT ... AS INTERMODAL SA DE CV
27. 自动取款机取款 JUL10 20:05 BBVA E934 凭证号:6021
28. 向第三方账户付款 BNET 1189291784 xx
29. 自动取款机取款 JUL11 21:00 BBVA 9340 凭证号:8887
30. 无卡取款
31. 自动取款机取款 JUL17 12:46 BBVA 9340 凭证号:1908
32. SPEI 收款 SANTANDER 8409055 付款 AS ALMA RUTH CORONA HUERT ... AS INTERMODAL SA DE CV
33. 自动取款机取款 JUL18 10:23 BBVA 7690 凭证号:3685
34. SPEI 发送 BANAMEX ... Luis Alberto Corona Huerta
35. 向第三方账户付款 BNET 1500027883 xx

校验规则：检查所有中文描述是否命中任意一个关键词。
关键词列表：现金密集型业务；小型零售商和街头摊贩（如露天市场摊贩）；夜总会；酒吧；娱乐场所经营者；灰色；非法行业关联者；未注册或非正式的安保服务提供商；涉嫌贷款翻转或文件造假的汽车贷款经纪人或中介；可能与贩毒或有组织犯罪相关的幌子企业（如虚假奢侈品转售店、空壳运输公司）；欺诈高发行业；不受监管的汽车经销商或中介，尤其是推广 “零首付” 优惠的或收入不规律或无法核实的自雇人士；在汽车金融行业工作的个人；独立或未注册的汽车维修店员工。

逐条检查结果：
- 所有描述均为常规银行交易，如取款、信用卡还款、工资入账、向第三方转账（包括备注为“汽车贷款”、“旅行”等）、SPEI收发款。
- 没有任何一条描述包含上述关键词或其同义词。例如，第9笔交易备注“letra carro”（汽车贷款）是个人消费贷款还款，不涉及“汽车贷款经纪人或中介”的欺诈行为描述。
- 没有描述提及现金密集型业务、零售摊贩、夜总会、酒吧、娱乐场所、灰色/非法行业、安保服务、幌子企业、欺诈高发行业、不受监管的汽车经销商、汽车金融行业从业者或汽车维修店员工。

决策结果：所有描述均未命中关键词。
结论：输出正常。

**补充说明**: 根据规则要求，对35笔交易的描述进行了提取、翻译和关键词匹配。所有交易描述均为常规银行业务，未发现与高风险职业相关的关键词。因此判定为未命中规则（hit=false）。

---

### 8. 交易明细分析_快进快出

**规则ID**: `MSTAR_BBVA_DTL_ANAL_FAST_IO`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_ANAL_FAST_IO
规则名称: 交易明细分析_快进快出

执行步骤与结果：
1. 步骤1：已取Detalle de Movimientos Realizados中所有35条记录，并按OPER日期升序排序（数据已按此顺序提供）。
2. 步骤2：统计所有记录中ABONOS取值不为空的总记录数。根据数据，'有效 Abonos (入账) 的交易数'为5，因此 total_cargo_cnt = 5。
3. 步骤3-6：从第一条记录开始，逐一查找ABONOS值不为空的行作为起始行，并执行后续匹配。
   - 第1个Abono（起始行）：记录3，OPER1=26/JUN，ABONOS1=24360.0。向下查找CARGOS列值与ABONOS1(24360.0)相同的记录。最近的匹配记录是记录4（Cargo:4000.0，不匹配），记录5（Cargo:12000.0，不匹配）... 遍历所有后续记录，未找到CARGOS值为24360.0的记录。因此，无法获取OPER2，本轮result无法计算，不计入result_total。
   - 第2个Abono（起始行）：记录10，OPER1=03/JUL，ABONOS1=24360.0。向下查找CARGOS列值与ABONOS1(24360.0)相同的记录。遍历后续记录，未找到CARGOS值为24360.0的记录。本轮result无法计算，不计入result_total。
   - 第3个Abono（起始行）：记录20，OPER1=07/JUL，ABONOS1=49618.72。向下查找CARGOS列值与ABONOS1(49618.72)相同的记录。遍历后续记录，未找到CARGOS值为49618.72的记录。本轮result无法计算，不计入result_total。
   - 第4个Abono（起始行）：记录26，OPER1=10/JUL，ABONOS1=24940.0。向下查找CARGOS列值与ABONOS1(24940.0)相同的记录。遍历后续记录，未找到CARGOS值为24940.0的记录。本轮result无法计算，不计入result_total。
   - 第5个Abono（起始行）：记录32，OPER1=17/JUL，ABONOS1=110490.0。向下查找CARGOS列值与ABONOS1(110490.0)相同的记录。遍历后续记录，未找到CARGOS值为110490.0的记录。本轮result无法计算，不计入result_total。
4. 校验规则1：在所有5轮查找中，均未找到与Abonos金额匹配的Cargos记录，因此没有任何一轮的result值被计算，result_total = 0。
5. 校验规则2：ratio = result_total / total_cargo_cnt = 0 / 5 = 0。
6. 决策结果：ratio (0) <= 0.8，因此输出“未命中快进快出（无异常）”。

结论：根据规则逻辑，未发现快进快出模式。ratio为0，小于等于阈值0.8，判定为无异常。

**补充说明**: 所有5笔Abonos交易均未在后续交易中找到金额完全匹配的Cargos交易，因此无法计算任何日期间隔（result）。根据规则，只有找到匹配对且间隔天数<=1时才计数。由于没有匹配对，result_total为0，ratio为0，未触发异常阈值。

---

### 9. 交易明细分析_异常备注

**规则ID**: `MSTAR_BBVA_DTL_ANAL_ABN_REM`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 执行步骤1（判断逻辑）：获取解析后Detalle de Movimientos Realizados部分的description对应的所有的值。
已获取全部35笔交易的描述（DESCRIPCION）字段。

执行校验规则：判断DESCRIPCION对应的所有的值是否包含以下任意关键词：Apuesta，médico / médic，juego。
检查过程：逐条检查35笔交易的描述，未发现任何描述包含关键词“Apuesta”、“médico”、“médic”或“juego”。
检查结果：所有描述均未命中关键词。

决策结果：全部都没命中，输出正常。

结论：根据规则MSTAR_BBVA_DTL_ANAL_ABN_REM的校验逻辑，未发现包含异常关键词的交易。

**补充说明**: 规则要求检查描述中是否包含特定关键词（Apuesta，médico / médic，juego）。经核查所有35笔交易描述，均不包含这些关键词，因此判定为正常（hit=false）。

---

### 10. 交易时间校验_特殊时间段交易

**规则ID**: `MSTAR_BBVA_TIME_CHK_SPECIAL`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_TIME_CHK_SPECIAL
规则名称: 交易时间校验_特殊时间段交易

执行步骤：
1. 按照判断逻辑步骤1，遍历Detalle de Movimientos Realizados的35条记录，从描述(description)中提取时间。
2. 提取结果：
   - 记录1: "RETIRO CAJERO AUTOMATICO JUN21 11:25 BBVA 9340 FOLIO:8584" -> 提取时间 "11:25"
   - 记录5: "RETIRO CAJERO AUTOMATICO JUN27 10:24 BBVA 9340 FOLIO:1557" -> 提取时间 "10:24"
   - 记录8: "RETIRO CAJERO AUTOMATICO JUN28 09:10 BBVA 6728 FOLIO:1767" -> 提取时间 "09:10"
   - 记录12: "RETIRO CAJERO AUTOMATICO JUL03 11:07 BBVA 4990 FOLIO:9573" -> 提取时间 "11:07"
   - 记录15: "RETIRO CAJERO AUTOMATICO JUL04 12:29 BBVA C516 FOLIO:3411" -> 提取时间 "12:29"
   - 记录22: "RETIRO CAJERO AUTOMATICO JUL07 15:01 BBVA 4990 FOLIO:1760" -> 提取时间 "15:01"
   - 记录27: "RETIRO CAJERO AUTOMATICO JUL10 20:05 BBVA E934 FOLIO:6021" -> 提取时间 "20:05"
   - 记录29: "RETIRO CAJERO AUTOMATICO JUL11 21:00 BBVA 9340 FOLIO:8887" -> 提取时间 "21:00"
   - 记录31: "RETIRO CAJERO AUTOMATICO JUL17 12:46 BBVA 9340 FOLIO:1908" -> 提取时间 "12:46"
   - 记录33: "RETIRO CAJERO AUTOMATICO JUL18 10:23 BBVA 7690 FOLIO:3685" -> 提取时间 "10:23"
   - 其他记录的描述中不包含时间信息（如PAGO TARJETA DE CREDITO, SPEI RECIBIDO等），按照规则跳过。
3. 按照步骤2，将获取到的时间放入集合：{'11:25', '10:24', '09:10', '11:07', '12:29', '15:01', '20:05', '21:00', '12:46', '10:23'}。
4. 按照步骤3，统计集合中处于2点至5点（包括2点和5点，24小时制）的交易笔数(count)。
   - 检查每个时间：
     * 11:25 -> 不在2-5点区间
     * 10:24 -> 不在2-5点区间
     * 09:10 -> 不在2-5点区间
     * 11:07 -> 不在2-5点区间
     * 12:29 -> 不在2-5点区间
     * 15:01 -> 不在2-5点区间
     * 20:05 -> 不在2-5点区间
     * 21:00 -> 不在2-5点区间
     * 12:46 -> 不在2-5点区间
     * 10:23 -> 不在2-5点区间
   - 统计结果：count = 0。

校验规则：
判断 count 是否大于 10。
当前 count = 0，不大于10。

决策结果：
根据规则，count <= 10 输出“正常”。

结论：
交易时间正常，未发现异常数量的凌晨2点至5点交易。

hit值判定：
根据决策结果“正常”，判定为未命中规则，hit=false。

**补充说明**: 严格按照规则步骤执行，从描述中提取了所有包含时间的交易，并统计了凌晨2-5点的交易笔数。所有提取到时间的交易均不在该特殊时间段内，因此count为0，符合规则要求。

---
