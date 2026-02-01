# BBVA 银行流水审计报告

**生成时间**: 2026-02-01 10:32:08

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

> 规则ID: MSTAR_BBVA_DTL_CNT_ABONOS
规则名称: 明细交易笔数校验_入账笔数

执行步骤与结果：
(Step 1) 从 'Comportamiento' 表格中提取 'Depósitos / Abonos (+)'（入账）对应的总笔数（Total Movimientos Abonos）。
- 数据来源：在提供的“Comportamiento”和“total_movimientos”部分，均明确列出“total_movimientos_abonos: 5”。
- 提取结果：数值1 = 5。

(Step 2) 遍历 'Detalle de Movimientos Realizados'或raw_transaction_data（交易明细）部分的所有交易行。
- 数据来源：已提供的结构化明细，总笔数为35。

(Step 3) [关键过滤] 仅统计 'Abonos' 列有有效数值（非空且不为0）的行。如果某行只有 'Cargo' 列有值，必须忽略。
- 执行过程：遍历35笔明细，检查每行的“ABONOS”字段。
- 过滤结果：符合条件的交易明细如下（共5笔）：
  1. 行3: ABONOS:24360.0
  2. 行10: ABONOS:24360.0
  3. 行20: ABONOS:49618.72
  4. 行26: ABONOS:24940.0
  5. 行32: ABONOS:110490.0

(Step 4) 计算符合条件的交易总行数。
- 计算过程：统计上述列表，共计5行。
- 提取结果：数值2 = 5。

校验规则：比较1和2是否相等。
- 比较结果：数值1 (5) 等于 数值2 (5)。

决策结果：如果相等，输出一致（无异常）。
- 最终判定：一致。

hit值判定：根据规则，一致对应 hit=false。

**补充说明**: 数据中已提供预计算的参考值“有效 Abonos 交易数: 5”，与手动统计结果一致，验证无误。

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
- 数据来源：在提供的“Comportamiento”和“total_movimientos”部分，均明确列出“Retiros / Cargos (-): 30”和“total_movimientos_cargos: 30”。
- 提取结果：数值1 = 30。

(Step 2) 遍历 'Detalle de Movimientos Realizados'（交易明细）部分的所有交易行。
- 明细部分总共有35笔交易。

(Step 3) [关键过滤] 仅统计 'Cargos' 列有有效数值（非空且不为0）的行。如果某行只有 'Abono' 列有值，必须忽略。
- 根据数据中提供的参考值：“其中包含有效 Cargos (出账) 的交易数: 30”。
- 为进行验证，人工复核明细：逐行检查“CARGOS”字段。
- 符合条件的交易（CARGOS有数值）明细如下（共30笔）：
  1. CARGOS:7200.0
  2. CARGOS:500.0
  4. CARGOS:4000.0
  5. CARGOS:12000.0
  6. CARGOS:3000.0
  7. CARGOS:300.0
  8. CARGOS:1700.0
  9. CARGOS:1500.0
  11. CARGOS:1000.0
  12. CARGOS:7000.0
  13. CARGOS:2000.0
  14. CARGOS:2500.0
  15. CARGOS:11000.0
  16. CARGOS:634.27
  17. CARGOS:1000.0
  18. CARGOS:535.0
  19. CARGOS:1000.0
  21. CARGOS:1000.0
  22. CARGOS:1000.0
  23. CARGOS:20000.0
  24. CARGOS:23000.0
  25. CARGOS:1400.0
  27. CARGOS:3200.0
  28. CARGOS:600.0
  29. CARGOS:11000.0
  30. CARGOS:1000.0
  31. CARGOS:1200.0
  33. CARGOS:12000.0
  34. CARGOS:5500.0
  35. CARGOS:2000.0
- 被忽略的交易（CARGOS为“无”或空，仅ABONOS有值）：第3、10、20、26、32行，共5笔。

(Step 4) 计算符合条件的交易总行数。
- 统计结果：数值2 = 30。

校验规则（严格按照校验规则）：
比较数值1（来自Comportamiento）和数值2（来自明细统计）是否相等。
- 数值1 = 30
- 数值2 = 30
- 比较结果：相等。

决策结果（严格按照决策结果）：
如果相等，输出一致（无异常）。
- 结论：一致。

最终判定：
根据规则，两个数值相等，判定为“一致”，因此 hit=false。

**补充说明**: 数据完整，计算过程清晰，统计笔数与系统提供的参考值及人工复核结果完全一致。

---

### 3. 明细交易金额校验_入账金额

**规则ID**: `MSTAR_BBVA_DTL_AMT_ABONOS`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 【执行步骤说明】
严格按照规则定义的判断逻辑执行：
Step 1: 从 'Comportamiento' 表格中提取 'Depósitos / Abonos (+)'（入账）对应的总金额。提取结果为：233,768.72。
Step 2: 遍历 'Detalle de Movimientos Realizados' 部分。
Step 3: 累加所有 'Abonos' 列的数值，忽略 'Cargo' 列的数值。
Step 4: 确保金额格式转换正确（处理千分位逗号）。'Comportamiento' 中的金额已去除千分位逗号。明细中的 Abonos 金额均为数值格式，无需额外转换。

【明细交易累加过程】
根据数据，有效 Abonos 交易数为 5 笔，符合规则要求列出所有明细。具体交易如下（按原始顺序）：
1. 第3笔：Abonos: 24,360.0
2. 第10笔：Abonos: 24,360.0
3. 第20笔：Abonos: 49,618.72
4. 第26笔：Abonos: 24,940.0
5. 第32笔：Abonos: 110,490.0

求和计算：
24,360.0 + 24,360.0 + 49,618.72 + 24,940.0 + 110,490.0 = 233,768.72

【校验规则执行】
比较 Step 1 的数值 (233,768.72) 与 Step 3 的累加结果 (233,768.72)。
两个数值完全相等。

【决策结果】
根据规则，两个数值相等，输出“一致”。

【最终判定】
数据一致，未发现异常。因此 hit=false。

**补充说明**: 明细中 Abonos 交易笔数（5笔）较少，已列出全部金额明细用于复核。计算总和与 Comportamiento 中报告的总入账金额完全一致。

---

### 4. 明细交易金额校验_出账金额

**规则ID**: `MSTAR_BBVA_DTL_AMT_CARGOS`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_AMT_CARGOS
规则名称: 明细交易金额校验_出账金额

**执行步骤 (严格按照判断逻辑):**
(Step 1) 从 'Comportamiento' 表格中提取 'Retiros / Cargos (-)'（出账）对应的总金额。
- 提取结果: 139,769.27 (来自数据中 'Retiros / Cargos (-): 30  139,769.27')

(Step 2) 遍历 'Detalle de Movimientos Realizados' 或raw_transaction_data部分。
- 已遍历提供的35条明细交易记录。

(Step 3) [关键过滤] 累加所有 'Cargos' 列的数值。忽略 'Abono' 列的数值。
- 根据数据，有效 Cargos (出账) 的交易数为 30 笔。
- 由于交易笔数较多（30笔），根据要求，列出前3笔和后3笔Cargos金额作为示例，并展示求和过程。
- 前3笔Cargos金额示例:
  1. 7200.0
  2. 500.0
  3. 4000.0
- 后3笔Cargos金额示例:
  28. 600.0
  29. 11000.0
  30. 1000.0
- 中间省略24笔Cargos金额明细。
- 对所有30笔Cargos金额求和。
- 求和过程: 7200.0 + 500.0 + 4000.0 + 12000.0 + 3000.0 + 300.0 + 1700.0 + 1500.0 + 1000.0 + 7000.0 + 2000.0 + 2500.0 + 11000.0 + 634.27 + 1000.0 + 535.0 + 1000.0 + 1000.0 + 1000.0 + 20000.0 + 23000.0 + 1400.0 + 3200.0 + 600.0 + 11000.0 + 1000.0 + 1200.0 + 12000.0 + 5500.0 + 2000.0 = 139,769.27
- 求和结果 (来自明细): 139,769.27

(Step 4) 确保金额格式转换正确（处理千分位逗号）。
- Comportamiento中的金额 '139,769.27' 已正确转换为数值 139769.27。
- 明细中的Cargos金额均为数值格式，无需额外转换。

**校验规则 (严格按照校验规则):**
比较1和2是否相等。
- 数值1 (来自Comportamiento): 139,769.27
- 数值2 (来自明细求和): 139,769.27
- 比较结果: 两个数值完全相等。

**决策结果 (严格按照决策结果):**
如果相等，输出一致（无异常）；如果不相等，输出不一致（异常）；
- 由于两个数值相等，因此输出“一致”。

**最终判定:**
- 数据一致，无异常。
- 根据规则，'一致' 对应 hit=false。

**补充说明**: 明细中Cargos交易笔数为30笔，与Comportamiento中记录的30笔一致。求和金额也完全匹配。验证通过。

---

### 5. 明细交易金额校验_单笔金额

**规则ID**: `MSTAR_BBVA_DTL_AMT_SINGLE`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_AMT_SINGLE
规则名称: 明细交易金额校验_单笔金额

执行步骤与结果：
1. 保持交易列表的原始顺序：已严格按照提供的35笔交易明细的原始顺序进行分析。
2. 确定初始锚点(Balance_1)：第一行交易（索引1）有'OPERACIÓN'值5183.2，将其记为Balance_1。计算起点从下一行（索引2）开始。
3. 寻找下一个锚点(Balance_2)并迭代核算：按照规则逻辑，从Balance_1开始，向下遍历找到下一个有'OPERACIÓN'或'SALDO OPERACIÓN'的行作为Balance_2，然后计算区间内Cargos和Abonos的累加和，并应用公式 result = Balance_1 - Sum(Cargos) + Sum(Abonos) - Balance_2。
4. 校验结果：根据系统提供的内部计算（Balance Check Analysis），共进行了15轮区间核算。所有轮次的result值均为0.00。具体轮次如下（作为示例）：
   - Round 1: 行[1->2]，Diff=0.00
   - Round 2: 行[2->4]，Diff=0.00
   - Round 3: 行[4->7]，Diff=0.00
   - ... (中间轮次省略，因交易笔数超过30笔且验证通过)
   - Round 13: 行[27->30]，Diff=0.00
   - Round 14: 行[30->32]，Diff=0.00
   - Round 15: 行[32->35]，Diff=0.00
5. 决策：根据校验规则，需要检查所有轮次的result值是否都为0。当前所有15轮核算的result均为0。

结论：所有区间核算结果均为0，明细交易金额连续且一致。根据决策结果，输出“一致”（无异常）。

**补充说明**: 系统提供的内部计算（Balance Check Analysis）已明确显示所有15轮核算的差异（Diff）均为0.00，结论为'所有区间校验通过'。这直接证明了规则校验逻辑的执行结果。因此，hit判定为false。

---

### 6. 交易日期校验_日期一致性

**规则ID**: `MSTAR_BBVA_DATE_CHK_CONS`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 执行步骤1：从提供的数据中获取模糊匹配包含'Periodo'的信息。找到内容为'DEL 21/06/2025 AL 20/07/2025'。解析后得到步骤1的日期区间为：[21/06/2025, 20/07/2025]。
执行步骤2：从'Detalle de Movimientos Realizados'中提取所有交易的OPER和LIQ日期。明细共35笔，所有日期如下（格式：日/月）：
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
计算最小日期(min_date)：所有日期中最早的是'21/JUN'（对应21/06/2025）。
计算最大日期(max_date)：所有日期中最晚的是'18/JUL'（对应18/07/2025）。
执行校验规则：判断步骤2中的min_date(21/06/2025)和max_date(18/07/2025)是否在步骤1的日期区间[21/06/2025, 20/07/2025]范围内。
比较结果：min_date(21/06/2025)等于区间起始日(21/06/2025)，在区间内。max_date(18/07/2025)早于区间结束日(20/07/2025)，在区间内。
决策结果：min_date和max_date均在步骤1的日期区间范围内，因此输出“一致（无异常）”。
根据决策结果，规则未命中，hit=false。

**补充说明**: 规则仅校验交易明细中的最小和最大日期是否在Periodo声明的区间内。经核对，明细日期范围[21/06/2025, 18/07/2025]完全落在Periodo区间[21/06/2025, 20/07/2025]之内，符合规则要求。

---

### 7. 交易明细分析_高风险职业

**规则ID**: `MSTAR_BBVA_DTL_ANAL_RISK_OCC`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 步骤1：取出Detalle de Movimientos Realizados中所有交易的DESCRIPCION字段值。共35笔交易，DESCRIPCION列表如下：
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

步骤2：将上述DESCRIPCION翻译成中文。翻译结果如下：
1. 自动取款机取款 JUN21 11:25 BBVA 9340 凭证号:8584
2. 信用卡还款 账户: BMOV
3. SPEI收款 SANTANDER 5292262 付款 ALMA RUTH CORONA HUERTA ... AS INTERMODAL SA DE CV
4. 信用卡还款 账户: BMOV
5. 自动取款机取款 JUN27 10:24 BBVA 9340 凭证号:1557
6. 信用卡还款 账户: BMOV
7. 信用卡还款 账户: BMOV
8. 自动取款机取款 JUN28 09:10 BBVA 6728 凭证号:1767
9. 向第三方账户付款 BNET 1500027883 汽车贷款
10. SPEI收款 SANTANDER 4039985 付款 AS ALMA RUTH CORONA HUERT ... AS INTERMODAL SA DE CV
11. 信用卡还款 账户: BMOV
12. 自动取款机取款 JUL03 11:07 BBVA 4990 凭证号:9573
13. SPEI发送 BANCOPPEL 0906250xx ... Jose Luis Aguilar
14. 向第三方账户付款 BNET 1503166940 xx
15. 自动取款机取款 JUL04 12:29 BBVA C516 凭证号:3411
16. 信用卡还款 账户: BMOV
17. 向第三方账户付款 BNET 1189291784 旅行
18. 向第三方账户付款 BNET 1500027883 Tatis
19. SPEI发送 BANCOPPEL 0906250xx ... Jose Luis Aguilar
20. 工资支付 0000300047226CP000101400
21. 向第三方账户付款 BNET 1523845844 转账给 JOSE ROBE
22. 自动取款机取款 JUL07 15:01 BBVA 4990 凭证号:1760
23. SPEI发送 BANAMEX 0906250xx ... Luis Alberto Corona Huerta
24. SPEI发送 BANORTE 0906250xx ... Alma
25. SPEI发送 BANCOPPEL 0906250xx ... Jose Luis Aguilar
26. SPEI收款 SANTANDER 6274788 付款 AS ALMA RUTH CORONA HUERT ... AS INTERMODAL SA DE CV
27. 自动取款机取款 JUL10 20:05 BBVA E934 凭证号:6021
28. 向第三方账户付款 BNET 1189291784 xx
29. 自动取款机取款 JUL11 21:00 BBVA 9340 凭证号:8887
30. 无卡取款
31. 自动取款机取款 JUL17 12:46 BBVA 9340 凭证号:1908
32. SPEI收款 SANTANDER 8409055 付款 AS ALMA RUTH CORONA HUERT ... AS INTERMODAL SA DE CV
33. 自动取款机取款 JUL18 10:23 BBVA 7690 凭证号:3685
34. SPEI发送 BANAMEX 0906250xx ... Luis Alberto Corona Huerta
35. 向第三方账户付款 BNET 1500027883 xx

校验规则：检查上述中文描述是否命中任意一个高风险职业关键词。关键词列表：现金密集型业务；小型零售商和街头摊贩（如露天市场摊贩）；夜总会；酒吧；娱乐场所经营者；灰色；非法行业关联者；未注册或非正式的安保服务提供商；涉嫌贷款翻转或文件造假的汽车贷款经纪人或中介；可能与贩毒或有组织犯罪相关的幌子企业（如虚假奢侈品转售店、空壳运输公司）；欺诈高发行业；不受监管的汽车经销商或中介，尤其是推广 “零首付” 优惠的或收入不规律或无法核实的自雇人士；在汽车金融行业工作的个人；独立或未注册的汽车维修店员工。

执行结果：逐一核对35笔交易的中文描述，未发现任何描述包含上述关键词。交易描述主要为：自动取款机取款、信用卡还款、SPEI收款/发送（来自/支付给个人或公司AS INTERMODAL SA DE CV）、工资支付、向第三方账户付款（备注包含“汽车贷款”、“旅行”等）。这些描述均不涉及关键词中定义的高风险职业。

决策结果：所有交易均未命中关键词，输出正常。

结论：根据规则MSTAR_BBVA_DTL_ANAL_RISK_OCC的校验逻辑，未发现高风险职业相关交易。hit值应判定为false（未命中/合规）。

**补充说明**: 已严格按照判断逻辑的步骤执行：1. 提取所有DESCRIPCION。2. 翻译成中文。3. 根据校验规则核对关键词。决策结果为正常，因此hit=false。

---

### 8. 交易明细分析_快进快出

**规则ID**: `MSTAR_BBVA_DTL_ANAL_FAST_IO`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_DTL_ANAL_FAST_IO
规则名称: 交易明细分析_快进快出

执行步骤与结果：
1. 步骤1：已获取Detalle de Movimientos Realizados中所有35条记录，并按OPER日期升序排序（数据已按此顺序提供）。
2. 步骤2：统计所有记录中ABONOS取值不为空的总记录数。根据数据，'有效 Abonos (入账) 的交易数'为5。因此，total_cargo_cnt = 5。
3. 步骤3-6：遍历所有记录，查找ABONOS不为空的记录作为起始行，并寻找其最近的下一个CARGOS值与ABONOS值相同的记录，计算日期间隔。
   - 第1笔Abonos（起始行）：记录3，OPER1=26/JUN，ABONOS1=24360.0。向下查找，在记录4找到CARGOS=4000.0，不匹配。继续查找，未找到CARGOS=24360.0的记录。因此，无法找到匹配的CARGOS记录，本轮次无result值。
   - 第2笔Abonos（起始行）：记录10，OPER1=03/JUL，ABONOS1=24360.0。向下查找，未找到CARGOS=24360.0的记录。本轮次无result值。
   - 第3笔Abonos（起始行）：记录20，OPER1=07/JUL，ABONOS1=49618.72。向下查找，未找到CARGOS=49618.72的记录。本轮次无result值。
   - 第4笔Abonos（起始行）：记录26，OPER1=10/JUL，ABONOS1=24940.0。向下查找，未找到CARGOS=24940.0的记录。本轮次无result值。
   - 第5笔Abonos（起始行）：记录32，OPER1=17/JUL，ABONOS1=110490.0。向下查找，未找到CARGOS=110490.0的记录。本轮次无result值。
4. 校验规则1：由于在所有5轮次中，均未找到与ABONOS值相同的CARGOS记录，因此没有任何轮次能计算出result值。result_total = 0。
5. 校验规则2：ratio = result_total / total_cargo_cnt = 0 / 5 = 0。
6. 决策结果：ratio (0) <= 0.8，因此输出“未命中快进快出（无异常）”。

关键数据：
- total_cargo_cnt (ABONOS不为空的记录数): 5
- result_total (间隔天数<=1的轮次数): 0
- ratio: 0.0

结论：根据规则逻辑，ratio为0，未超过0.8的阈值，因此判定为未命中快进快出模式，无异常。

**补充说明**: 分析严格遵循了规则定义的逻辑。核心发现是：在5笔入账（Abonos）交易发生后，均未在后续交易中找到金额相等的出账（Cargos）记录。因此，无法构成‘快进快出’模式。规则关注的是‘入账后短期内出现等额出账’的行为，本例中不存在此类行为。

---

### 9. 交易明细分析_异常备注

**规则ID**: `MSTAR_BBVA_DTL_ANAL_ABN_REM`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 执行步骤1（判断逻辑）：获取解析后Detalle de Movimientos Realizados部分的description对应的所有值。
已获取全部35笔交易的描述字段。
执行校验规则：判断所有描述值是否包含以下任意关键词：Apuesta，médico / médic，juego。
检查结果：对35条描述逐一进行关键词匹配。
- 关键词 'Apuesta'：未在任何描述中发现。
- 关键词 'médico / médic'：未在任何描述中发现。
- 关键词 'juego'：未在任何描述中发现。
决策结果：所有关键词均未命中。
结论：根据规则，全部关键词均未命中，输出正常。因此规则未命中（hit=false）。

**补充说明**: 已严格按照判断逻辑、校验规则和决策结果执行。所有交易描述中均未发现规则指定的异常关键词。

---

### 10. 交易时间校验_特殊时间段交易

**规则ID**: `MSTAR_BBVA_TIME_CHK_SPECIAL`

**命中状态**: ✅ **未命中** (合规)

**置信度**: HIGH

**判断依据**:

> 规则ID: MSTAR_BBVA_TIME_CHK_SPECIAL
规则名称: 交易时间校验_特殊时间段交易

执行步骤：
步骤1：遍历Detalle de Movimientos Realizados的35条记录，从描述(description)中提取时间。
- 记录1: "RETIRO CAJERO AUTOMATICO JUN21 11:25 BBVA 9340 FOLIO:8584" -> 提取时间: 11:25
- 记录5: "RETIRO CAJERO AUTOMATICO JUN27 10:24 BBVA 9340 FOLIO:1557" -> 提取时间: 10:24
- 记录8: "RETIRO CAJERO AUTOMATICO JUN28 09:10 BBVA 6728 FOLIO:1767" -> 提取时间: 09:10
- 记录12: "RETIRO CAJERO AUTOMATICO JUL03 11:07 BBVA 4990 FOLIO:9573" -> 提取时间: 11:07
- 记录15: "RETIRO CAJERO AUTOMATICO JUL04 12:29 BBVA C516 FOLIO:3411" -> 提取时间: 12:29
- 记录22: "RETIRO CAJERO AUTOMATICO JUL07 15:01 BBVA 4990 FOLIO:1760" -> 提取时间: 15:01
- 记录27: "RETIRO CAJERO AUTOMATICO JUL10 20:05 BBVA E934 FOLIO:6021" -> 提取时间: 20:05
- 记录29: "RETIRO CAJERO AUTOMATICO JUL11 21:00 BBVA 9340 FOLIO:8887" -> 提取时间: 21:00
- 记录31: "RETIRO CAJERO AUTOMATICO JUL17 12:46 BBVA 9340 FOLIO:1908" -> 提取时间: 12:46
- 记录33: "RETIRO CAJERO AUTOMATICO JUL18 10:23 BBVA 7690 FOLIO:3685" -> 提取时间: 10:23
- 其他记录的描述中不包含时间信息，跳过。
步骤2：将提取到的时间放入集合：{'11:25', '10:24', '09:10', '11:07', '12:29', '15:01', '20:05', '21:00', '12:46', '10:23'}。
步骤3：统计集合中处于2点至5点（含2点和5点）的交易笔数。检查每个时间：
- 11:25 -> 不在2-5点区间
- 10:24 -> 不在2-5点区间
- 09:10 -> 不在2-5点区间
- 11:07 -> 不在2-5点区间
- 12:29 -> 不在2-5点区间
- 15:01 -> 不在2-5点区间
- 20:05 -> 不在2-5点区间
- 21:00 -> 不在2-5点区间
- 12:46 -> 不在2-5点区间
- 10:23 -> 不在2-5点区间
统计结果：count = 0。

校验规则：判断 count 是否大于 10。
比较结果：count = 0，0 <= 10。

决策结果：根据规则，count <= 10，输出“正常”。

结论：未发现交易时间异常。

**补充说明**: 所有包含时间的交易记录均已检查，无交易发生在凌晨2点至5点之间。规则校验通过。

---
