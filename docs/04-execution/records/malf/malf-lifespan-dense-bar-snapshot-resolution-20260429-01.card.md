# MALF Lifespan Dense Bar Snapshot Resolution Card

日期：2026-04-29

状态：`opened`

## 1. 执行目标

本卡正式开启 `malf_lifespan_dense_bar_snapshot_resolution`。目标是把 MALF day
bounded proof 中已登记的 sparse/event-level Lifespan snapshot 修正为 dense
bar-level WavePosition 发布语义。

## 2. 授权范围

| 项 | 裁决 |
|---|---|
| active module | `MALF` |
| allowed work | `MALF Lifespan dense bar-level snapshot and Service WavePosition resolution` |
| source authority | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` |
| formal DB scope | `malf_lifespan_day.duckdb`; `malf_service_day.duckdb` |
| downstream construction | `not allowed` |

## 3. 不授权范围

本卡不授权 Position bounded proof、Position runner、`position.duckdb`、Portfolio /
Trade / System runner、Signal pinning 修改或 full-chain Pipeline。

## 4. 验收条件

| 检查 | 要求 |
|---|---|
| Lifespan dense snapshot | initialized symbol 每个 source bar 发布一行 |
| Service WavePosition | 跟随 dense Lifespan 发布每 bar interface |
| transition semantics | `system_state = transition`; `wave_core_state = terminated`; `direction = old_direction` |
| downstream writeback | `no` |
| governance state | current next card points to this MALF resolution card |
