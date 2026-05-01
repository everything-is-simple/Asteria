# Asteria Validated 资产清单 v1

日期：2026-04-27

## 1. 目的

本文件说明 `H:\Asteria-Validated` 中的历史遗产，对 Asteria 当前重构分别有什么用。

核心原则：

```text
能当权威输入的，直接升格为权威输入。
只能当经验旁证的，保留为旁证，不反向支配新系统设计。
```

## 2. 当前目录分层

| 路径 | 资产性质 | 当前用途裁决 |
|---|---|---|
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` | 已通过实现证据的 MALF 历史权威设计 | 作为当前 complete alignment closeout 的历史语义锚点 |
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_3` | MALF v1.3 语义升级权威设计 | 作为后续 repo 文档同步与代码修订卡依据，不声明当前实现已覆盖 |
| `H:\Asteria-Validated\README.md` | Validated 根目录人读索引 | 声明 Validated 资产区职责、当前权威锚点和禁止用途 |
| `H:\Asteria-Validated\validated-asset-manifest-20260429-01.json` | Validated 根目录机器清单 | 记录顶层资产角色、大小、时间和 SHA256 |
| `H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.*` | 架构级剖切面研究报告 | 作为治理、历史总账、增量协议与下一阶段施工路径的分析输入 |
| `H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip` | 当前仓库文档与代码归档 | 作为 2026-04-28 release gate closure 前的正式代码/文档快照 |
| `H:\Asteria-Validated\Asteria-docs-code-20260429-130309.zip` | 当前系统文档与代码归档 | 作为三天重构成果的最新 docs/code 快照；其语义必须通过 repo 执行记录和 MALF 兼容审计解释 |
| `H:\Asteria-Validated\Asteria_System_Design_Set_v1_0` | 全系统权威设计整理包 | 覆盖 Data / MALF / Alpha / Signal / Position / Portfolio Plan / Trade / System Readout / Pipeline 的当前设计状态 |
| `H:\Asteria-Validated\Asteria_System_Design_Set_v1_0.zip` | 全系统权威设计整理包归档 | 与同名目录一致；作为系统级设计包 validated archive |
| `H:\Asteria-Validated\Asteria-malf-day-bounded-proof-20260428-01.zip` | MALF day 放行证据 | 证明 MALF day Core/Lifespan/Service 三库 bounded proof 已通过 |
| `H:\Asteria-Validated\Asteria-governance-release-gate-closure-20260428-01.zip` | 治理 release gate 证据 | 证明 release gate 四件套与外部 evidence 检查已落地 |
| `H:\Asteria-Validated\Asteria-docs-authority-refresh-20260429-01.zip` | 文档权威链刷新证据 | 证明 Validated 资产、repo 文档、docs sync 检查已形成闭环 |
| `H:\Asteria-Validated\Asteria-external-root-assets-refresh-20260429-01.zip` | 外部根目录资产刷新证据 | 证明 Validated / Report / Temp 三根目录分工和 inventory 已落档 |
| `H:\Asteria-Validated\Asteria-validated-root-manifest-refresh-20260429-01.zip` | Validated 根目录 manifest 刷新证据 | 证明 Validated 根 README 与机器 manifest 已落档 |
| `H:\Asteria-Validated\Market-Average-Lifespan-reference` | 市场参考资料与旧工作流索引 | 作为 data/reference 辅助资料，不作为治理正文 |
| `H:\Asteria-Validated\Market-Average-Lifespan-system` | 历代系统验证快照、经验总结、回测报告 | 作为经验资产、验收旁证和历史对照，不直接迁入主线实现 |

## 3. 可直接复用

### 3.1 MALF 权威定义包

路径：

```text
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_3
```

用途：

1. `MALF-Core` 的定义与定理权威。
2. `MALF-Lifespan-Stats` 的统计学权威。
3. `MALF-System-Service` 的下游接口权威。

裁决：

```text
v1.2 是当前已通过实现证据的历史锚点；v1.3 是后续语义升级与代码修订的权威依据。
```

### 3.2 A 股市场参考资料

路径：

```text
H:\Asteria-Validated\Market-Average-Lifespan-reference\A股市场
H:\Asteria-Validated\Market-Average-Lifespan-reference\申万行业分类
```

用途：

1. `market_meta` 设计时的行业分类来源参考。
2. A 股交易规则、涨跌停制度、停牌语义的背景资料。
3. Universe 与 objective gate 设计时的领域参考。

裁决：

```text
可进入 Data Foundation 的 reference 层，但不应直接当成代码或正式表合同。
```

### 3.3 剖切面研究报告与代码归档

路径：

```text
H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.md
H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.pdf
H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.docx
H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip
H:\Asteria-Validated\Asteria-docs-code-20260429-130309.zip
H:\Asteria-Validated\Asteria_System_Design_Set_v1_0
H:\Asteria-Validated\Asteria_System_Design_Set_v1_0.zip
```

用途：

1. 记录 2026-04-28 时点对治理、主线、数据、编排四个切面的剖切面判断。
2. 作为“为什么要把多 DuckDB 视为逻辑历史总账本”的正式分析依据。
3. 作为 hard governance 落地与 release gate closure 前后的对照快照。
4. `20260429-130309` 作为三天重构后的当前系统文档与代码快照，必须结合
   `malf-authority-compatibility-audit-20260429-01` 解释其没有偏移 MALF 权威。
5. `Asteria_System_Design_Set_v1_0` 是当前系统全模块设计整理包，明确记录 MALF
   frozen、Data foundation contract、下游 pre-gate 的当前事实。

裁决：

```text
报告是分析输入，zip 是代码/文档快照；二者都进入 Validated。`214427` 是 2026-04-28
锚点，`130309` 是 2026-04-29 当前系统快照。快照之间和快照之后的 repo HEAD 变更必须由
repo 内执行记录、closeout、manifest 和新的 Validated 归档补齐，不得用任何旧 zip 覆盖
当前仓库真相。
```

### 3.4 当前 release evidence

路径：

```text
H:\Asteria-Validated\Asteria-malf-day-bounded-proof-20260428-01.zip
H:\Asteria-Validated\Asteria-governance-release-gate-closure-20260428-01.zip
H:\Asteria-Validated\Asteria-docs-authority-refresh-20260429-01.zip
H:\Asteria-Validated\Asteria-external-root-assets-refresh-20260429-01.zip
H:\Asteria-Validated\Asteria-validated-root-manifest-refresh-20260429-01.zip
H:\Asteria-Validated\Asteria-malf-authority-compatibility-audit-20260429-01.zip
H:\Asteria-Validated\Asteria-system-design-set-refresh-20260429-01.zip
```

用途：

1. 证明 MALF day bounded proof 已经形成 repo 内四件套与外部证据。
2. 证明 release gate closure 已经把执行结论、manifest、validated zip 纳入治理检查。
3. 证明 docs authority refresh 已经把 Validated 资产锚点纳入 docs sync 检查。
4. 证明 repo 外三根目录的职责分区和资产 inventory 已经形成治理证据。
5. 证明 Validated 根目录的人读 README 与机器 manifest 已经形成治理证据。
6. 证明当前系统 docs/code 快照已按 MALF 权威目录与 zip 做兼容审计，结论为不偏移。
7. 证明全系统设计整理包已落入 Validated，并且不改变当前门禁。

裁决：

```text
这些 zip 是执行证据，不是新的业务语义来源。
它们可以改变门禁状态，不能改变 MALF 定义或下游模块边界。
```

## 4. 高价值旁证

### 4.1 core/data/malf 实战经验总结

路径：

[`battle-tested-lessons-core-data-malf-20260403.md`](H:/Asteria-Validated/Market-Average-Lifespan-system/marketlifespan-quant/battle-tested-lessons-core-data-malf-20260403.md)

价值：

1. 五目录纪律为什么是硬约束。
2. `raw -> base` 两级事实层为什么不能省。
3. `MALF` 的完整性与 freshness 为什么必须分开看。
4. DuckDB checksum 损坏、freshness 漏刷、BJ 映射缺口、复权窗口截断这些坑都是真实发生过的。

裁决：

```text
这是 Asteria 架构层的重要旁证，适合拿来写设计边界和审计规则，不适合直接复刻旧模块形态。
```

### 4.2 全模块经验总表

路径：

[`battle-tested-lessons-all-modules-and-mainline-bridging-20260408.md`](H:/Asteria-Validated/Market-Average-Lifespan-system/marketlifespan-quant/battle-tested-lessons-all-modules-and-mainline-bridging-20260408.md)

价值：

1. 清楚区分长期正式事实和 `run_id` 审计层。
2. 对 `MALF -> PAS -> position -> trade -> system` 的职责边界有过硬的实战沉淀。
3. 对 `system` 不能冒充“正式上线”这件事给了很稳的语言边界。

裁决：

```text
这是 Asteria 后续做 Alpha / Signal / Position / Trade / System 设计时的高价值旁证。
```

### 4.3 MALF 正式验证冻结快照

路径：

```text
H:\Asteria-Validated\Market-Average-Lifespan-system\marketlifespan-quant\malf-validation-freeze-current-20260326
```

价值：

1. 证明旧体系里什么被当成了 “MALF 正式验证资产”。
2. 适合作为未来 Asteria `malf day` bounded proof 之后的对照样式。
3. 可以帮助我们定义：什么样的 summary / report / source-manifest 值得进入 `Validated`。

裁决：

```text
可复用的是归档方法，不是里面的旧语义表结构。
```

### 4.4 system mainline closeout 快照

路径：

```text
H:\Asteria-Validated\Market-Average-Lifespan-system\marketlifespan-quant\system-mainline-closeout-current-20260326
```

价值：

1. 展示“系统级 closeout”作为归档对象该怎么存。
2. 可为 Asteria 未来 `system` 验收提供快照模板。

裁决：

```text
只适合作为未来 closeout 资产形态参考，不适合作为当前主线输入。
```

### 4.5 readiness 与历史信件

路径：

[`v001-launch-readiness-checklist-20260403.md`](H:/Asteria-Validated/Market-Average-Lifespan-system/marketlifespan-quant/v001-launch-readiness-checklist-20260403.md)

[`letter-to-v001-from-lifespan-quant-20260405.md`](H:/Asteria-Validated/Market-Average-Lifespan-system/marketlifespan-quant/letter-to-v001-from-lifespan-quant-20260405.md)

价值：

1. `readiness checklist` 给了“什么不该叫正式上线”的成熟口径。
2. 那封“来自下一代的信”点明了一个很重要的历史分叉：旧系统把 `structure / filter` 拉成独立层，而 Asteria 现在已经决定把结构语义收回 MALF。

裁决：

```text
语言边界可参考，架构路线不可直接照搬。
```

## 5. 低直接复用价值

### 5.1 workflow 索引壳

路径：

[`6A工作流.md`](H:/Asteria-Validated/Market-Average-Lifespan-reference/workflows/6A工作流.md)

[`RIPER-5_With_Conditional_Review_Gate_CN.md`](H:/Asteria-Validated/Market-Average-Lifespan-reference/workflows/RIPER-5_With_Conditional_Review_Gate_CN.md)

裁决：

这两份现在只是索引壳，正文已经不在这里。

```text
不适合当 Asteria 的治理正文来源。
```

### 5.2 旧回测报告目录

路径：

```text
...bof-16cell-three-year-official-current-20260326
...pb-16cell-three-year-official-current-20260327
...simple-five-case-2010-2013-strategy-calendar-current-20260406
...legacy-emotionquant-gamma\...
```

裁决：

这些资产有历史研究价值，但对 Asteria 当前“先定主线、再做 MALF 第一模块”的帮助有限。

```text
保留，不进入当前重构主路径。
```

## 6. 当前可执行用法

### 6.1 现在就该用

1. 把 `MALF_Three_Part_Design_Set_v1_2` 继续作为 MALF 唯一权威输入。
2. 把 `battle-tested-lessons-core-data-malf-20260403.md` 作为 `data / malf` 设计评审旁证。
3. 把 `battle-tested-lessons-all-modules-and-mainline-bridging-20260408.md` 作为未来下游模块边界参考。
4. 把 `A股市场` 与 `申万行业分类` 作为 `market_meta` 的 reference 资料池。
5. 把五份当前 release / governance evidence zip 作为门禁状态证明。
6. 使用 `README.md` 和 `validated-asset-manifest-20260429-01.json` 快速判断 Validated 顶层资产职责。
7. 把剖切面研究报告作为逻辑历史总账、每日增量、pipeline ledger 的架构依据。
8. 把 `Asteria-docs-code-20260429-130309.zip` 作为当前系统 docs/code 快照，但只通过
   repo 执行结论和 MALF 兼容审计解释其状态。
9. 把 `Asteria_System_Design_Set_v1_0` 作为全系统当前设计状态入口，不把它解释为
   Alpha 或下游施工许可。

### 6.2 现在不要做

1. 不要直接迁入旧系统的 `structure / filter` 模块设计。
2. 不要把旧回测快照当成新系统正式验收基线。
3. 不要让 `Validated` 中的历史 run 资产反向决定 Asteria 当前主线。
4. 不要把 release evidence zip 当作可直接迁移的模块代码。

## 7. 一句话结论

`H:\Asteria-Validated` 最有用的部分，不是可直接运行的历史系统，而是已经付过学费的边界、失败案例、验收口径和 MALF 终稿。
