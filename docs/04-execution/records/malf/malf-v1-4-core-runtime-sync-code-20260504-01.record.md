# MALF v1.4 Core Runtime Sync Code Record

日期：2026-05-04

状态：`code-only passed`

## 1. 执行范围

本记录覆盖：

- `src/asteria/malf/` 的 contract、schema、Core、Lifespan、Service、audit、bootstrap。
- `scripts/malf/` 的 day runner 参数面。
- `tests/unit/malf/` 的 v1.4 gap 回归。
- `docs/02-modules/malf/`、`governance/module_api_contracts/malf.toml`。
- `governance/module_gate_registry.toml`、`docs/03-refactor/00-module-gate-ledger-v1.md`、`docs/04-execution/00-conclusion-index-v1.md` 与本次 execution 四件套。

## 2. 结果边界

| 项 | 结果 |
|---|---|
| formal DB rebuild | `not performed` |
| formal DB promotion | `not performed` |
| validated release evidence | `not updated` |
| current runtime evidence | `malf-v1-3-formal-rebuild-closeout-20260502-01 remains current` |
| current allowed next action | `MALF v1.4 Core formal rebuild / runtime proof closeout` |

## 3. 本次代码同步结论

- `MalfDayRequest` 已强制承载 v1.4 运行策略字段。
- Core build 已按 `bar-level break + confirmed pivot` 双流处理。
- `malf_core_state_snapshot` 已成为 Core 当前状态读取面。
- `malf_structure_ledger.reference_pivot_id` 已按上下文派生。
- `malf_candidate_ledger` 已显式记录 `candidate_event_type`。
- Lifespan / Service 已依赖 Core v1.4 事实面，不再只靠旧事件账本反推当前状态。

## 4. 验证命令

```powershell
H:\Asteria\.venv\Scripts\pytest.exe tests\unit\malf --basetemp=H:/Asteria-temp/pytest-tmp-malf-v14-all2 -o cache_dir=H:/Asteria-temp/pytest-cache-malf-v14-all2
```

其余治理与静态检查见 conclusion。

## 5. 关联入口

- [card](malf-v1-4-core-runtime-sync-code-20260504-01.card.md)
- [evidence-index](malf-v1-4-core-runtime-sync-code-20260504-01.evidence-index.md)
- [conclusion](malf-v1-4-core-runtime-sync-code-20260504-01.conclusion.md)
