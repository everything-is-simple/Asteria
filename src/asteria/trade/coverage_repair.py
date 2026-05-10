from __future__ import annotations

from pathlib import Path

from asteria.trade.contracts import (
    TRADE_RULE_VERSION,
    TRADE_SCHEMA_VERSION,
    TradeBuildRequest,
)
from asteria.trade.coverage_repair_contracts import (
    FOCUS_DATES,
    Trade2024CoverageRepairRequest,
    Trade2024CoverageRepairSummary,
)
from asteria.trade.coverage_repair_flow import (
    apply_focus_window_repair,
    load_focus_portfolio_plan_inputs,
    resolve_released_chain,
    run_repair_audit,
    single_manifest_row,
)
from asteria.trade.coverage_repair_followup import (
    run_followup_diagnosis,
    write_repair_evidence,
)
from asteria.trade.coverage_repair_shared import summary_status, utc_now
from asteria.trade.rules import build_trade_rows


def run_trade_2024_coverage_repair(
    request: Trade2024CoverageRepairRequest,
) -> Trade2024CoverageRepairSummary:
    released_chain = resolve_released_chain(request.source_system_db)
    portfolio_row = single_manifest_row(released_chain["manifest_rows"], "portfolio_plan")
    trade_row = single_manifest_row(released_chain["manifest_rows"], "trade")
    target_trade_db = Path(trade_row["source_db"])
    released_portfolio_plan_run_id = portfolio_row["source_run_id"]
    released_trade_run_id = trade_row["source_run_id"]
    released_portfolio_plan_db = Path(portfolio_row["source_db"])

    inputs = load_focus_portfolio_plan_inputs(
        released_portfolio_plan_db,
        released_portfolio_plan_run_id,
    )
    build_request = TradeBuildRequest(
        source_portfolio_plan_db=released_portfolio_plan_db,
        target_trade_db=target_trade_db,
        report_root=request.report_root,
        validated_root=request.validated_root,
        temp_root=request.temp_root,
        run_id=released_trade_run_id,
        mode="bounded",
        source_portfolio_plan_release_version=portfolio_row["source_release_version"],
        source_portfolio_plan_run_id=released_portfolio_plan_run_id,
        schema_version=TRADE_SCHEMA_VERSION,
        trade_rule_version=TRADE_RULE_VERSION,
        start_dt=request.focus_start_dt,
        end_dt=request.focus_end_dt,
    )
    created_at = utc_now()
    trade_rows = build_trade_rows(inputs, build_request, created_at)
    apply_focus_window_repair(
        target_trade_db=target_trade_db,
        build_request=build_request,
        trade_rows=trade_rows,
        created_at=created_at,
    )
    audit_report_path, audit_payload = run_repair_audit(
        build_request=build_request,
        repair_request=request,
        created_at=created_at,
    )
    followup_next_card, followup_attribution, followup_artifacts = run_followup_diagnosis(
        request=request,
        released_chain=released_chain,
    )
    manifest_path, closeout_path, validated_zip = write_repair_evidence(
        request=request,
        released_system_run_id=released_chain["released_system_run_id"],
        released_portfolio_plan_run_id=released_portfolio_plan_run_id,
        released_trade_run_id=released_trade_run_id,
        followup_next_card=followup_next_card,
        followup_attribution=followup_attribution,
        audit_report_path=audit_report_path,
        audit_payload=audit_payload,
        followup_artifacts=followup_artifacts,
    )
    status = summary_status(
        hard_fail_count=int(audit_payload["hard_fail_count"]),
        followup_next_card=followup_next_card,
        followup_attribution=followup_attribution,
    )
    return Trade2024CoverageRepairSummary(
        run_id=request.run_id,
        status=status,
        released_system_run_id=released_chain["released_system_run_id"],
        released_portfolio_plan_run_id=released_portfolio_plan_run_id,
        released_trade_run_id=released_trade_run_id,
        repaired_focus_dates=tuple(FOCUS_DATES),
        input_portfolio_plan_count=int(audit_payload["input_portfolio_plan_count"]),
        order_intent_count=int(audit_payload["order_intent_count"]),
        execution_plan_count=int(audit_payload["execution_plan_count"]),
        fill_count=int(audit_payload["fill_count"]),
        rejection_count=int(audit_payload["rejection_count"]),
        hard_fail_count=int(audit_payload["hard_fail_count"]),
        followup_next_card=followup_next_card,
        followup_attribution=followup_attribution,
        audit_report_path=str(audit_report_path),
        manifest_path=str(manifest_path),
        closeout_path=str(closeout_path),
        validated_zip=str(validated_zip),
    )
