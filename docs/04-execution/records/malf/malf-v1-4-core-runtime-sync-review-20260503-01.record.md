# MALF v1.4 Core 运行同步评审记录

run_id: `malf-v1-4-core-runtime-sync-review-20260503-01`

prepared_card_date: 2026-05-03

execution_date: 2026-05-04

status: `只读评审已执行 / 运行同步未打开`

## 1. 执行范围

本次执行对照当前权威定义包、repo 实现与 live MALF day Core schema，
完成了 MALF v1.4 Core 运行同步准备卡的评审。

本次执行是 review-only。它没有修改 Python 代码，没有迁移 schema，没有重建 DuckDB，
没有 promote formal data，没有运行 MALF 运行证明，也没有改变当前主线允许的下一张卡。

## 2. 已读取输入

| 输入 | 目的 |
|---|---|
| `README.md` | 当前 Asteria 权威状态与允许的下一步动作 |
| `docs/00-governance/00-asteria-refactor-charter-v1.md` | 主线与模块施工规则 |
| `docs/01-architecture/00-mainline-authoritative-map-v1.md` | MALF 边界与下游锁定关系 |
| `docs/01-architecture/01-database-topology-v1.md` | 当前 MALF day DB 状态与目标拓扑 |
| `docs/03-refactor/00-module-gate-ledger-v1.md` | 当前模块门禁状态 |
| `docs/04-execution/00-conclusion-index-v1.md` | 当前执行结论状态 |
| `docs/04-execution/records/malf/malf-v1-4-core-runtime-sync-review-20260503-01.card.md` | 准备态运行同步评审卡 |
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` | MALF v1.4 权威定义包 |
| `src/asteria/malf/core_engine.py` | 当前 Core 实现真相 |
| `src/asteria/malf/schema.py` | 当前 Core schema bootstrap 真相 |
| `src/asteria/malf/contracts.py` | 当前 request 合同真相 |
| `src/asteria/malf/bootstrap.py` | 当前 runner 持久化真相 |
| `H:\Asteria-data\malf_core_day.duckdb` | 当前 live MALF day Core DB schema 真相 |

## 3. 评审命令

```powershell
Select-String -Path 'src\asteria\malf\core_engine.py','src\asteria\malf\schema.py','src\asteria\malf\contracts.py','src\asteria\malf\bootstrap.py' -Pattern 'def _advance_or_break|def _derive_structures|latest_by_type|pivot_detection_rule_version|core_event_ordering_version|price_compare_policy|epsilon_policy|malf_core_state_snapshot|candidate_event_type|invalidated_by_candidate_id|def _candidate_from_pivot'
```

实现层观察证据：

```text
core_engine.py 包含 `_derive_structures`，其 reference 选择使用 `latest_by_type`。
core_engine.py 包含 `_advance_or_break`，这是当前生效的 break 路径。
core_engine.py 记录了 `invalidated_by_candidate_id`，但没有 `candidate_event_type`。
schema.py 与 contracts.py 仍未暴露 `pivot_detection_rule_version`、`core_event_ordering_version`、`price_compare_policy`、`epsilon_policy`、`malf_core_state_snapshot`。
```

```powershell
@'
from pathlib import Path
import duckdb

core_db = Path(r'H:\Asteria-data\malf_core_day.duckdb')
with duckdb.connect(str(core_db), read_only=True) as con:
    tables = [
        row[0]
        for row in con.execute(
            "select table_name from information_schema.tables "
            "where table_schema='main' order by table_name"
        ).fetchall()
    ]
    print(tables)
'@ | H:\Asteria\.venv\Scripts\python.exe -
```

live schema 观察证据：

```text
tables=malf_break_ledger,malf_candidate_ledger,malf_core_run,malf_pivot_ledger,malf_schema_version,malf_structure_ledger,malf_transition_ledger,malf_wave_ledger
watched_columns_present=
has_malf_core_state_snapshot=False
```

## 4. 评审发现

| 优先级 | 目标 | 发现 |
|---|---|---|
| P0 | bar-level break 判定 | 尚未完成运行同步。v1.4 authority 规定 break 来自原始 `bar_low` / `bar_high`，而当前实现路径仍通过 `_advance_or_break` 走 pivot 驱动。 |
| P0 | `malf_core_state_snapshot` | 缺失。当前 Core live DB 只有事件账本，没有专门的 Core 状态快照表。 |
| P1 | O1/O2/O3 运行账本字段 | 缺失。当前 request、run ledger、pivot ledger 与 live DB schema 都没有承接这些 v1.4 policy/version 字段。 |
| P1 | 上下文化 structure reference | 尚未完成运行同步。当前 `_derive_structures` 仍通过 `latest_by_type` 使用全局 latest same-type pivot reference。 |
| P2 | candidate 事件类型 | 只有部分失效链路表达。当前没有显式 candidate event type 去区分 created、same-direction refresh、opposite-direction replacement 与 confirmed。 |

## 5. 边界检查

| 边界项 | 结果 |
|---|---|
| Python code edits | 未执行 |
| DuckDB schema migration | 未执行 |
| Formal DB rebuild | 未执行 |
| MALF 运行证明 | 未执行 |
| MALF week/month proof | 未执行 |
| Global gate registry update | 未执行 |
| Module gate ledger update | 未执行 |
| Conclusion index update | 已做 review-only 登记；未改变 gate 状态 |
| Downstream construction | 未打开 |

## 6. 记录结论

本次评审确认：MALF v1.4 Core authority 已经足够支撑后续运行同步，
但当前 repo/runtime surface 还不是完整的 v1.4 Core runtime closure。

当前允许的下一步业务动作仍为：

```text
Position freeze review reentry / review-only
```
