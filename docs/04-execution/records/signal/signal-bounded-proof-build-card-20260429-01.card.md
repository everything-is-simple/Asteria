# Signal Bounded Proof Build Card

日期：2026-04-29

## 1. 背景

Signal freeze review 已通过，Signal 六件套已冻结为 `frozen / freeze review passed`。
当前卡只打开 Signal bounded proof 的施工授权，不打开 Signal full build、下游模块施工
或全链路 pipeline。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `signal` |
| run_id | `signal-bounded-proof-build-card-20260429-01` |
| stage | `bounded-proof / build-card-opened` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| upstream release | `Alpha bounded proof passed` |
| freeze review | `signal-freeze-review-20260429-01` |
| source DBs | `H:\Asteria-data\alpha_bof.duckdb`; `H:\Asteria-data\alpha_tst.duckdb`; `H:\Asteria-data\alpha_pb.duckdb`; `H:\Asteria-data\alpha_cpb.duckdb`; `H:\Asteria-data\alpha_bpb.duckdb` |
| source tables | `alpha_signal_candidate`; `alpha_source_audit` |
| source boundary | `read-only released Alpha signal candidates` |
| bounded scope | `day / bounded sample only` |
| working path | `H:\Asteria-temp\signal\<run_id>\` |
| formal DB path | `H:\Asteria-data` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| frozen docs | `docs/02-modules/signal/00-authority-design-v1.md` through `05-build-card-v1.md` |
| release conclusion | `docs/04-execution/records/signal/signal-freeze-review-20260429-01.conclusion.md` |
| upstream semantics | `Alpha interprets opportunity; Signal aggregates intent` |
| formal DB permission | `allowed only after this card is implemented as bounded proof evidence` |
| allowed run modes | `bounded`; `resume`; `audit-only` |

## 5. 允许动作

- 创建 Signal bounded proof 所需的最小 runner、schema、audit 和测试。
- 只读消费五个 Alpha family DB 的 released bounded proof 表面。
- 在 bounded proof/audit 路径明确需要时，创建 `H:\Asteria-data\signal.duckdb`。
- 生成 Signal bounded proof card、record、evidence-index、conclusion、report closeout 和
  validated evidence。

## 6. 禁止动作

- 不运行 Signal full build、segmented production build 或 daily incremental build。
- 不创建 Position / Portfolio Plan / Trade / System / Pipeline 正式 runner。
- 不创建 Position / Portfolio Plan / Trade / System / Pipeline 正式 DB。
- 不建立 full-chain pipeline runtime。
- 不迁移旧 Signal engine 为正式语义权威。
- 不允许 Signal 修改 Alpha DB 或回写 MALF。
- 不允许 Signal 重新定义 Alpha candidate、MALF WavePosition、`wave_core_state` 或
  `system_state`。
- 不输出 `position_size`、`target_weight`、`portfolio_allocation`、`order_intent` 或
  `fill` 语义。

## 7. 验收与后续门禁

本卡打开后，下一步只允许执行 Signal bounded proof。Signal bounded proof 必须形成完整四件套：

```text
card
record
evidence-index
conclusion
```

Signal bounded proof release gate 通过后，才允许进入 Position freeze review 或下一张明确
授权的主线卡。

## 8. 验收命令

本卡和门禁状态更新后必须运行：

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
```

Signal bounded proof release gate 前还必须运行：

```powershell
H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache
H:\Asteria\.venv\Scripts\pytest.exe --basetemp=H:/Asteria-temp/pytest-tmp-signal-bounded-proof-20260429-01 -o cache_dir=H:/Asteria-temp/pytest-cache-signal-bounded-proof-20260429-01
```

## 9. 关联入口

- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
- [conclusion index](../../00-conclusion-index-v1.md)
- [Signal authority design](../../../02-modules/signal/00-authority-design-v1.md)
- [Signal semantic contract](../../../02-modules/signal/01-semantic-contract-v1.md)
- [Signal database schema spec](../../../02-modules/signal/02-database-schema-spec-v1.md)
- [Signal runner contract](../../../02-modules/signal/03-runner-contract-v1.md)
- [Signal audit spec](../../../02-modules/signal/04-audit-spec-v1.md)
- [Signal freeze review conclusion](signal-freeze-review-20260429-01.conclusion.md)
