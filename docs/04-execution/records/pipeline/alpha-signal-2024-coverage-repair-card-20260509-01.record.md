# Alpha-Signal 2024 Coverage Repair Record

日期：2026-05-09

## 1. 背景

`pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01`
已真实执行但仍 `blocked`。当时 repo authority 的最小剩余断点被切到
`alpha-signal-2024-coverage-repair-card-20260509-01`：MALF repaired run 已经存在，
但 released Alpha family 与 released Signal day surface 还没有把
`2024-01-02..2024-01-05` 四个 focus trading dates 继续传到下游观察链。

## 2. Formal Execution

| stage | command summary |
|---|---|
| alpha-signal repair | `run_alpha_signal_2024_coverage_repair.py --run-id alpha-signal-2024-coverage-repair-card-20260509-01` |
| followup rerun check | `run_pipeline_bounded_proof.py --module-scope year_replay_rerun --run-id alpha-signal-2024-coverage-repair-card-20260509-01-rerun-check --source-chain-release-version system-readout-bounded-proof-build-card-20260508-01 --target-year 2024` |
| temp system probe diagnosis | `run_system_readout_build(...) -> run_year_replay_coverage_gap_diagnosis(...)` on temp `system-probe.duckdb` |

## 3. Repair Result

| item | value |
|---|---|
| status | `completed / passed` |
| alpha families rewritten | `5` |
| signal hard_fail_count | `0` |
| followup rerun status | `failed / blocked` |
| followup rerun hard_fail_count | `2` |
| truthful next card | `coverage-gap-evidence-incomplete-closeout-card-20260509-01` |

## 4. Key Findings

| item | value |
|---|---|
| released Alpha BOF/TST/PB/CPB/BPB earliest day | `2024-01-02` |
| released Alpha repaired-lineage rows | `source_malf_run_id = malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001` |
| released Signal earliest day | `2024-01-02` |
| released Signal source alpha run | `alpha-production-builder-hardening-20260506-01` |
| released Position earliest day | `2024-01-09` |
| released Portfolio Plan earliest day | `2024-01-09` |
| released Trade order intent earliest day | `2024-12-31` |

这说明本卡的 Alpha / Signal repair 已经真实生效；rerun 继续 `blocked`
不是因为 repair 没落进正式 day surface，而是因为 downstream released day surface
还没有把 `2024-01-02..2024-01-05` 继续传完。

## 5. Follow-up Classification

- 直接对 live `system.duckdb` 做 rerun，只会继续看到旧的 released
  `system_source_manifest`，因此仍会把表面缺口回指到旧 MALF source lock。
- 为了避免把旧 manifest 误报成新的最小断点，本卡额外在 `H:\Asteria-temp`
  下构建了一份只读 temp `system-probe.duckdb`，让 current released MALF / Alpha / Signal /
  Position / Portfolio Plan / Trade day surface 重新汇总成观察面。
- 对这份 temp system probe 跑同一份 year replay diagnosis 后，新的首断点已经下移到
  `position`，diagnosis 推荐下一卡为：

```text
coverage-gap-evidence-incomplete-closeout-card-20260509-01
```

## 6. Decision

本卡应记为 `passed`，并把当前唯一 prepared next card 切到
`coverage-gap-evidence-incomplete-closeout-card-20260509-01`。

这一步不是直接打开 Position / Portfolio Plan / Trade full rebuild，也不是把 System / Pipeline
semantic repair 提前放行；它只是如实把“新的第一个 downstream released day break 已落到 Position”
登记成下一张 closeout 卡。

## 7. Evidence

- `H:\Asteria-report\pipeline\2026-05-09\alpha-signal-2024-coverage-repair-card-20260509-01\manifest.json`
- `H:\Asteria-report\pipeline\2026-05-09\alpha-signal-2024-coverage-repair-card-20260509-01\closeout.md`
- `H:\Asteria-Validated\Asteria-alpha-signal-2024-coverage-repair-card-20260509-01.zip`
- `H:\Asteria-temp\pipeline\alpha-signal-2024-coverage-repair-card-20260509-01\followup-system-probe\report\pipeline\2026-05-09\alpha-signal-2024-coverage-repair-card-20260509-01-system-probe-diagnosis\coverage-attribution.md`
