# MALF v1.4 Core Formal Rebuild Repair Record

日期：2026-05-04

run_id：`malf-v1-4-core-formal-rebuild-repair-20260504-01`

状态：`passed`

## 1. Repair Scope

- 把 MALF day formal rebuild 命中的历史正式表写入从位置式 `insert into ... values (...)`
  改为显式列名写入。
- 把 canonical column tuple 固化到 `src/asteria/malf/insert_contracts.py`。
- 只补真实命中的 day 表兼容补列，不扩大成历史正式库 migration。
- 增加“历史 promoted DB + v1.4 runner”回归测试。

## 2. Execution Sequence

1. 新增 `src/asteria/malf/insert_contracts.py`，集中定义 MALF day 各表写入列契约，并生成
   `insert into table (c1, c2, ...) values (?, ?, ...)` SQL。
2. 更新 `src/asteria/malf/bootstrap.py`，把 Core / Lifespan / Service / Audit 命中的 day
   表写入统一切到显式列名。
3. 更新 `src/asteria/malf/bootstrap_support.py`，把 `malf_core_run`、`malf_lifespan_run`、
   `malf_service_run` 的写入改为显式列名。
4. 更新 `src/asteria/malf/schema.py`，仅为真实命中的
   `malf_core_state_snapshot` 增补兼容列检查，不重写历史物理列顺序。
5. 新增 `tests/unit/malf/test_v14_legacy_promoted_tables.py`，固定覆盖旧 promoted day 表列位。
6. 运行治理、格式、类型与 MALF 单测验证，然后立即重跑正式 `closeout`，验证 repair 是否真正
   解开历史正式库的首笔写入阻塞。

## 3. Verification

| command | result |
|---|---|
| `python scripts/governance/check_project_governance.py` | `passed` |
| `ruff check . --cache-dir H:\Asteria-temp\ruff-cache` | `passed` |
| `ruff format --check . --cache-dir H:\Asteria-temp\ruff-cache` | `passed` |
| `mypy src --cache-dir H:\Asteria-temp\mypy-cache` | `passed` |
| `pytest tests/unit/malf --basetemp=H:/Asteria-temp/pytest-tmp-malf-v1-4-core-formal-rebuild-repair-20260504-01 -o cache_dir=H:/Asteria-temp/pytest-cache-malf-v1-4-core-formal-rebuild-repair-20260504-01` | `29 passed` |
| `git diff --check` | `passed` |

## 4. Formal Compatibility Proof

正式 rerun 使用：

```text
run_id = malf-v1-4-core-formal-rebuild-closeout-20260504-01
source = H:\Asteria-data\market_base_day.duckdb
targets = H:\Asteria-data\malf_core_day.duckdb / malf_lifespan_day.duckdb / malf_service_day.duckdb
```

修复后的正式写入结果：

| surface | observation |
|---|---|
| `malf_core_run` | `pivot_detection_rule_version / core_event_ordering_version / price_compare_policy / epsilon_policy` 正确落入命名列；`created_at` 保持 timestamp |
| `malf_lifespan_run` | v1.4 policy 字段正确入列；未再出现列位错写 |
| `malf_service_run` | v1.4 policy 字段正确入列；未再出现列位错写 |
| `malf_pivot_ledger` | `pivot_detection_rule_version` 正确入列；`created_at` 保持 timestamp |
| `core stage` | 已从历史首笔事务阻塞推进为 `completed` |
| `lifespan stage` | `completed` |
| `service stage` | `completed` |

## 5. Boundary Outcome

- 本卡只修复“历史 promoted DB + v1.4 runner positional insert mismatch”。
- 本卡不切换当前 runtime evidence；repair 完成时当前正式 runtime evidence 仍是
  `malf-v1-3-formal-rebuild-closeout-20260502-01`。
- repair 之后的 closeout rerun 已继续执行，但在 hard audit 处发现新的阻塞；该问题超出本卡
  “列位兼容写入”边界，必须另开后续 repair card。
