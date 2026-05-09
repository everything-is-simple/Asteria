# MALF 2024 Natural-Year Coverage Repair Conclusion

日期：2026-05-09

状态：`passed`

## 1. Conclusion

`malf-2024-natural-year-coverage-repair-card-20260509-01` 已通过。当前 released MALF day
surface 的最早断点已不再卡在 `2024-01-08`：本卡对 `000020.SZ` 执行了最小 coherent
released-run repair，并正式生成：

```text
malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001
```

该 released service run 已覆盖 `2024-01-02..2024-01-05` 四个 focus trading dates，且：

```text
hard_fail_count = 0
```

## 2. Gate Result

| 项 | 结果 |
|---|---|
| repaired symbol set | `000020.SZ` |
| source filter | `day + analysis_price_line + backward` |
| source scope | `1992-04-28..2024-12-31 / symbol=000020.SZ` |
| published service scope | `2024-01-02..2024-12-31 / symbol=000020.SZ` |
| source rows | `7416` |
| Core waves | `470` |
| Core snapshots | `7416` |
| Lifespan snapshots | `7394` |
| Service WavePosition rows | `242` |
| Service latest rows | `1` |
| hard_fail_count | `0` |
| WavePosition natural key duplicate groups | `0` |
| validated evidence | `H:\Asteria-Validated\Asteria-malf-2024-natural-year-coverage-repair-card-20260509-01.zip` |
| allowed next action | `pipeline_one_year_strategy_behavior_replay_rerun_build_card` |

## 3. Boundary

- 本结论只放行最小 MALF released day surface repair，不宣称旧 `symbol_limit=20` released run 已整体重修。
- 本结论不改写现有 `system_source_manifest`，也不宣称 year replay 已 rerun。
- Alpha / Signal / Position / Portfolio Plan / Trade / System Readout 没有在本卡内重建。
- full rebuild、daily incremental、resume/idempotence 和 `v1 complete` 仍未放行。

## 4. Next

下一步唯一允许动作切换为：

```text
pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01
```
