from __future__ import annotations

from pathlib import Path

from asteria.portfolio_plan.contracts import (
    PORTFOLIO_PLAN_RULE_VERSION,
    PORTFOLIO_PLAN_SCHEMA_VERSION,
    PortfolioPlanBuildRequest,
)
from asteria.portfolio_plan.coverage_repair_contracts import (
    FOCUS_DATES,
    PortfolioPlan2024CoverageRepairRequest,
    PortfolioPlan2024CoverageRepairSummary,
)
from asteria.portfolio_plan.coverage_repair_flow import (
    apply_focus_window_repair,
    load_focus_position_inputs,
    resolve_released_chain,
    run_repair_audit,
    single_manifest_row,
)
from asteria.portfolio_plan.coverage_repair_followup import (
    run_followup_closeout,
    write_repair_evidence,
)
from asteria.portfolio_plan.coverage_repair_shared import summary_status, utc_now
from asteria.portfolio_plan.rules import build_portfolio_plan_rows


def run_portfolio_plan_2024_coverage_repair(
    request: PortfolioPlan2024CoverageRepairRequest,
) -> PortfolioPlan2024CoverageRepairSummary:
    released_chain = resolve_released_chain(request.source_system_db)
    position_row = single_manifest_row(released_chain["manifest_rows"], "position")
    portfolio_row = single_manifest_row(released_chain["manifest_rows"], "portfolio_plan")
    trade_row = single_manifest_row(released_chain["manifest_rows"], "trade")
    target_portfolio_plan_db = Path(portfolio_row["source_db"])
    released_portfolio_plan_run_id = portfolio_row["source_run_id"]
    released_position_run_id = position_row["source_run_id"]
    released_trade_run_id = trade_row["source_run_id"]
    released_position_db = Path(position_row["source_db"])

    positions = load_focus_position_inputs(released_position_db, released_position_run_id)
    build_request = PortfolioPlanBuildRequest(
        source_position_db=released_position_db,
        target_portfolio_plan_db=target_portfolio_plan_db,
        report_root=request.report_root,
        validated_root=request.validated_root,
        temp_root=request.temp_root,
        run_id=released_portfolio_plan_run_id,
        mode="bounded",
        source_position_release_version=position_row["source_release_version"],
        source_position_run_id=released_position_run_id,
        schema_version=PORTFOLIO_PLAN_SCHEMA_VERSION,
        portfolio_plan_rule_version=PORTFOLIO_PLAN_RULE_VERSION,
        start_dt=request.focus_start_dt,
        end_dt=request.focus_end_dt,
    )
    created_at = utc_now()
    portfolio_rows = build_portfolio_plan_rows(positions, build_request, created_at)
    apply_focus_window_repair(
        target_portfolio_plan_db=target_portfolio_plan_db,
        build_request=build_request,
        portfolio_rows=portfolio_rows,
        created_at=created_at,
    )
    audit_report_path, audit_payload = run_repair_audit(
        build_request=build_request,
        repair_request=request,
        created_at=created_at,
    )
    followup_next_card, followup_attribution, followup_artifacts = run_followup_closeout(
        request=request,
        released_chain=released_chain,
    )
    manifest_path, closeout_path, validated_zip = write_repair_evidence(
        request=request,
        released_system_run_id=released_chain["released_system_run_id"],
        released_portfolio_plan_run_id=released_portfolio_plan_run_id,
        released_position_run_id=released_position_run_id,
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
    return PortfolioPlan2024CoverageRepairSummary(
        run_id=request.run_id,
        status=status,
        released_system_run_id=released_chain["released_system_run_id"],
        released_portfolio_plan_run_id=released_portfolio_plan_run_id,
        released_position_run_id=released_position_run_id,
        released_trade_run_id=released_trade_run_id,
        repaired_focus_dates=tuple(FOCUS_DATES),
        input_position_count=int(audit_payload["input_position_count"]),
        admission_count=int(audit_payload["admission_count"]),
        target_exposure_count=int(audit_payload["target_exposure_count"]),
        trim_count=int(audit_payload["trim_count"]),
        hard_fail_count=int(audit_payload["hard_fail_count"]),
        followup_next_card=followup_next_card,
        followup_attribution=followup_attribution,
        audit_report_path=str(audit_report_path),
        manifest_path=str(manifest_path),
        closeout_path=str(closeout_path),
        validated_zip=str(validated_zip),
    )
