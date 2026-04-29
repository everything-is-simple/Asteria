# Alpha Bounded Proof Build Card

日期：2026-04-29

## 1. 背景

MALF day bounded proof 已通过，`malf_service_day.duckdb` 已发布 Alpha 可只读消费的
WavePosition。Alpha freeze review 已通过并冻结 Alpha 六件套。当前卡打开的唯一目标是
授权 Alpha bounded proof 施工，不打开 Alpha full build、Signal、Pipeline 或任何下游模块。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `alpha` |
| run_id | `alpha-bounded-proof-build-card-20260429-01` |
| stage | `bounded-proof / build-card-opened` |
| source DB | `H:\Asteria-data\malf_service_day.duckdb` |
| timeframe | `day` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| upstream release | `MALF day bounded proof passed` |
| freeze review | `alpha-freeze-review-20260429-01` |
| source tables | `malf_wave_position`; `malf_wave_position_latest`; `malf_interface_audit` |
| source boundary | `read-only MALF WavePosition` |
| bounded scope | `day / bounded sample only` |
| working path | `H:\Asteria-temp\alpha\<run_id>\` |
| formal DB path | `H:\Asteria-data` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| frozen docs | `docs/02-modules/alpha/00-authority-design-v1.md` through `05-build-card-v1.md` |
| release conclusion | `docs/04-execution/records/alpha/alpha-freeze-review-20260429-01.conclusion.md` |
| upstream semantics | `MALF defines structure and position; Alpha interprets opportunity` |
| formal DB permission | `allowed only for Alpha bounded proof and audit under this card` |
| allowed run modes | `bounded`; `resume`; `audit-only` |

## 5. 允许动作

- 创建 Alpha bounded proof runner 和 family audit runner。
- 为 BOF / TST / PB / CPB / BPB 执行 bounded proof 所需的 working DB、checkpoint、run ledger 和 audit 输出。
- 在 bounded proof/audit 路径明确需要时，创建五个正式 Alpha family DB：
  `alpha_bof.duckdb`、`alpha_tst.duckdb`、`alpha_pb.duckdb`、`alpha_cpb.duckdb`、
  `alpha_bpb.duckdb`。
- Alpha 输出表面仅限 `alpha_family_run`、`alpha_schema_version`、`alpha_rule_version`、
  `alpha_event_ledger`、`alpha_score_ledger`、`alpha_signal_candidate` 和
  `alpha_source_audit`。
- 生成 Alpha bounded proof evidence、record、evidence-index 和 conclusion。

## 6. 禁止动作

- 不运行 Alpha full build、segmented production build 或 daily incremental build。
- 不创建 Signal / Position / Portfolio Plan / Trade / System / Pipeline 正式 runner。
- 不创建 Signal / Position / Portfolio Plan / Trade / System / Pipeline 正式 DB。
- 不建立 full-chain pipeline runtime。
- 不迁移旧 Alpha engine 为正式语义权威。
- 不允许 Alpha 或任何下游模块写回 MALF。
- 不允许 Alpha 自定义、合并或重定义 `wave_core_state` 与 `system_state`。
- 不输出 `position_size`、`target_weight`、`portfolio_allocation`、`order_intent` 或
  `fill` 语义。

## 7. 验收与后续门禁

本卡打开后，下一步只允许执行 Alpha bounded proof。Alpha bounded proof 必须形成完整四件套：

```text
card
record
evidence-index
conclusion
```

Alpha bounded proof release gate 通过后，才允许进入：

```text
Signal freeze review
```

## 8. 验收命令

本卡和门禁状态更新后必须运行：

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
```

Alpha bounded proof release gate 前还必须运行：

```powershell
H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache
H:\Asteria\.venv\Scripts\pytest.exe --basetemp=H:/Asteria-temp/pytest-tmp-alpha-bounded-proof-20260429-01 -o cache_dir=H:/Asteria-temp/pytest-cache-alpha-bounded-proof-20260429-01
```

## 9. 关联入口

- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
- [conclusion index](../../00-conclusion-index-v1.md)
- [Alpha authority design](../../../02-modules/alpha/00-authority-design-v1.md)
- [Alpha semantic contract](../../../02-modules/alpha/01-semantic-contract-v1.md)
- [Alpha database schema spec](../../../02-modules/alpha/02-database-schema-spec-v1.md)
- [Alpha runner contract](../../../02-modules/alpha/03-runner-contract-v1.md)
- [Alpha audit spec](../../../02-modules/alpha/04-audit-spec-v1.md)
- [Alpha freeze review conclusion](alpha-freeze-review-20260429-01.conclusion.md)
