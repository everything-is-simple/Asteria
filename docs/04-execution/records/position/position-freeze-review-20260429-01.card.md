# Position Freeze Review Card

日期：2026-04-29

## 1. 基本信息

| 项 | 值 |
|---|---|
| module | `position` |
| run_id | `position-freeze-review-20260429-01` |
| stage | `freeze-review / card-opened` |
| owner | `codex` |

## 2. 授权来源

Signal bounded proof 已通过。当前卡只打开 Position freeze review，不打开 Position
bounded proof、Position full build、Portfolio Plan、Trade、System Readout 或 full-chain
Pipeline。

## 3. 允许动作

- 只读审阅 `docs/02-modules/position/` 六件套。
- 对照 `H:\Asteria-data\signal.duckdb` 的 `formal_signal_ledger` 检查 Position 输入契约。
- 形成 Position freeze review 的 card、record、evidence-index、conclusion。

## 4. 禁止动作

- 不创建 `src\asteria\position`。
- 不创建 `scripts\position` runner。
- 不创建 `H:\Asteria-data\position.duckdb`。
- 不修改 Signal 历史输出。
- 不进入 Portfolio Plan / Trade / System / Pipeline 施工。
