from __future__ import annotations

SIGNAL_PAS_SCHEMA_VERSION = "signal-pas-alignment-schema-v1"
SIGNAL_PAS_RULE_VERSION = "signal-pas-alignment-v1"

SIGNAL_PAS_ACTIVE_STATES = frozenset({"triggered", "reentry_candidate"})

SIGNAL_PAS_EXECUTION_HINT = "T_PLUS_1_OPEN"
SIGNAL_PAS_EXECUTION_TRADE_DATE_POLICY = "next_trading_day_after_signal_date"
SIGNAL_PAS_EXECUTION_PRICE_FIELD = "open"

SIGNAL_PAS_REQUIRED_INPUT_FIELDS = frozenset(
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
        "candidate_id",
    }
)

SIGNAL_PAS_REQUIRED_OUTPUT_FIELDS = frozenset(
    {
        "symbol",
        "timeframe",
        "signal_date",
        "signal_type",
        "signal_state",
        "signal_strength",
        "signal_family",
        "source_run_id",
        "source_pas_run_id",
        "schema_version",
        "signal_rule_version",
        "source_alpha_pas_rule_version",
        "lineage",
        "execution_hint",
        "execution_trade_date_policy",
        "execution_price_field",
    }
)

SIGNAL_PAS_FORBIDDEN_OUTPUT_FIELDS = frozenset(
    {
        "position_size",
        "portfolio_allocation",
        "target_weight",
        "broker_order",
        "order_intent_id",
        "fill_id",
        "account_state",
        "profit_claim",
    }
)
