from __future__ import annotations

from asteria.system_readout.contracts import (
    SYSTEM_READOUT_SCHEMA_VERSION,
    SYSTEM_READOUT_VERSION,
    SystemReadoutBuildRequest,
)
from asteria.system_readout.coverage_repair_contracts import (
    FOCUS_DATES,
    SystemReadout2024CoverageRepairRequest,
    SystemReadout2024CoverageRepairSummary,
)
from asteria.system_readout.coverage_repair_flow import (
    apply_focus_window_repair,
    resolve_released_chain,
    run_repair_audit,
)
from asteria.system_readout.coverage_repair_followup import (
    run_followup_diagnosis,
    write_repair_evidence,
)
from asteria.system_readout.coverage_repair_shared import summary_status, utc_now


def run_system_readout_2024_coverage_repair(
    request: SystemReadout2024CoverageRepairRequest,
) -> SystemReadout2024CoverageRepairSummary:
    released_chain = resolve_released_chain(request.source_system_db)
    build_request = SystemReadoutBuildRequest(
        source_malf_service_db=request.data_root / "malf_service_day.duckdb",
        source_alpha_root=request.data_root,
        source_signal_db=request.data_root / "signal.duckdb",
        source_position_db=request.data_root / "position.duckdb",
        source_portfolio_plan_db=request.data_root / "portfolio_plan.duckdb",
        source_trade_db=request.data_root / "trade.duckdb",
        target_system_db=request.source_system_db,
        report_root=request.report_root,
        validated_root=request.validated_root,
        temp_root=request.temp_root,
        run_id=released_chain["released_system_run_id"],
        mode="bounded",
        source_chain_release_version=released_chain["source_chain_release_version"],
        schema_version=SYSTEM_READOUT_SCHEMA_VERSION,
        system_readout_version=SYSTEM_READOUT_VERSION,
        start_dt=request.focus_start_dt,
        end_dt=request.focus_end_dt,
        symbol_limit=None,
    )
    created_at = utc_now()
    counts = apply_focus_window_repair(
        target_system_db=request.source_system_db,
        released_system_run_id=released_chain["released_system_run_id"],
        build_request=build_request,
        created_at=created_at,
    )
    audit_report_path, audit_payload = run_repair_audit(
        build_request=build_request,
        repair_request=request,
        created_at=created_at,
    )
    followup_next_card, followup_attribution, followup_artifacts = run_followup_diagnosis(
        request=request,
    )
    manifest_path, closeout_path, validated_zip = write_repair_evidence(
        request=request,
        released_system_run_id=released_chain["released_system_run_id"],
        audit_report_path=audit_report_path,
        audit_payload=audit_payload,
        followup_next_card=followup_next_card,
        followup_attribution=followup_attribution,
        followup_artifacts=followup_artifacts,
    )
    status = summary_status(
        hard_fail_count=int(audit_payload["hard_fail_count"]),
        followup_next_card=followup_next_card,
        followup_attribution=followup_attribution,
    )
    return SystemReadout2024CoverageRepairSummary(
        run_id=request.run_id,
        status=status,
        released_system_run_id=released_chain["released_system_run_id"],
        repaired_focus_dates=tuple(FOCUS_DATES),
        source_manifest_count=counts["source_manifest_count"],
        module_status_count=counts["module_status_count"],
        readout_count=counts["readout_count"],
        summary_count=counts["summary_count"],
        audit_snapshot_count=counts["audit_snapshot_count"],
        hard_fail_count=int(audit_payload["hard_fail_count"]),
        followup_next_card=followup_next_card,
        followup_attribution=followup_attribution,
        audit_report_path=str(audit_report_path),
        manifest_path=str(manifest_path),
        closeout_path=str(closeout_path),
        validated_zip=str(validated_zip),
    )
