# Data Foundation Build Card v1

日期：2026-04-27

状态：draft / foundation-contract / bounded-bootstrap-support

## 1. 本轮目标

本轮在 Data Foundation foundation contract 基础上，补充最小 bounded bootstrap 支撑：

```text
TDX txt -> raw_market.duckdb -> market_base_day.duckdb
```

该实现只服务 MALF day bounded proof 的输入准备，不放行完整 Data Foundation，也不占用
Alpha / Signal / Position / Portfolio / Trade / System 的主线施工位。

## 2. 本轮允许修改

```text
docs/02-modules/data/
docs/02-modules/01-data-foundation-design-v1.md
docs/02-modules/04-mainline-module-delivery-index-v1.md
docs/03-refactor/00-module-gate-ledger-v1.md
src/asteria/data/
scripts/data/run_data_bootstrap.py
tests/unit/data/
```

## 3. 本轮禁止修改

| 禁止项 | 原因 |
|---|---|
| 创建正式 Data DuckDB | 尚未进入实现与 schema gate |
| 迁移旧 data runner 代码 | 旧代码只能做参考，新实现必须遵守 Asteria contract |
| 修改 MALF 及下游语义 | Data 不能重定义主线业务语义 |
| 建立全链路 pipeline | 当前主线仍锁定 MALF day bounded proof |
| 复制旧下游 DuckDB 为正式库 | 旧下游只读旁证，不是新主线语义权威 |

## 4. 本轮交付物

本轮交付：

```text
00-authority-design-v1.md
01-semantic-contract-v1.md
02-database-schema-spec-v1.md
03-runner-contract-v1.md
04-audit-spec-v1.md
05-build-card-v1.md
```

以及一个稳定入口文档：

```text
docs/02-modules/01-data-foundation-design-v1.md
```

以及最小实现：

```text
src/asteria/data/contracts.py
src/asteria/data/tdx_text.py
src/asteria/data/schema.py
src/asteria/data/bootstrap.py
src/asteria/data/legacy_audit.py
scripts/data/run_data_bootstrap.py
```

## 5. 验收命令

本轮至少执行：

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\pytest.exe tests\unit\data -q
git diff --check
```

## 6. 下一轮建议

Data Foundation 文档补齐后，下一轮建议输出总审查清单，明确：

```text
Data / MALF / Alpha / Signal / Position / Portfolio Plan / Trade / System Readout / Pipeline
```

分别缺什么文档、缺什么 DB、下一步该补什么。
