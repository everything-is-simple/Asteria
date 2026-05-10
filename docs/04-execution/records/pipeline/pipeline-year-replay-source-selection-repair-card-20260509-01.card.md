# Pipeline Year Replay Source Selection Repair Card

日期：2026-05-10

状态：`passed`

## 1. 目标

在 `system-readout-2024-coverage-repair-card-20260509-01` 已真实完成之后，只修 Pipeline 的
year replay source-selection 逻辑，让 `run_year_replay_coverage_gap_diagnosis` 和后续 rerun 只读消费
released System Readout truth，而不是继续留在旧的 routing / lock 语义上。

## 2. 触发事实

| item | value |
|---|---|
| released System Readout earliest day | `2024-01-02` |
| follow-up attribution | `calendar_semantic_gap_only` |
| prepared handoff | `pipeline-system-readout-2024-coverage-repair-handoff-20260510-01` |

## 3. 允许动作

- 只修 Pipeline source-selection 归因与读取路径。
- 不改写 `system.duckdb`。
- 不打开 System full build、Pipeline semantic repair、full rebuild 或 daily incremental。

## 4. 仍然禁止

| forbidden | decision |
|---|---|
| 回写上游模块 | 禁止 |
| 重新定义 year replay 的业务语义 | 禁止 |
| v1 complete | 禁止 |

## 5. 完成标准

- 只读解析 latest released `system_readout_run` 与当前 `system_source_manifest`。
- 证明 year replay source lock 已真实指向 repaired MALF / downstream released truth。
- 在不打开 rerun、closeout 或 Stage 11 runtime 的前提下，把 live 下一卡切到 disposition decision。

## 6. 实际结果

本卡已正式执行，并把当前唯一 prepared next card 切到：

```text
pipeline-year-replay-disposition-decision-card-20260510-01
```

只读 repair 结论如下：

- released `system_readout_run` 仍是 `system-readout-bounded-proof-build-card-20260508-01`
- released observed window 已覆盖 `2024-01-02..2024-12-31`
- released MALF source run 已指向 `malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001`
- follow-up attribution 仍为 `calendar_semantic_gap_only`
- year replay disposition 现在才有资格决定 rerun、closeout，还是后续 Stage 11 队列
