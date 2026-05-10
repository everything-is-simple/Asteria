# Trade 2024 Coverage Repair Record

日期：2026-05-10

run_id：`trade-2024-coverage-repair-card-20260509-01`

## 1. Inputs

- `H:\Asteria-data\portfolio_plan.duckdb`
- `H:\Asteria-data\trade.duckdb`
- `H:\Asteria-data\system.duckdb`
- `docs/04-execution/records/portfolio_plan/portfolio-plan-2024-coverage-repair-card-20260509-01.conclusion.md`
- `docs/04-execution/records/trade/trade-2024-coverage-repair-card-20260509-01.card.md`

## 2. Preflight

- 锁定当前 released `system_readout_run = system-readout-bounded-proof-build-card-20260508-01`。
- 从 `system_source_manifest` 锁定 released `portfolio_plan` run 为
  `portfolio-plan-bounded-proof-build-card-20260507-01`。
- 从同一条 manifest 链锁定 released `trade` run 为
  `trade-bounded-proof-build-card-20260507-01`。
- 只读取 released Portfolio Plan day surface 在 `2024-01-02..2024-01-05` 的 focus-window rows，
  不扩大到 System / Pipeline 正式施工。

## 3. Execution

| stage | action |
|---|---|
| resolve live locks | 读取 `system.duckdb.system_source_manifest`，确认 released Portfolio Plan / Trade source lock |
| build | 复用现有 Trade rules，在 released Trade run_id 上重算 focus-window day rows |
| rewrite | 仅删除并重写 `trade_portfolio_snapshot`、`order_intent_ledger`、`execution_plan_ledger`、`fill_ledger`、`order_rejection_ledger` 的 focus-window rows，并刷新 `trade_run`、`trade_audit` |
| audit | 复用 Trade audit，生成 `trade-day-audit-summary.json` |
| follow-up | 构造只读 probe `system.duckdb`；保留旧 `system_chain_readout`，但对 probe manifest 改锁当前正式库里最新 completed day runs，再复跑 coverage diagnosis |
| evidence | 写出 repo 四件套、`H:\Asteria-report` 证据和 `H:\Asteria-Validated` zip |

## 4. Outputs

- `H:\Asteria-report\trade\2026-05-10\trade-2024-coverage-repair-card-20260509-01\trade-day-audit-summary.json`
- `H:\Asteria-report\trade\2026-05-10\trade-2024-coverage-repair-card-20260509-01\manifest.json`
- `H:\Asteria-report\trade\2026-05-10\trade-2024-coverage-repair-card-20260509-01\closeout.md`
- `H:\Asteria-report\pipeline\2026-05-10\trade-2024-coverage-repair-card-20260509-01-followup-diagnosis\coverage-matrix.json`
- `H:\Asteria-report\pipeline\2026-05-10\trade-2024-coverage-repair-card-20260509-01-followup-diagnosis\coverage-attribution.md`
- `H:\Asteria-Validated\Asteria-trade-2024-coverage-repair-card-20260509-01.zip`

## 5. Verified Findings

- `hard_fail_count = 0`
- released Trade rejection earliest day 已前移到 `2024-01-02`
- released Trade order intent earliest day 已前移到 `2024-01-05`
- released Trade execution plan earliest day 已前移到 `2024-01-05`
- follow-up next card 已真实下移到 `system-readout-2024-coverage-repair-card-20260509-01`
- truthful attribution 已变为 `released_surface_gap:system_readout`

## 6. Semantic Finding

- released Trade 在 `2024-01-02..2024-01-04` 的 focus-window 状态是
  `rejected / no_target_exposure_before_first_admitted_day`，因此不应伪造 `order_intent`、
  `execution_plan` 或 `fill`。
- released Trade 在 `2024-01-05` 已 truthfully materialize `order_intent_ledger` 与
  `execution_plan_ledger`。
- 在该语义下，Trade focus-window released day surface 已经 truthfully 收口；新的首断点是
  System Readout。
