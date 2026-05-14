from __future__ import annotations

ALPHA_PAS_SCHEMA_VERSION = "alpha-pas-proof-schema-v1"
ALPHA_PAS_RULE_VERSION = "alpha-pas-bounded-proof-v1"

PAS_REQUIRED_SERVICE_FIELDS = frozenset(
    {
        "symbol",
        "timeframe",
        "setup_date",
        "signal_date",
        "setup_family",
        "candidate_state",
        "context_reason_code",
        "trigger_reason_code",
        "failure_reason_code",
        "confidence",
        "strength_score",
        "strength_bucket",
        "source_run_id",
        "malf_wave_position_run_id",
        "rule_version",
        "schema_version",
        "source_concept_trace",
        "lineage",
        "execution_hint",
        "execution_trade_date_policy",
        "execution_price_field",
    }
)

PAS_FORBIDDEN_OUTPUT_FIELDS = frozenset(
    {
        "position_size",
        "portfolio_allocation",
        "portfolio_weight",
        "target_weight",
        "broker_order",
        "broker_order_id",
        "order_intent_id",
        "fill_ledger",
        "fill_id",
        "account_state",
        "account_balance",
        "profit_claim",
        "realized_pnl",
    }
)

PAS_LIFECYCLE_STATES = frozenset(
    {
        "waiting",
        "triggered",
        "cancelled",
        "modified",
        "reentry_candidate",
        "invalidated",
        "accepted_by_signal",
        "rejected_by_signal",
    }
)

PAS_SETUP_FAMILIES = ("TST", "BOF", "BPB", "PB", "CPB")

PAS_EXECUTION_HINT = "T_PLUS_1_OPEN"
PAS_EXECUTION_TRADE_DATE_POLICY = "next_trading_day_after_signal_date"
PAS_EXECUTION_PRICE_FIELD = "open"

PAS_SOURCE_CONCEPT_TRACE = (
    "Alpha_PAS_Design_Set_v1_0;"
    "docs/03-refactor/08-alpha-pas-authority-map-v1.md;"
    "MALF v1.4 WavePosition"
)
