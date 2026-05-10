from __future__ import annotations

from pathlib import Path

from asteria.position.contracts import (
    POSITION_RULE_VERSION,
    POSITION_SCHEMA_VERSION,
    PositionBuildRequest,
)
from asteria.position.coverage_repair_contracts import (
    FOCUS_DATES,
    Position2024CoverageRepairRequest,
    Position2024CoverageRepairSummary,
)
from asteria.position.coverage_repair_flow import (
    apply_focus_window_repair,
    load_focus_signals,
    resolve_released_chain,
    run_repair_audit,
    single_manifest_row,
)
from asteria.position.coverage_repair_followup import (
    run_followup_closeout,
    write_repair_evidence,
)
from asteria.position.coverage_repair_shared import summary_status, utc_now
from asteria.position.rules import build_position_rows


def run_position_2024_coverage_repair(
    request: Position2024CoverageRepairRequest,
) -> Position2024CoverageRepairSummary:
    released_chain = resolve_released_chain(request.source_system_db)
    position_row = single_manifest_row(released_chain["manifest_rows"], "position")
    signal_row = single_manifest_row(released_chain["manifest_rows"], "signal")
    target_position_db = Path(position_row["source_db"])
    released_position_run_id = position_row["source_run_id"]
    released_signal_run_id = signal_row["source_run_id"]
    released_signal_db = Path(signal_row["source_db"])

    focus_signals = load_focus_signals(released_signal_db, released_signal_run_id)
    build_request = PositionBuildRequest(
        source_signal_db=released_signal_db,
        target_position_db=target_position_db,
        report_root=request.report_root,
        validated_root=request.validated_root,
        temp_root=request.temp_root,
        run_id=released_position_run_id,
        mode="bounded",
        source_signal_release_version=signal_row["source_release_version"],
        source_signal_run_id=released_signal_run_id,
        schema_version=POSITION_SCHEMA_VERSION,
        position_rule_version=POSITION_RULE_VERSION,
        start_dt=request.focus_start_dt,
        end_dt=request.focus_end_dt,
    )
    created_at = utc_now()
    rows = build_position_rows(focus_signals, build_request, created_at)
    apply_focus_window_repair(
        target_position_db=target_position_db,
        build_request=build_request,
        rows=rows,
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
        released_position_run_id=released_position_run_id,
        released_signal_run_id=released_signal_run_id,
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
    return Position2024CoverageRepairSummary(
        run_id=request.run_id,
        status=status,
        released_system_run_id=released_chain["released_system_run_id"],
        released_position_run_id=released_position_run_id,
        released_signal_run_id=released_signal_run_id,
        repaired_focus_dates=tuple(FOCUS_DATES),
        input_signal_count=int(audit_payload["input_signal_count"]),
        position_candidate_count=int(audit_payload["position_candidate_count"]),
        entry_plan_count=int(audit_payload["entry_plan_count"]),
        exit_plan_count=int(audit_payload["exit_plan_count"]),
        hard_fail_count=int(audit_payload["hard_fail_count"]),
        followup_next_card=followup_next_card,
        followup_attribution=followup_attribution,
        audit_report_path=str(audit_report_path),
        manifest_path=str(manifest_path),
        closeout_path=str(closeout_path),
        validated_zip=str(validated_zip),
    )
