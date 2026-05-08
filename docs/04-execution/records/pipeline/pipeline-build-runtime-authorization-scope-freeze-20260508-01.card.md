# Pipeline Build/Runtime Authorization Scope Freeze Card

日期：2026-05-08

状态：`passed / scope frozen`

## 1. 背景

`pipeline-freeze-review-20260508-01` 已通过，Pipeline 六件套已经冻结为 orchestration-only 文档合同表面。
当前问题不再是“能不能直接开跑 full-chain”，而是必须先把下一步 runtime 授权范围钉死，避免把
freeze review passed 误解释成 `single-module orchestration build`、`full-chain dry-run` 与
`full-chain bounded proof` 同时放行。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `pipeline-build-runtime-authorization-scope-freeze-20260508-01` |
| stage | `authorization-scope-freeze / passed / scope frozen` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| source conclusion | `docs/04-execution/records/pipeline/pipeline-freeze-review-20260508-01.conclusion.md` |
| source evidence | `docs/04-execution/records/pipeline/pipeline-freeze-review-20260508-01.evidence-index.md` |
| scope question | `single-module orchestration build vs full-chain dry-run vs full-chain bounded proof` |
| current registry truth | `governance/module_gate_registry.toml` |
| pipeline docs | `docs/02-modules/pipeline/00-authority-design-v1.md` through `05-build-card-v1.md` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `orchestration-only; no business-semantic rewrite` |
| formal DB permission | `not created or modified by this scope card` |
| allowed next action before card | `none; explicit governance reentry for authorization-scope freeze only` |

## 5. 允许动作

- 复核 Pipeline freeze review 结论、六件套和当前 live authority。
- 决定下一张明确授权卡只允许哪一种 Pipeline runtime 范围。
- 输出 prepared next card，并把 full-chain dry-run / bounded proof 继续保留为后续新卡。
- 同步 gate ledger、conclusion index、registry、pipeline docs 和治理测试。

## 6. 禁止动作

- 不创建 `H:\Asteria-data\pipeline.duckdb`。
- 不创建 `src\asteria\pipeline` 或 `scripts\pipeline`。
- 不执行 single-module orchestration build、full-chain dry-run 或 full-chain bounded proof。
- 不修改任何业务模块代码、DB 或正式输出。
- 不把 `Pipeline freeze review passed` 偷换成 `Pipeline runtime passed`。

## 7. 后续门禁

本卡只冻结范围，不执行 runtime。通过后唯一允许恢复的下一张卡是：

```text
pipeline-single-module-orchestration-build-card-20260508-01
```

## 8. 关联入口

- [Pipeline freeze review conclusion](pipeline-freeze-review-20260508-01.conclusion.md)
- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
- [conclusion index](../../00-conclusion-index-v1.md)
