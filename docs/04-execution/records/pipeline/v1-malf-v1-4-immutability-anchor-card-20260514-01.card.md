# V1 MALF v1.4 Immutability Anchor Card

日期：2026-05-14

状态：`passed / MALF v1.4 immutability anchored`

## 1. 背景

`v1-core-module-recovery-roadmap-freeze-card-20260514-01` 已冻结 core recovery / proof
路线，并把下一张 route card 切到 `v1-malf-v1-4-immutability-anchor-card`。本卡只读核对
`H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4`，输出后续 Alpha/PAS 恢复工作必须遵守的
MALF 不变量清单。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `v1-malf-v1-4-immutability-anchor-card-20260514-01` |
| route type | `roadmap-only / read-only / post-terminal / authority anchor` |
| owner | `codex` |

## 3. 输入范围

| 输入 | 用途 |
|---|---|
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` | MALF v1.4 authority package |
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4.zip` | MALF v1.4 archived authority package |
| `docs/02-modules/malf/00-authority-design-v1.md` | repo-local MALF authority bridge |
| `docs/04-execution/records/malf/malf-v1-4-core-operational-boundary-authority-sync-20260503-01.conclusion.md` | v1.4 authority sync evidence |
| `docs/04-execution/records/malf/malf-v1-4-core-runtime-sync-implementation-20260505-01.conclusion.md` | current day runtime-aligned evidence boundary |
| `docs/03-refactor/06-asteria-core-module-recovery-and-proof-roadmap-v1.md` | current core recovery route |

## 4. 授权动作

- 只读核对 MALF v1.4 package、repo MALF authority design 与既有 MALF 结论。
- 输出后续 Alpha/PAS 工作必须遵守的 MALF 不变量清单。
- 把 `v1-alpha-pas-source-inventory-card` 标记为下一张 prepared route card。
- 登记执行四件套、外部 report / manifest 与 Validated archive。
- 同步 gate ledger 与 conclusion index 的 post-terminal 路线说明。

## 5. 禁止动作

- 不修改 `governance/module_gate_registry.toml` 的 `current_allowed_next_card`。
- 不写、不 rebuild、不 promote `H:\Asteria-data`。
- 不改 MALF v1.4 语义，不改 MALF schema，不执行 MALF runtime。
- 不冻结新版 Alpha/PAS 合同，不迁移历史 Alpha/PAS 代码。
- 不打开 broker feasibility、真实账户、自动委托或实盘交易。

## 6. 通过标准

- MALF v1.4 authority anchor 已列明。
- 后续 Alpha/PAS 只能消费 MALF，不得重定义 MALF。
- 历史版本不得覆盖 MALF v1.4。
- 当前 live next 保持 `none / terminal`。
- `H:\Asteria-data` mutation 为 `no`。
