# MALF Go+SQLite 版本需求文档

日期：2026-05-14

## 简介

本文档定义 MALF Go+SQLite 版本（项目代号 malf-go-sqlite）的完整需求。


## 词汇表

| 术语 | 定义 |
|---|---|
| **MALF** | Market Average Lifespan Framework，市场平均生命周期框架，本项目的核心语义框架 |
| **MALF_Go** | 本项目，MALF 的 Go + SQLite 实现 |
| **Asteria** | MALF 的 Python/DuckDB 参考实现，语义权威来源 |
| **PriceBar** | 价格 K 线，包含 symbol、timeframe、bar_dt、open、high、low、close |
| **Pivot** | 确认极值，已确认的局部高点（H）或低点（L） |
| **Primitive** | 结构原语，HH / HL / LL / LH 之一 |
| **Wave** | 波段生命，有方向、有推进、有守护、有终止的结构对象 |
| **Current_Effective_Guard** | 当前有效守护点，active wave 当前用于判断 break 的 HL 或 LH |
| **Break** | 击穿事件，当前有效守护点被价格穿越，触发旧 wave 终止 |
| **Transition** | 转换未决区，旧 wave 终止后、新 wave 确认前的系统状态 |
| **Transition_Boundary** | 转换边界，break 后由 transition 接管的上下边界 |
| **Candidate_Guard** | 候选守护点，新 wave 出生前先出现的候选 L 或 H |
| **Progress_Confirmation** | 推进确认，active candidate guard 之后突破 transition boundary 的事件 |
| **New_Wave** | 新波段，经 candidate guard + progress confirmation 共同确认的新方向性结构 |
| **System_State** | 系统状态，uninitialized / up_alive / down_alive / transition 之一 |
| **Wave_Core_State** | 波段核心状态，alive / terminated 之一，不得与 system_state 混用 |
| **Lifespan** | 生命统计层，在已确认 wave 上统计推进次数、停滞时间、历史分位、生命状态 |
| **new_count** | 推进次数，wave 生命周期内 progress primitive 被确认更新的累计次数 |
| **no_new_span** | 未推进持续时间，自上一次 progress primitive 更新以来经过的 bar 数 |
| **rank** | 历史分位，当前 wave 在同类历史样本中的排位，不是概率 |
| **life_state** | 生命状态，early / developing / extended / stagnant / terminal 之一 |
| **WavePosition** | 波段位置坐标，Core + Lifespan 合成的只读输出，供下游读取 |
| **Service** | 只读服务层，将 Core + Lifespan 合成为 WavePosition 并发布 |
| **Core_State_Snapshot** | Core 状态快照，记录当前 bar 的完整 Core 状态，用于读取和审计 |
| **pivot_detection_rule_version** | Pivot 检测规则版本，必须记录，影响 H/L 序列 |
| **core_rule_version** | Core 规则版本，必须记录，影响 wave/break/transition 语义 |
| **source_run_id** | 来源运行编号，标识输入数据来自哪次构建 |
| **run_id** | 本次运行编号，标识本次 MALF_Go 运行 |
| **SQLite_Ledger** | SQLite 账本，MALF_Go 的持久化存储单元 |
| **6A_Workflow** | Asteria 治理工作流，A1 Align → A2 Architect → A3 Act → A4 Assert → A5 Archive → A6 Advance |
| **Execution_Card** | 执行卡，记录单次施工任务的输入、输出、结论和证据 |
| **Conclusion_Index** | 结论索引，汇总所有已完成执行卡的结论 |
| **Module_Gate_Ledger** | 模块门禁账本，记录每个模块的 freeze / proof / release 状态 |
| **Bounded_Proof** | 有界证明，在有限标的和时间窗口内验证模块语义正确性 |
| **Property_Based_Test** | 属性测试，通过生成大量随机输入验证代码属性的测试方法 |
