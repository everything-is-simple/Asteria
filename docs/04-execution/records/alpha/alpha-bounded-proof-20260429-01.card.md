# Alpha Bounded Proof Card

日期：2026-04-29

## 1. 背景

MALF day bounded proof 已通过并发布 `malf_service_day.duckdb`。Alpha freeze review
已冻结 Alpha 六件套，Alpha bounded proof build card 已打开。本卡执行该 bounded proof，
只证明 Alpha family DB / runner / audit / evidence 链路，不打开 Alpha full build 或下游施工。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `alpha` |
| run_id | `alpha-bounded-proof-20260429-01` |
| stage | `bounded-proof` |
| source DB | `H:\Asteria-data\malf_service_day.duckdb` |
| timeframe | `day` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| source tables | `malf_wave_position`; `malf_wave_position_latest`; `malf_interface_audit` |
| source boundary | `read-only MALF WavePosition` |
| service version | `service-v1` |
| bounded scope | `day / 2024-01-01..2024-12-31 / symbol_limit=4` |
| rule scope | `WavePosition-only minimal Alpha family rules` |

## 4. 允许动作

- 创建 BOF / TST / PB / CPB / BPB 五个 Alpha family DB。
- 写入 Alpha 七表：run、schema version、rule version、event、score、candidate、source audit。
- 跑 `bounded`、`resume`、`audit-only` runner 能力。
- 生成 report closeout、manifest、family audit summary 和 Validated evidence zip。

## 5. 禁止动作

- 不运行 Alpha full build、segmented production build 或 daily incremental build。
- 不创建 Signal / Position / Portfolio Plan / Trade / System / Pipeline runner 或正式 DB。
- 不输出 `position_size`、`target_weight`、`order_intent_id`、portfolio allocation 或 fill。
- 不回写 MALF，不重定义 `wave_core_state` 或 `system_state`。

## 6. 关联入口

- [record](alpha-bounded-proof-20260429-01.record.md)
- [evidence-index](alpha-bounded-proof-20260429-01.evidence-index.md)
- [conclusion](alpha-bounded-proof-20260429-01.conclusion.md)
