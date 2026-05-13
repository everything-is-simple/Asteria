# V1 Usage Value Decision Card

日期：2026-05-13

状态：`passed / usage value decision completed`

## 1. 背景

`final-release-closeout-card` 已通过，Asteria 主线当前 truth 仍是 `none / terminal`。
本卡是 `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` 中第四张
post-terminal 使用验证路线卡，只读裁决当前 v1 是否具备真实研究使用价值。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `v1-usage-value-decision-card-20260513-01` |
| route type | `roadmap-only / read-only / post-terminal` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| usage readout | `H:\Asteria-report\pipeline\2026-05-13\v1-usage-readout-report-card-20260513-01\usage-readout-manifest.json` |
| downstream reference audit | `H:\Asteria-report\pipeline\2026-05-13\v1-downstream-reference-audit-20260513-01\downstream-reference-audit-manifest.json` |
| current live truth | `governance/module_gate_registry.toml` + `docs/03-refactor/00-module-gate-ledger-v1.md` + `docs/04-execution/00-conclusion-index-v1.md` |
| report root | `H:\Asteria-report` |
| validated root | `H:\Asteria-Validated` |

## 4. 允许动作

- 只读消费第 3 卡 usage readout manifest。
- 只读消费 downstream reference audit supplemental manifest。
- 分类登记 `usage blocker / strategy quality issue / source caveat / future enhancement`。
- 在 `H:\Asteria-report` 生成人读裁决报告和 machine-readable manifest。
- 在 `H:\Asteria-temp` 落 run-scoped temp manifest。
- 在 `H:\Asteria-Validated` 归档 validated zip。

## 5. 禁止动作

- 不写、不重建、不 promote `H:\Asteria-data`。
- 不把使用价值裁决扩写成收益回测。
- 不把 `fill_ledger` retained gap 伪装成真实成交闭环。
- 不接 broker，不宣称实盘自动交易能力。
- 不打开 production daily incremental activation。

## 6. 通过标准

- 明确回答：当前 v1 对真实研究是否有使用价值。
- 分类结果至少覆盖 `usage blocker / strategy quality issue / source caveat / future enhancement`。
- 当前 live next 仍保持 `none / terminal`。
- 若通过，只允许进入 `daily-incremental-production-scope-card` 作为下一张路线卡。
