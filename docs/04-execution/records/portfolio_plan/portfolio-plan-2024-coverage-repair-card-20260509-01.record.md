# Portfolio Plan 2024 Coverage Repair Record

日期：2026-05-10

run_id：`portfolio-plan-2024-coverage-repair-card-20260509-01`

## 1. Inputs

- `H:\Asteria-data\position.duckdb`
- `H:\Asteria-data\portfolio_plan.duckdb`
- `H:\Asteria-data\trade.duckdb`
- `H:\Asteria-data\system.duckdb`
- `docs/04-execution/records/position/position-2024-coverage-repair-card-20260509-01.conclusion.md`
- `docs/04-execution/records/portfolio_plan/portfolio-plan-2024-coverage-repair-card-20260509-01.card.md`

## 2. Preflight

- 锁定当前 released `system_readout_run = system-readout-bounded-proof-build-card-20260508-01`。
- 从 `system_source_manifest` 锁定 released `portfolio_plan` run 为
  `portfolio-plan-bounded-proof-build-card-20260507-01`。
- 从同一条 manifest 链锁定 released `position` run 为
  `position-bounded-proof-build-card-20260506-01`。
- 从同一条 manifest 链锁定 released `trade` run 为
  `trade-bounded-proof-build-card-20260507-01`。
- 只读取 released Position day surface 在 `2024-01-02..2024-01-05` 的 focus-window rows，
  不扩大到 Trade / System / Pipeline runtime 施工。

## 3. Execution

| stage | action |
|---|---|
| resolve live locks | 读取 `system.duckdb.system_source_manifest`，确认 released Portfolio Plan / Position / Trade source lock |
| build | 复用现有 Portfolio Plan rules，在 released Portfolio Plan run_id 上重算 focus-window day rows |
| rewrite | 仅删除并重写 `portfolio_position_snapshot`、`portfolio_admission_ledger`、`portfolio_target_exposure`、`portfolio_trim_ledger` 的 focus-window day rows，并同步刷新 `portfolio_constraint_ledger`、`portfolio_plan_run`、`portfolio_plan_audit` |
| audit | 复用 Portfolio Plan audit，生成 `portfolio-plan-day-audit-summary.json` |
| follow-up | 构造只读 probe `system.duckdb`，复跑 downstream coverage diagnosis / closeout decision |
| evidence | 写出 repo 四件套、`H:\Asteria-report` 证据和 `H:\Asteria-Validated` zip |

## 4. Outputs

- `H:\Asteria-report\portfolio_plan\2026-05-10\portfolio-plan-2024-coverage-repair-card-20260509-01\portfolio-plan-day-audit-summary.json`
- `H:\Asteria-report\portfolio_plan\2026-05-10\portfolio-plan-2024-coverage-repair-card-20260509-01\manifest.json`
- `H:\Asteria-report\portfolio_plan\2026-05-10\portfolio-plan-2024-coverage-repair-card-20260509-01\closeout.md`
- `H:\Asteria-report\pipeline\2026-05-10\portfolio-plan-2024-coverage-repair-card-20260509-01-followup-diagnosis\coverage-matrix.json`
- `H:\Asteria-report\pipeline\2026-05-10\portfolio-plan-2024-coverage-repair-card-20260509-01-followup-diagnosis\coverage-attribution.md`
- `H:\Asteria-Validated\Asteria-portfolio-plan-2024-coverage-repair-card-20260509-01.zip`

## 5. Verified Findings

- `hard_fail_count = 0`
- released Portfolio Plan admission earliest day 已前移到 `2024-01-02`
- released Portfolio Plan target exposure earliest day 是 `2024-01-05`
- follow-up next card 已真实下移到 `trade-2024-coverage-repair-card-20260509-01`
- truthful attribution 已变为 `downstream_surface_gap:trade`

## 6. Semantic Finding

- released Portfolio Plan 在 `2024-01-02` 与 `2024-01-03` 的 focus-window 状态是
  `rejected / position_candidate_rejected`。
- released Portfolio Plan 在 `2024-01-04` 的 focus-window 状态是
  `expired / superseded_by_newer_position_candidate`。
- 因此 `portfolio_target_exposure` 不需要为 `2024-01-02..2024-01-04` 伪造 exposure rows；
  只要 `2024-01-05` 的 admitted focus-window row 已被 truthfully materialize，就不再构成
  Portfolio Plan 语义缺口。
- 在该语义下，Portfolio Plan focus-window released day surface 已经 truthfully 收口；新的首断点是
  Trade。
