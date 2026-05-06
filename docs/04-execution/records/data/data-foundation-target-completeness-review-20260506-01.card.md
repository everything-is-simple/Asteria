# Data Foundation Target Completeness Review Card

日期：2026-05-06

状态：`review-only / opened`

## 1. 基本信息

| 项 | 值 |
|---|---|
| module | `data` |
| run_id | `data-foundation-target-completeness-review-20260506-01` |
| stage | `pre-position upstream completeness review` |
| owner | `codex` |

## 2. 目标

审计 Data Foundation 是否已经从设计、实现、正式 DB 与证据层面达到最终完整目标。

## 3. 允许动作

- 只读检查 `docs/02-modules/data`、`governance`、`src/asteria/data`、`scripts/data`、`tests/unit/data`。
- 只读探针 `H:\Asteria-data` 中 Data 正式 DB。
- 记录 Data 对 Position 前置条件的真实状态。

## 4. 禁止动作

- 不重建 Data DB。
- 不扩展 reference source。
- 不修改 Data runner 或 schema。
- 不打开 MALF/Alpha/Signal/Position 施工。
