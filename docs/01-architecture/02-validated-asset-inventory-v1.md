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
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` | 现行权威设计 | 直接作为 Asteria 的 MALF 权威输入 |
| `H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.*` | 架构级剖切面研究报告 | 作为治理、历史总账、增量协议与下一阶段施工路径的分析输入 |
| `H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip` | 当前仓库文档与代码归档 | 作为 2026-04-28 release gate closure 前的正式代码/文档快照 |
| `H:\Asteria-Validated\Market-Average-Lifespan-reference` | 市场参考资料与旧工作流索引 | 作为 data/reference 辅助资料，不作为治理正文 |
| `H:\Asteria-Validated\Market-Average-Lifespan-system` | 历代系统验证快照、经验总结、回测报告 | 作为经验资产、验收旁证和历史对照，不直接迁入主线实现 |

## 3. 可直接复用

### 3.1 MALF 三份终稿

路径：

```text
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2
```

用途：

1. `MALF-Core` 的定义与定理权威。
2. `MALF-Lifespan-Stats` 的统计学权威。
3. `MALF-System-Service` 的下游接口权威。

裁决：

```text
这是 Asteria 当前唯一应被直接继承的语义权威组。
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
```

用途：

1. 记录 2026-04-28 时点对治理、主线、数据、编排四个切面的剖切面判断。
2. 作为“为什么要把多 DuckDB 视为逻辑历史总账本”的正式分析依据。
3. 作为 hard governance 落地与 release gate closure 前后的对照快照。

裁决：

```text
报告是分析输入，zip 是代码/文档快照；二者都进入 Validated。`214427` 快照之后的
repo HEAD 变更必须由 repo 内执行记录、closeout、manifest 和新的 Validated 归档补齐，
不得用旧 zip 覆盖当前仓库真相。
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

### 6.2 现在不要做

1. 不要直接迁入旧系统的 `structure / filter` 模块设计。
2. 不要把旧回测快照当成新系统正式验收基线。
3. 不要让 `Validated` 中的历史 run 资产反向决定 Asteria 当前主线。

## 7. 一句话结论

`H:\Asteria-Validated` 最有用的部分，不是可直接运行的历史系统，而是已经付过学费的边界、失败案例、验收口径和 MALF 终稿。
