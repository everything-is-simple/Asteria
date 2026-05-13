from __future__ import annotations

import json
from pathlib import Path

from asteria.pipeline.v1_usage_value_decision import run_v1_usage_value_decision
from asteria.pipeline.v1_usage_value_decision_contracts import (
    V1_DAILY_INCREMENTAL_PRODUCTION_SCOPE_CARD,
    V1_USAGE_VALUE_DECISION_RUN_ID,
    UsageValueDecisionRequest,
)


def test_usage_value_decision_generates_research_usable_with_caveats(
    tmp_path: Path,
) -> None:
    repo_root = _build_terminal_repo(tmp_path)
    usage_manifest_path = _write_usage_readout_manifest(tmp_path)
    reference_manifest_path = _write_downstream_reference_manifest(tmp_path)

    summary = run_v1_usage_value_decision(
        UsageValueDecisionRequest(
            repo_root=repo_root,
            report_root=tmp_path / "Asteria-report",
            validated_root=tmp_path / "Asteria-Validated",
            temp_root=tmp_path / "Asteria-temp",
            usage_readout_manifest_path=usage_manifest_path,
            downstream_reference_manifest_path=reference_manifest_path,
        )
    )

    assert summary.run_id == V1_USAGE_VALUE_DECISION_RUN_ID
    assert summary.status == "passed / usage value decision completed"
    assert summary.live_next_card == "none / terminal"
    assert summary.value_decision == "research_usable_with_caveats"
    assert summary.next_route_card == V1_DAILY_INCREMENTAL_PRODUCTION_SCOPE_CARD
    assert summary.issue_count == 0
    assert summary.category_counts == {
        "usage_blocker": 0,
        "strategy_quality_issue": 2,
        "source_caveat": 3,
        "future_enhancement": 4,
    }

    manifest = json.loads(Path(summary.manifest_path).read_text(encoding="utf-8"))
    assert manifest["formal_db_mutation"] == "no"
    assert manifest["value_decision"] == "research_usable_with_caveats"
    assert "有研究使用价值" in manifest["human_conclusion"]
    assert manifest["decision_categories"]["usage_blocker"] == []
    assert len(manifest["decision_categories"]["strategy_quality_issue"]) == 2
    assert len(manifest["decision_categories"]["source_caveat"]) == 3
    assert len(manifest["decision_categories"]["future_enhancement"]) == 4
    assert manifest["input_evidence"]["usage_readout"]["order_intent_row_count"] == 1
    assert manifest["input_evidence"]["usage_readout"]["order_rejection_row_count"] == 1158
    assert manifest["input_evidence"]["downstream_reference"]["fill_ledger_row_count"] == 0

    report_text = Path(summary.report_path).read_text(encoding="utf-8")
    assert "research_usable_with_caveats" in report_text
    assert "usage_blocker = 0" in report_text
    assert "order_intent_ledger = 1" in report_text
    assert "order_rejection_ledger = 1158" in report_text
    assert "fill_ledger row_count = 0" in report_text
    assert "不能宣称收益回测" in report_text


def test_usage_value_decision_blocks_when_usage_readout_manifest_missing(
    tmp_path: Path,
) -> None:
    repo_root = _build_terminal_repo(tmp_path)
    reference_manifest_path = _write_downstream_reference_manifest(tmp_path)

    summary = run_v1_usage_value_decision(
        UsageValueDecisionRequest(
            repo_root=repo_root,
            report_root=tmp_path / "Asteria-report",
            validated_root=tmp_path / "Asteria-Validated",
            temp_root=tmp_path / "Asteria-temp",
            usage_readout_manifest_path=tmp_path / "missing-usage-readout.json",
            downstream_reference_manifest_path=reference_manifest_path,
        )
    )

    assert summary.status == "blocked / usage value decision input gaps found"
    assert summary.value_decision == "insufficient_evidence"
    assert summary.issue_count == 1
    assert "usage readout manifest missing" in summary.issues[0]
    manifest = json.loads(Path(summary.manifest_path).read_text(encoding="utf-8"))
    assert manifest["decision_categories"]["usage_blocker"]


def test_usage_value_decision_blocks_when_supplemental_audit_has_issues(
    tmp_path: Path,
) -> None:
    repo_root = _build_terminal_repo(tmp_path)
    usage_manifest_path = _write_usage_readout_manifest(tmp_path)
    reference_manifest_path = _write_downstream_reference_manifest(
        tmp_path,
        status="blocked / downstream semantics benchmark input gaps found",
        issues=["trade schema table missing: fill_ledger"],
    )

    summary = run_v1_usage_value_decision(
        UsageValueDecisionRequest(
            repo_root=repo_root,
            report_root=tmp_path / "Asteria-report",
            validated_root=tmp_path / "Asteria-Validated",
            temp_root=tmp_path / "Asteria-temp",
            usage_readout_manifest_path=usage_manifest_path,
            downstream_reference_manifest_path=reference_manifest_path,
        )
    )

    assert summary.status == "blocked / usage value decision input gaps found"
    assert summary.value_decision == "insufficient_evidence"
    assert summary.issue_count == 2
    assert any(
        "downstream reference audit manifest is not passed" in issue for issue in summary.issues
    )
    assert any("trade schema table missing: fill_ledger" in issue for issue in summary.issues)


def _build_terminal_repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    (repo_root / "governance").mkdir(parents=True)
    (repo_root / "docs" / "03-refactor").mkdir(parents=True)
    (repo_root / "docs" / "04-execution").mkdir(parents=True)
    (repo_root / "governance" / "module_gate_registry.toml").write_text(
        "\n".join(
            [
                'current_allowed_next_card = ""',
                'latest_mainline_release_run_id = "final-release-closeout-card"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (
        repo_root / "docs" / "03-refactor" / "05-asteria-v1-usage-validation-roadmap-v1.md"
    ).write_text(
        "\n".join(
            [
                "| 4 | `v1-usage-value-decision-card` | prepared next route card |",
                "| 5 | `daily-incremental-production-scope-card` | gated |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md").write_text(
        "\n".join(
            [
                "v1-usage-readout-report-card-20260513-01 = passed",
                "v1-downstream-reference-audit-20260513-01 = passed",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return repo_root


def _write_usage_readout_manifest(tmp_path: Path) -> Path:
    path = tmp_path / "usage-readout-manifest.json"
    path.write_text(
        json.dumps(
            {
                "run_id": "v1-usage-readout-report-card-20260513-01",
                "status": "passed / usage readout report generated",
                "live_next_card": "none / terminal",
                "selected_symbol_count": 31,
                "date_window": {"start": "2024-01-02", "end": "2024-12-31"},
                "issue_count": 0,
                "issues": [],
                "caveats": [
                    "fill_ledger source-bound gap retained",
                    "ST / suspension / listing-delisting lifecycle source caveats retained",
                    "calendar semantic gap remains a usage-readout caveat, not a release blocker",
                ],
                "readout": {
                    "trade_intent": {
                        "trade.duckdb::order_intent_ledger": {
                            "row_count": 1,
                            "symbol_filter_applied": True,
                        },
                        "trade.duckdb::order_rejection_ledger": {
                            "row_count": 1158,
                            "symbol_filter_applied": False,
                            "scope_note": (
                                "scope symbols were not applied because this table has "
                                "no `symbol` field"
                            ),
                            "reason_distribution": [
                                {
                                    "rejection_reason": ("superseded_by_newer_position_candidate"),
                                    "row_count": 1000,
                                },
                                {
                                    "rejection_reason": "position_candidate_rejected",
                                    "row_count": 156,
                                },
                                {
                                    "rejection_reason": "max_active_symbols_constraint",
                                    "row_count": 2,
                                },
                            ],
                        },
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def _write_downstream_reference_manifest(
    tmp_path: Path,
    *,
    status: str = "passed / downstream semantics benchmark input generated",
    issues: list[str] | None = None,
) -> Path:
    path = tmp_path / "downstream-reference-audit-manifest.json"
    issues = issues or []
    path.write_text(
        json.dumps(
            {
                "run_id": "v1-downstream-reference-audit-20260513-01",
                "status": status,
                "live_next_card": "none / terminal",
                "issue_count": len(issues),
                "issues": issues,
                "usage_readout_semantics": {
                    "order_intent_row_count": 1,
                    "order_rejection_row_count": 1158,
                    "order_rejection_symbol_filter_applied": False,
                },
                "formal_schema": {
                    "trade.duckdb::fill_ledger": {
                        "row_count": 0,
                        "has_symbol": False,
                    }
                },
                "category_counts": {
                    "covered": 4,
                    "expression_risk": 2,
                    "real_gap": 1,
                    "not_applicable_reference": 1,
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path
