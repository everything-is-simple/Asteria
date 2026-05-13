from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import duckdb

from asteria.pipeline.v1_usage_readout_report import run_v1_usage_readout_report
from asteria.pipeline.v1_usage_readout_report_contracts import (
    V1_USAGE_READOUT_REPORT_CARD,
    V1_USAGE_VALUE_DECISION_CARD,
    UsageReadoutReportRequest,
)


def test_usage_readout_report_generates_human_report_and_manifest(tmp_path: Path) -> None:
    repo_root = _build_terminal_repo(tmp_path)
    formal_data_root = tmp_path / "Asteria-data"
    _seed_formal_data(formal_data_root)
    scope_manifest_path = _write_scope_manifest(tmp_path)

    summary = run_v1_usage_readout_report(
        UsageReadoutReportRequest(
            repo_root=repo_root,
            formal_data_root=formal_data_root,
            report_root=tmp_path / "Asteria-report",
            validated_root=tmp_path / "Asteria-Validated",
            temp_root=tmp_path / "Asteria-temp",
            scope_manifest_path=scope_manifest_path,
        )
    )

    assert summary.status == "passed / usage readout report generated"
    assert summary.live_next_card == "none / terminal"
    assert summary.live_next_card_preserved is True
    assert summary.selected_symbol_count == 2
    assert summary.date_window == "2024-01-02..2024-12-31"
    assert summary.next_route_card == V1_USAGE_VALUE_DECISION_CARD
    assert Path(summary.manifest_path).exists()
    assert Path(summary.report_path).exists()
    assert Path(summary.closeout_path).exists()
    assert Path(summary.validated_zip).exists()

    manifest = json.loads(Path(summary.manifest_path).read_text(encoding="utf-8"))
    assert manifest["route_type"] == "roadmap_only_read_only_post_terminal"
    assert manifest["card_id"] == V1_USAGE_READOUT_REPORT_CARD
    assert manifest["selected_symbol_count"] == 2
    assert (
        manifest["readout"]["market_structure"]["malf_service_day.duckdb::malf_wave_position"][
            "row_count"
        ]
        == 2
    )
    assert (
        manifest["readout"]["opportunity"]["alpha_bof.duckdb::alpha_signal_candidate"]["row_count"]
        == 1
    )
    assert (
        manifest["readout"]["opportunity"]["alpha_bpb.duckdb::alpha_signal_candidate"]["row_count"]
        == 1
    )
    assert (
        manifest["readout"]["opportunity"]["signal.duckdb::formal_signal_ledger"]["row_count"] == 2
    )
    assert (
        manifest["readout"]["trade_intent"]["trade.duckdb::order_intent_ledger"]["row_count"] == 1
    )
    rejection_payload = manifest["readout"]["trade_intent"]["trade.duckdb::order_rejection_ledger"]
    assert rejection_payload["scope_note"] is not None
    assert rejection_payload["symbol_filter_applied"] is False
    assert rejection_payload["date_filter_applied"] is True
    assert rejection_payload["reason_distribution"] == [
        {
            "rejection_reason": "superseded_by_newer_position_candidate",
            "row_count": 1,
        }
    ]
    assert "fill_ledger source-bound gap retained" in manifest["caveats"]

    report_text = Path(summary.report_path).read_text(encoding="utf-8")
    assert "Asteria v1 Usage Readout Report" in report_text
    assert "市场结构" in report_text
    assert "交易意图" in report_text
    assert "scope symbols were not applied because this table has no `symbol` field" in report_text
    assert "reason_distribution" in report_text
    assert "下一张路线卡：`v1-usage-value-decision-card`" in report_text


def test_usage_readout_report_blocks_when_scope_manifest_is_not_read_only(tmp_path: Path) -> None:
    repo_root = _build_terminal_repo(tmp_path)
    formal_data_root = tmp_path / "Asteria-data"
    _seed_formal_data(formal_data_root)
    scope_manifest_path = _write_scope_manifest(tmp_path, db_permission="write")

    summary = run_v1_usage_readout_report(
        UsageReadoutReportRequest(
            repo_root=repo_root,
            formal_data_root=formal_data_root,
            report_root=tmp_path / "Asteria-report",
            validated_root=tmp_path / "Asteria-Validated",
            temp_root=tmp_path / "Asteria-temp",
            scope_manifest_path=scope_manifest_path,
        )
    )

    assert summary.status == "blocked / usage readout report gaps found"
    assert summary.next_route_card == V1_USAGE_READOUT_REPORT_CARD
    assert any(
        "scope manifest db_permission must be read_only" in issue for issue in summary.issues
    )


def _write_scope_manifest(tmp_path: Path, *, db_permission: str = "read_only") -> Path:
    path = tmp_path / "scope-manifest.json"
    path.write_text(
        json.dumps(
            {
                "run_id": "v1-usage-validation-scope-card-20260512-01",
                "status": "completed",
                "route_type": "roadmap_only_read_only_post_terminal",
                "live_next_card": "none / terminal",
                "date_window": {"start": "2024-01-02", "end": "2024-12-31"},
                "db_permission": db_permission,
                "selected_entries": [
                    {"level1_industry": "银行", "symbol": "000001.SZ"},
                    {"level1_industry": "传媒", "symbol": "300418.SZ"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


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
        "| 3 | `v1-usage-readout-report-card` | prepared next route card |\n",
        encoding="utf-8",
    )
    (repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md").write_text(
        "v1-application-db-readiness-audit-card-20260513-01 = passed\n",
        encoding="utf-8",
    )
    return repo_root


def _seed_formal_data(root: Path) -> None:
    _seed_malf(root)
    _seed_alpha_signal(root)
    _seed_downstream(root)


def _seed_malf(root: Path) -> None:
    with _connect(root / "malf_service_day.duckdb") as con:
        con.execute(
            """
            create table malf_wave_position(
                symbol varchar,
                timeframe varchar,
                bar_dt date,
                system_state varchar,
                wave_core_state varchar,
                direction varchar,
                life_state varchar,
                position_quadrant varchar,
                run_id varchar,
                schema_version varchar,
                source_core_run_id varchar,
                source_lifespan_run_id varchar
            )
            """
        )
        con.execute(
            """
            insert into malf_wave_position values
            (
                '000001.SZ', 'day', ?, 'up_alive', 'alive', 'up', 'young', 'early_active',
                'malf-run', 'v1', 'core-run', 'lifespan-run'
            ),
            (
                '300418.SZ', 'day', ?, 'down_alive', 'alive', 'down', 'extended',
                'late_active', 'malf-run', 'v1', 'core-run', 'lifespan-run'
            )
            """,
            [date(2024, 1, 2), date(2024, 1, 3)],
        )
    with _connect(root / "malf_lifespan_day.duckdb") as con:
        con.execute(
            """
            create table malf_lifespan_snapshot(
                symbol varchar,
                timeframe varchar,
                bar_dt date,
                life_state varchar,
                position_quadrant varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            insert into malf_lifespan_snapshot values
            ('000001.SZ', 'day', ?, 'young', 'early_active', 'lifespan-run')
            """,
            [date(2024, 1, 2)],
        )


def _seed_alpha_signal(root: Path) -> None:
    for db_name, family in {
        "alpha_bof.duckdb": "BOF",
        "alpha_tst.duckdb": "TST",
        "alpha_pb.duckdb": "PB",
        "alpha_cpb.duckdb": "CPB",
        "alpha_bpb.duckdb": "BPB",
    }.items():
        with _connect(root / db_name) as con:
            con.execute(
                """
                create table alpha_signal_candidate(
                    alpha_family varchar,
                    symbol varchar,
                    timeframe varchar,
                    bar_dt date,
                    candidate_state varchar,
                    opportunity_bias varchar,
                    confidence_bucket varchar,
                    reason_code varchar,
                    run_id varchar
                )
                """
            )
            con.execute(
                """
                insert into alpha_signal_candidate values
                (?, '000001.SZ', 'day', ?, 'accepted', 'long', 'high', 'sample', 'alpha-run')
                """,
                [family, date(2024, 1, 2)],
            )
    with _connect(root / "signal.duckdb") as con:
        con.execute(
            """
            create table formal_signal_ledger(
                symbol varchar,
                timeframe varchar,
                signal_dt date,
                signal_state varchar,
                signal_bias varchar,
                confidence_bucket varchar,
                reason_code varchar,
                run_id varchar,
                source_alpha_release_version varchar
            )
            """
        )
        con.execute(
            """
            insert into formal_signal_ledger values
            (
                '000001.SZ', 'day', ?, 'accepted', 'long', 'high', 'sample',
                'signal-run', 'alpha-release'
            ),
            (
                '300418.SZ', 'day', ?, 'rejected', 'neutral', 'low',
                'no_active_alpha_candidate', 'signal-run', 'alpha-release'
            )
            """,
            [date(2024, 1, 2), date(2024, 1, 3)],
        )


def _seed_downstream(root: Path) -> None:
    with _connect(root / "position.duckdb") as con:
        con.execute(
            """
            create table position_candidate_ledger(
                symbol varchar,
                timeframe varchar,
                candidate_dt date,
                candidate_state varchar,
                position_bias varchar,
                reason_code varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            insert into position_candidate_ledger values
            ('000001.SZ', 'day', ?, 'accepted', 'long', 'sample', 'position-run')
            """,
            [date(2024, 1, 2)],
        )
    with _connect(root / "portfolio_plan.duckdb") as con:
        con.execute(
            """
            create table portfolio_admission_ledger(
                symbol varchar,
                timeframe varchar,
                plan_dt date,
                admission_state varchar,
                admission_reason varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            insert into portfolio_admission_ledger values
            ('000001.SZ', 'day', ?, 'admitted', 'sample', 'portfolio-run')
            """,
            [date(2024, 1, 2)],
        )
    with _connect(root / "trade.duckdb") as con:
        con.execute(
            """
            create table order_intent_ledger(
                symbol varchar,
                timeframe varchar,
                intent_dt date,
                order_side varchar,
                order_intent_state varchar,
                run_id varchar
            )
            """
        )
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
            insert into order_intent_ledger values
            ('000001.SZ', 'day', ?, 'buy', 'planned', 'trade-run')
            """,
            [date(2024, 1, 2)],
        )
        con.execute(
            """
            insert into order_rejection_ledger values
            (
                'rejection-1',
                'trade-run',
                'intent-1',
                ?,
                'superseded_by_newer_position_candidate',
                'intent',
                'portfolio-run',
                'trade-run',
                'trade-bounded-proof-v1',
                'trade-portfolio-plan-minimal-v1',
                current_timestamp
            )
            """,
            [date(2024, 1, 2)],
        )
    with _connect(root / "system.duckdb") as con:
        con.execute(
            """
            create table system_chain_readout(
                symbol varchar,
                timeframe varchar,
                readout_dt date,
                readout_status varchar,
                wave_core_state varchar,
                system_state varchar,
                source_chain_release_version varchar
            )
            """
        )
        con.execute(
            """
            insert into system_chain_readout values
            ('000001.SZ', 'day', ?, 'complete', 'alive', 'up_alive', 'chain-release')
            """,
            [date(2024, 1, 2)],
        )
    with _connect(root / "pipeline.duckdb") as con:
        con.execute(
            """
            create table build_manifest(
                artifact_name varchar,
                artifact_role varchar,
                artifact_path varchar,
                source_ref varchar,
                source_type varchar
            )
            """
        )
        con.execute(
            """
            insert into build_manifest values
            (
                'system.duckdb',
                'formal_db',
                'H:/Asteria-data/system.duckdb',
                'final-release-closeout-card',
                'release'
            )
            """
        )


def _connect(path: Path) -> duckdb.DuckDBPyConnection:
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path))
