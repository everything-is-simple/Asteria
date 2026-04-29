# Asteria 执行卡记录区

本目录负责把 repo 内正式执行闭环补齐。

它回答的不是“模块怎么设计”，也不是“当前门禁开到哪”，而是：

1. 为什么这张卡开工。
2. 这张卡实际怎么执行。
3. 证据资产放在哪里。
4. 最后结论是什么。

当前执行层权威锚点：

- `H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.md`
- `H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip`
- `H:\Asteria-Validated\Asteria-docs-code-20260429-130309.zip`
- `H:\Asteria-Validated\Asteria_System_Design_Set_v1_0`
- `H:\Asteria-Validated\Asteria_System_Design_Set_v1_0.zip`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip`

当前已打开 `Alpha bounded proof build card`；唯一允许推进的业务动作是 Alpha bounded
proof。Alpha full build 和下游模块施工仍未放行。

## 1. 与其他目录的分工

| 位置 | 负责什么 |
|---|---|
| `docs/02-modules/` | 模块定义、契约、Schema、Runner、Audit、Build Card |
| `docs/03-refactor/` | 冻结状态、门禁账本、重构施工清单 |
| `docs/04-execution/` | 执行闭环索引、执行记录、结论 |
| `H:\Asteria-report` | 报告、清单、审计摘要等真实证据 |
| `H:\Asteria-Validated` | validated zip、正式证据归档资产 |

一句话说：

```text
02-modules 定义要做什么
03-refactor 定义允不允许做
04-execution 记录这次到底怎么做完的
```

## 2. 最小闭环

每张正式执行卡都必须有四类文档：

| 文档 | 作用 |
|---|---|
| `card` | 本次执行目标、输入范围、允许动作、禁止动作 |
| `evidence-index` | 外部证据路径、关键计数、关键审计值 |
| `record` | 执行经过、关键步骤、promote 与验证记录 |
| `conclusion` | 最终裁决与对门禁的影响 |

没有这四件套，就不算 repo 内闭环完成。

## 3. 目录结构

```text
docs/04-execution/
  README.md
  00-execution-discipline-v1.md
  00-conclusion-index-v1.md
  templates/
  records/
    <module_id>/
      <run_id>.card.md
      <run_id>.evidence-index.md
      <run_id>.record.md
      <run_id>.conclusion.md
```

## 4. 命名规则

1. 执行记录按模块分目录，不按日期散铺。
2. 单卡文件统一带 `run_id`。
3. `conclusion` 是单卡唯一正式结论入口。
4. `evidence-index` 只索引和摘要，不复制大报告或二进制资产。

## 5. 当前正式记录

已闭环的 MALF proof：

- [MALF day bounded proof card](records/malf/malf-day-bounded-proof-20260428-01.card.md)
- [MALF day bounded proof evidence index](records/malf/malf-day-bounded-proof-20260428-01.evidence-index.md)
- [MALF day bounded proof record](records/malf/malf-day-bounded-proof-20260428-01.record.md)
- [MALF day bounded proof conclusion](records/malf/malf-day-bounded-proof-20260428-01.conclusion.md)

已闭环的 Alpha freeze review：

- [Alpha freeze review card](records/alpha/alpha-freeze-review-20260429-01.card.md)
- [Alpha freeze review evidence index](records/alpha/alpha-freeze-review-20260429-01.evidence-index.md)
- [Alpha freeze review record](records/alpha/alpha-freeze-review-20260429-01.record.md)
- [Alpha freeze review conclusion](records/alpha/alpha-freeze-review-20260429-01.conclusion.md)

已闭环的 governance gate：

- [governance release gate closure card](records/governance/governance-release-gate-closure-20260428-01.card.md)
- [governance release gate closure evidence index](records/governance/governance-release-gate-closure-20260428-01.evidence-index.md)
- [governance release gate closure record](records/governance/governance-release-gate-closure-20260428-01.record.md)
- [governance release gate closure conclusion](records/governance/governance-release-gate-closure-20260428-01.conclusion.md)

已闭环的 docs authority refresh：

- [docs authority refresh card](records/governance/docs-authority-refresh-20260429-01.card.md)
- [docs authority refresh evidence index](records/governance/docs-authority-refresh-20260429-01.evidence-index.md)
- [docs authority refresh record](records/governance/docs-authority-refresh-20260429-01.record.md)
- [docs authority refresh conclusion](records/governance/docs-authority-refresh-20260429-01.conclusion.md)

已闭环的 external root assets refresh：

- [external root assets refresh card](records/governance/external-root-assets-refresh-20260429-01.card.md)
- [external root assets refresh evidence index](records/governance/external-root-assets-refresh-20260429-01.evidence-index.md)
- [external root assets refresh record](records/governance/external-root-assets-refresh-20260429-01.record.md)
- [external root assets refresh conclusion](records/governance/external-root-assets-refresh-20260429-01.conclusion.md)

已闭环的 Validated root manifest refresh：

- [validated root manifest refresh card](records/governance/validated-root-manifest-refresh-20260429-01.card.md)
- [validated root manifest refresh evidence index](records/governance/validated-root-manifest-refresh-20260429-01.evidence-index.md)
- [validated root manifest refresh record](records/governance/validated-root-manifest-refresh-20260429-01.record.md)
- [validated root manifest refresh conclusion](records/governance/validated-root-manifest-refresh-20260429-01.conclusion.md)

已闭环的 MALF authority compatibility audit：

- [MALF authority compatibility audit card](records/governance/malf-authority-compatibility-audit-20260429-01.card.md)
- [MALF authority compatibility audit evidence index](records/governance/malf-authority-compatibility-audit-20260429-01.evidence-index.md)
- [MALF authority compatibility audit record](records/governance/malf-authority-compatibility-audit-20260429-01.record.md)
- [MALF authority compatibility audit conclusion](records/governance/malf-authority-compatibility-audit-20260429-01.conclusion.md)

已闭环的 Asteria system design set refresh：

- [Asteria system design set refresh card](records/governance/asteria-system-design-set-refresh-20260429-01.card.md)
- [Asteria system design set refresh evidence index](records/governance/asteria-system-design-set-refresh-20260429-01.evidence-index.md)
- [Asteria system design set refresh record](records/governance/asteria-system-design-set-refresh-20260429-01.record.md)
- [Asteria system design set refresh conclusion](records/governance/asteria-system-design-set-refresh-20260429-01.conclusion.md)

总索引：

- [execution conclusion index](00-conclusion-index-v1.md)
