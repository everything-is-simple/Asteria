# Alpha/PAS Source Inventory Evidence Index

日期：2026-05-14

## 1. Repo Evidence

| asset | role |
|---|---|
| `docs/03-refactor/06-asteria-core-module-recovery-and-proof-roadmap-v1.md` | route authority and card order |
| `docs/03-refactor/07-alpha-pas-source-inventory-v1.md` | source inventory output |
| `docs/03-refactor/00-module-gate-ledger-v1.md` | post-terminal route status sync |
| `docs/04-execution/00-conclusion-index-v1.md` | conclusion registration |
| `governance/module_gate_registry.toml` | live terminal truth, unchanged |
| `docs/02-modules/alpha/` | current Alpha six-doc surface |
| `src/asteria/alpha/` | current Alpha implementation surface |
| `scripts/alpha/` | current Alpha runner surface |
| `tests/unit/alpha/` | current Alpha regression surface |
| `docs/04-execution/records/alpha/` | current Alpha evidence records |

## 2. External Source Roots

| source root | status |
|---|---|
| `G:\malf-history\astock_lifespan-alpha` | exists |
| `G:\malf-history\EmotionQuant-alpha` | exists |
| `G:\malf-history\EmotionQuant-beta` | exists |
| `G:\malf-history\EmotionQuant-gamma` | exists |
| `G:\malf-history\lifespan-0.01` | exists |
| `G:\malf-history\Lifespan-Validated` | exists |
| `G:\malf-history\MarketLifespan-Quant` | exists |
| `H:\Asteria-Validated\MALF-system-history` | exists |
| `G:\《股市浮沉二十载》\2020.(Au)LanceBeggs` | exists |
| `G:\《股市浮沉二十载》\2021.Bob_Volman外汇超短线交易` | exists |
| `G:\《股市浮沉二十载》\2018.(CHINA)简简单单做股票` | exists |

### 2.1 Book Chapter Anchors

| source | anchor | evidence role |
|---|---|---|
| `G:\《股市浮沉二十载》\2020.(Au)LanceBeggs\YTC卷2：市场和市场分析\YTC卷2：市场和市场分析-markdowns\YTC卷2：市场和市场分析_20260321_124128.md` | 第 3 章，尤其 3.3 / 3.5 / 3.6 | strength / weakness and ongoing market analysis source anchor |
| `G:\《股市浮沉二十载》\2020.(Au)LanceBeggs\YTC卷3：交易策略\YTC卷3：交易策略_ocr_results\YTC卷3：交易策略_20260321_124515.md` | 第 4 / 5 章 | setup family and trading example source anchor |

本卡只记录章节锚点，不复制书籍正文。下一卡必须把书中“当前价格行为是否支持预期”的
行进中分析，与 Asteria 的 MALF completed-wave baseline 分开表达。

### 2.2 Historical PAS Anchors

| source | anchor | evidence role |
|---|---|---|
| `G:\malf-history\MarketLifespan-Quant\src\mlq\alpha\pas\contracts.py` | PAS five-trigger summaries, trigger ledger, formal signal, 16-cell readout | trigger / formal candidate / historical rank source anchor |
| `G:\malf-history\MarketLifespan-Quant\src\mlq\core\contracts.py` | `BOF / BPB / PB / TST / CPB` public vocabulary | setup family vocabulary source anchor |
| `G:\malf-history\MarketLifespan-Quant\docs\04-reference\battle-tested-lessons-all-modules-and-mainline-bridging-20260408.md` | trigger detection vs formal signal vs downstream ownership | boundary and anti-migration source anchor |
| `G:\malf-history\EmotionQuant-gamma\WARP.md` | T+1 Open, IRS ranking, MSS sidecar, BOF-only mainline | execution hint and ranking sidecar source anchor |
| `G:\malf-history\astock_lifespan-alpha\docs\02-spec\03-alpha-pas-trigger-semantic-spec-v1-20260419.md` | early Alpha/PAS trigger semantic spec | legacy trigger vocabulary source anchor |

These anchors support `sufficient_for_definition`, not direct code migration,
profit proof, or broker readiness.

## 3. External Evidence

| asset | path |
|---|---|
| report | `H:\Asteria-report\pipeline\2026-05-14\v1-alpha-pas-source-inventory-card-20260514-01\alpha-pas-source-inventory-report.md` |
| manifest | `H:\Asteria-report\pipeline\2026-05-14\v1-alpha-pas-source-inventory-card-20260514-01\alpha-pas-source-inventory-manifest.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-v1-alpha-pas-source-inventory-card-20260514-01.zip` |

## 4. Non-Evidence

本卡 evidence 不证明：

- 新版 Alpha/PAS contract 已冻结。
- 历史代码可以迁移。
- 书籍内容可以复制进 repo。
- T+1 open return proof 已改善。
- broker adapter feasibility 可以进入 live queue。
- 历史 PAS 代码可以不经 authority map 和 contract redesign 直接迁移。
- Alpha/PAS 已证明收益或可接真实 broker。

当前 live next 仍为 `none / terminal`。
