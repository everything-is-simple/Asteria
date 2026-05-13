# V1 Usage Readout Report Card

日期：2026-05-13

状态：`passed / usage readout report generated`

## 1. 背景

`final-release-closeout-card` 已通过，Asteria 主线当前 truth 仍是 `none / terminal`。
本卡按 `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` 执行第三张
post-terminal 只读路线卡，用正式库生成第一份 v1 使用读出报告。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `v1-usage-readout-report-card-20260513-01` |
| route type | `roadmap-only / read-only / post-terminal` |
| predecessor | `v1-application-db-readiness-audit-card-20260513-01` |
| source scope | `v1-usage-validation-scope-card-20260512-01` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| formal DB root | `H:\Asteria-data` |
| scope manifest | `H:\Asteria-report\pipeline\2026-05-12\v1-usage-validation-scope-card-20260512-01\scope-manifest.json` |
| 股票池 | `31` 个申万一级行业代表股 |
| 日期范围 | `2024-01-02..2024-12-31` |
| 权限 | `read_only` |

## 4. 允许动作

- 只读读取正式 Data / MALF / Alpha / Signal / downstream / Pipeline DB。
- 汇总 MALF 结构、Alpha / Signal 机会、Position / Portfolio Plan、Trade intent / rejection、System / Pipeline readout。
- 在 `H:\Asteria-report` 生成人读报告和 machine-readable manifest。
- 在 `H:\Asteria-temp` 落 run-scoped temp manifest。
- 在 `H:\Asteria-Validated` 归档 validated zip。

## 5. 禁止动作

- 不修改、重建、补写或 promote `H:\Asteria-data`。
- 不把本卡解释成新的主线 live next card。
- 不把报告读出替代第 4 张 `v1-usage-value-decision-card` 的使用价值裁决。
- 不修复 `fill_ledger`、ST、停牌、完整上市退市或历史行业沿革 caveat。
- 不打开日更生产化或额外 System full build。

## 6. 验收口径

本卡只证明：当前 v1 正式库能被只读汇总成一份人读研究报告，并可追溯到正式 DB、
run_id 与 source lineage。是否具有真实研究使用价值，留给下一张路线卡裁决。
