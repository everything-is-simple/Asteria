from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import duckdb

from asteria.pipeline.v1_t_plus_one_open_backtesting_py_proof import (
    run_v1_t_plus_one_open_backtesting_py_proof,
)
from asteria.pipeline.v1_t_plus_one_open_backtesting_py_proof_contracts import (
    V1_T_PLUS_ONE_OPEN_BACKTESTING_PY_PROOF_CARD,
    V1_VECTORBT_PORTFOLIO_ANALYTICS_PROOF_CARD,
    TPlusOneOpenBacktestingPyProofRequest,
)


def test_t_plus_one_open_backtesting_py_proof_generates_manifest(tmp_path: Path) -> None:
    repo_root = _build_terminal_repo(tmp_path)
    formal_data_root = tmp_path / "Asteria-data"
    _seed_formal_data(formal_data_root)
    scope_manifest_path = _write_scope_manifest(tmp_path)

    summary = run_v1_t_plus_one_open_backtesting_py_proof(
        TPlusOneOpenBacktestingPyProofRequest(
            repo_root=repo_root,
            formal_data_root=formal_data_root,
            report_root=tmp_path / "Asteria-report",
            validated_root=tmp_path / "Asteria-Validated",
            temp_root=tmp_path / "Asteria-temp",
            scope_manifest_path=scope_manifest_path,
            initial_cash=10_000.0,
            commission=0.0,
        )
    )

    assert summary.status == "passed / t+1 open backtesting.py proof completed"
    assert summary.live_next_card == "none / terminal"
    assert summary.selected_symbol_count == 2
    assert summary.signal_symbol_count == 1
    assert summary.completed_backtest_count == 1
    assert summary.skipped_symbol_count == 1
    assert summary.total_trade_count >= 1
    assert summary.next_route_card == V1_VECTORBT_PORTFOLIO_ANALYTICS_PROOF_CARD
    assert Path(summary.manifest_path).exists()
    assert Path(summary.report_path).exists()
    assert Path(summary.closeout_path).exists()
    assert Path(summary.validated_zip).exists()

    manifest = json.loads(Path(summary.manifest_path).read_text(encoding="utf-8"))
    assert manifest["card_id"] == V1_T_PLUS_ONE_OPEN_BACKTESTING_PY_PROOF_CARD
    assert manifest["formal_db_mutation"] == "no"
    assert manifest["execution_semantics"]["execution_hint"] == "T_PLUS_1_OPEN"
    assert (
        manifest["execution_semantics"]["trade_date_policy"] == "next_trading_day_after_signal_date"
    )
    assert manifest["execution_semantics"]["price_field"] == "open"
    assert manifest["aggregate"]["completed_backtest_count"] == 1
    assert manifest["aggregate"]["skipped_symbol_count"] == 1
    assert any(
        result["skip_reason"] == "no_active_signal_in_scope"
        for result in manifest["symbol_results"]
    )
    report_text = Path(summary.report_path).read_text(encoding="utf-8")
    assert "T+0 signal -> T+1 open execution" in report_text
    assert "not live trading capability" in report_text


def test_t_plus_one_open_backtesting_py_proof_blocks_without_signal_export_contract(
    tmp_path: Path,
) -> None:
    repo_root = _build_terminal_repo(tmp_path, include_signal_export=False)
    formal_data_root = tmp_path / "Asteria-data"
    _seed_formal_data(formal_data_root)
    scope_manifest_path = _write_scope_manifest(tmp_path)

    summary = run_v1_t_plus_one_open_backtesting_py_proof(
        TPlusOneOpenBacktestingPyProofRequest(
            repo_root=repo_root,
            formal_data_root=formal_data_root,
            report_root=tmp_path / "Asteria-report",
            validated_root=tmp_path / "Asteria-Validated",
            temp_root=tmp_path / "Asteria-temp",
            scope_manifest_path=scope_manifest_path,
        )
    )

    assert summary.status == "blocked / t+1 open backtesting.py proof gaps found"
    assert summary.next_route_card == V1_T_PLUS_ONE_OPEN_BACKTESTING_PY_PROOF_CARD
    assert any("signal export contract predecessor" in issue for issue in summary.issues)


def _write_scope_manifest(tmp_path: Path) -> Path:
    path = tmp_path / "scope-manifest.json"
    path.write_text(
        json.dumps(
            {
                "run_id": "v1-usage-validation-scope-card-20260512-01",
                "status": "completed",
                "route_type": "roadmap_only_read_only_post_terminal",
                "live_next_card": "none / terminal",
                "date_window": {"start": "2024-01-02", "end": "2024-01-05"},
                "db_permission": "read_only",
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


def _build_terminal_repo(tmp_path: Path, *, include_signal_export: bool = True) -> Path:
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
        ("| 3 | `v1-t-plus-one-open-backtesting-py-proof-card` | prepared next route card |\n"),
        encoding="utf-8",
    )
    conclusion_text = (
        "v1-signal-export-contract-card-20260513-01 = passed\n" if include_signal_export else ""
    )
    (repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md").write_text(
        conclusion_text,
        encoding="utf-8",
    )
    return repo_root


def _seed_formal_data(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(root / "signal.duckdb")) as con:
        con.execute(
            """
            create table formal_signal_ledger(
                signal_id varchar,
                symbol varchar,
                timeframe varchar,
                signal_dt date,
                signal_type varchar,
                signal_state varchar,
                signal_bias varchar,
                signal_strength double,
                confidence_bucket varchar,
                reason_code varchar,
                support_count bigint,
                conflict_count bigint,
                rejected_component_count bigint,
                source_alpha_release_version varchar,
                run_id varchar,
                schema_version varchar,
                signal_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            insert into formal_signal_ledger values
            (
                'sig-1', '000001.SZ', 'day', ?, 'directional_opportunity',
                'active', 'up_opportunity', 0.8, 'high', 'sample', 1, 0, 0,
                'alpha-release', 'signal-run', 'signal-schema', 'signal-rule', now()
            ),
            (
                'sig-2', '000001.SZ', 'day', ?, 'directional_opportunity',
                'active', 'down_opportunity', 0.6, 'medium', 'sample', 1, 0, 0,
                'alpha-release', 'signal-run', 'signal-schema', 'signal-rule', now()
            )
            """,
            [date(2024, 1, 2), date(2024, 1, 4)],
        )
    with duckdb.connect(str(root / "market_base_day.duckdb")) as con:
        con.execute(
            """
            create table market_base_bar(
                symbol varchar,
                timeframe varchar,
                trade_date date,
                price_line varchar,
                adj_mode varchar,
                open_px double,
                high_px double,
                low_px double,
                close_px double,
                volume double
            )
            """
        )
        con.executemany(
            """
            insert into market_base_bar values
            ('000001.SZ', 'day', ?, 'execution_price_line', 'none', ?, ?, ?, ?, ?)
            """,
            [
                (date(2024, 1, 1), 9.5, 9.8, 9.3, 9.6, 1000.0),
                (date(2024, 1, 2), 10.0, 10.5, 9.8, 10.2, 1000.0),
                (date(2024, 1, 3), 11.0, 11.5, 10.8, 11.2, 1000.0),
                (date(2024, 1, 4), 12.0, 12.5, 11.8, 12.2, 1000.0),
                (date(2024, 1, 5), 13.0, 13.5, 12.8, 13.2, 1000.0),
            ],
        )
