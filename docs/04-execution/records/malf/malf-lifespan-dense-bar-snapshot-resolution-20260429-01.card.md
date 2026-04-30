# MALF Lifespan Dense Bar Snapshot Resolution Card

日期：2026-04-30

状态：`passed`

## 1. 执行目标

本卡闭环 `malf_lifespan_dense_bar_snapshot_resolution`。目标是把 MALF day
bounded proof 中已登记的 sparse/event-level Lifespan snapshot 修正为 dense
bar-level WavePosition 发布语义，并形成正式 run evidence。

## 2. 授权范围

| 项 | 裁决 |
|---|---|
| active module | `MALF` |
| allowed work | `MALF Lifespan dense bar-level snapshot and Service WavePosition resolution` |
| source authority | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` |
| run_id | `malf-lifespan-dense-bar-snapshot-resolution-20260429-01` |
| formal DB scope | `malf_lifespan_day.duckdb`; `malf_service_day.duckdb` |
| downstream construction | `not allowed` |

## 3. 不授权范围

本卡不授权 Position bounded proof、Position runner、`position.duckdb`、Portfolio /
Trade / System runner、Signal pinning 修改或 full-chain Pipeline。

## 4. 验收结果

| 检查 | 结果 |
|---|---|
| Lifespan dense snapshot | `passed` |
| Service WavePosition | `passed` |
| transition semantics | `passed` |
| downstream writeback | `no` |
| hard audit | `hard_fail_count = 0` |
| allowed next action | `Position freeze review reentry` |
