from __future__ import annotations

import json
from pathlib import Path

import duckdb

from asteria.pipeline.v1_downstream_reference_audit import run_downstream_reference_audit
from asteria.pipeline.v1_downstream_reference_audit_contracts import (
    V1_DOWNSTREAM_REFERENCE_AUDIT_RUN_ID,
    V1_USAGE_VALUE_DECISION_CARD,
    DownstreamReferenceAuditRequest,
)


def test_downstream_reference_audit_generates_decision_input(tmp_path: Path) -> None:
    repo_root = _build_terminal_repo(tmp_path)
    formal_data_root = tmp_path / "Asteria-data"
    _seed_trade_schema(formal_data_root)
    usage_manifest_path = _write_usage_manifest(tmp_path)

    summary = run_downstream_reference_audit(
        DownstreamReferenceAuditRequest(
            repo_root=repo_root,
            formal_data_root=formal_data_root,
            report_root=tmp_path / "Asteria-report",
            validated_root=tmp_path / "Asteria-Validated",
            temp_root=tmp_path / "Asteria-temp",
            usage_readout_manifest_path=usage_manifest_path,
        )
    )

    assert summary.run_id == V1_DOWNSTREAM_REFERENCE_AUDIT_RUN_ID
    assert summary.status == "passed / downstream semantics benchmark input generated"
    assert summary.live_next_card == "none / terminal"
    assert summary.next_route_card == V1_USAGE_VALUE_DECISION_CARD
    assert summary.issue_count == 0
    assert summary.category_counts == {
        "covered": 4,
        "expression_risk": 2,
        "real_gap": 1,
        "not_applicable_reference": 1,
    }

    manifest = json.loads(Path(summary.manifest_path).read_text(encoding="utf-8"))
    assert manifest["route_type"] == "roadmap_only_read_only_post_terminal_supplement"
    assert manifest["formal_db_mutation"] == "no"
    assert manifest["usage_readout_semantics"]["order_intent_row_count"] == 1
    assert manifest["usage_readout_semantics"]["order_rejection_row_count"] == 1158
    assert manifest["formal_schema"]["trade.duckdb::order_rejection_ledger"]["has_symbol"] is False
    assert manifest["formal_schema"]["trade.duckdb::fill_ledger"]["row_count"] == 0
    assert {row["category"] for row in manifest["benchmark_rows"]} == {
        "covered",
        "expression_risk",
        "real_gap",
        "not_applicable_reference",
    }

    report_text = Path(summary.report_path).read_text(encoding="utf-8")
    assert "Asteria Downstream Reference Audit" in report_text
    assert "已覆盖" in report_text
    assert "表达风险" in report_text
    assert "真实缺口" in report_text
    assert "不适用外部参考" in report_text
    assert "order_intent_ledger = 1" in report_text
    assert "order_rejection_ledger = 1158" in report_text


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
        "| 4 | `v1-usage-value-decision-card` | prepared next route card |\n",
        encoding="utf-8",
    )
    (repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md").write_text(
        "v1-usage-readout-report-card-20260513-01 = passed\n",
        encoding="utf-8",
    )
    return repo_root


def _write_usage_manifest(tmp_path: Path) -> Path:
    path = tmp_path / "usage-readout-manifest.json"
    path.write_text(
        json.dumps(
            {
                "run_id": "v1-usage-readout-report-card-20260513-01",
                "status": "passed / usage readout report generated",
                "live_next_card": "none / terminal",
                "selected_symbol_count": 31,
                "date_window": {"start": "2024-01-02", "end": "2024-12-31"},
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


def _seed_trade_schema(root: Path) -> None:
    root.mkdir(parents=True)
    with duckdb.connect(str(root / "trade.duckdb")) as con:
        con.execute(
            """
            create table order_rejection_ledger(
                order_rejection_id varchar,
                trade_run_id varchar,
                order_intent_id varchar,
                rejection_dt date,
                rejection_reason varchar,
                rejection_stage varchar,
                source_portfolio_plan_release_version varchar,
                run_id varchar,
                schema_version varchar,
                trade_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table fill_ledger(
                fill_id varchar,
                order_intent_id varchar,
                execution_dt date,
                fill_seq integer,
                fill_price double,
                fill_quantity double
            )
            """
        )
