from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import duckdb
from tests.unit.pipeline.support_repo_builders import build_governance_repo

from asteria.pipeline.v1_usage_validation_scope import run_v1_usage_validation_scope
from asteria.pipeline.v1_usage_validation_scope_contracts import (
    V1_APPLICATION_DB_READINESS_AUDIT_CARD,
    V1_USAGE_VALIDATION_SCOPE_INDUSTRY_SCHEMA,
    V1_USAGE_VALIDATION_SCOPE_SOURCE_REFERENCE,
    UsageValidationScopeRequest,
)


def _seed_market_meta(meta_db: Path) -> list[str]:
    industries = [f"行业{i:02d}" for i in range(1, 32)]
    meta_db.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(meta_db)) as con:
        con.execute(
            """
            create table trade_calendar (
                calendar_code varchar,
                trade_date date,
                is_open boolean,
                source_timeframe varchar,
                source_db_name varchar,
                run_id varchar,
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table instrument_master (
                instrument_id varchar,
                symbol varchar,
                exchange_code varchar,
                asset_type varchar,
                first_seen_date date,
                latest_seen_date date,
                list_status varchar,
                source_scope varchar,
                run_id varchar,
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table industry_classification (
                instrument_id varchar,
                industry_schema varchar,
                industry_code varchar,
                industry_name varchar,
                effective_date date,
                source_vendor varchar,
                run_id varchar,
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            insert into trade_calendar
            select
                'CN_A_SHARE',
                unnest(?::date[]),
                true,
                'day',
                'market_base_day.duckdb',
                'meta-run-001',
                'meta-v1',
                timestamp '2026-05-12 00:00:00'
            """,
            [[date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4), date(2024, 1, 5)]],
        )
        symbols: list[str] = []
        for idx, industry in enumerate(industries, start=1):
            base_symbol = f"{idx:06d}.SZ"
            symbols.append(base_symbol)
            con.execute(
                """
                insert into instrument_master values (?, ?, 'SZ', 'stock', ?, ?, 'observed',
                    'raw_market_and_market_base', 'meta-run-001', 'meta-v1',
                    timestamp '2026-05-12 00:00:00')
                """,
                [base_symbol, base_symbol, date(2024, 1, 2), date(2024, 12, 31)],
            )
            con.execute(
                """
                insert into industry_classification values (?, ?, ?, ?, ?, 'sw_source',
                    'meta-run-001', 'meta-v1', timestamp '2026-05-12 00:00:00')
                """,
                [
                    base_symbol,
                    V1_USAGE_VALIDATION_SCOPE_INDUSTRY_SCHEMA,
                    f"{idx:06d}",
                    f"{industry}|二级|三级",
                    date(2021, 7, 31),
                ],
            )
            if idx in {1, 2}:
                alt_symbol = f"{900000 + idx:06d}.SZ"
                symbols.append(alt_symbol)
                con.execute(
                    """
                    insert into instrument_master values (?, ?, 'SZ', 'stock', ?, ?, 'observed',
                        'raw_market_and_market_base', 'meta-run-001', 'meta-v1',
                        timestamp '2026-05-12 00:00:00')
                    """,
                    [alt_symbol, alt_symbol, date(2024, 1, 2), date(2024, 12, 31)],
                )
                con.execute(
                    """
                    insert into industry_classification values (?, ?, ?, ?, ?, 'sw_source',
                        'meta-run-001', 'meta-v1', timestamp '2026-05-12 00:00:00')
                    """,
                    [
                        alt_symbol,
                        V1_USAGE_VALIDATION_SCOPE_INDUSTRY_SCHEMA,
                        f"{idx:06d}",
                        f"{industry}|二级|三级",
                        date(2021, 7, 31),
                    ],
                )
        return symbols


def _seed_market_base(base_db: Path, symbols: list[str]) -> None:
    base_db.parent.mkdir(parents=True, exist_ok=True)
    full_dates = [date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4), date(2024, 1, 5)]
    with duckdb.connect(str(base_db)) as con:
        con.execute(
            """
            create table market_base_bar (
                symbol varchar,
                asset_type varchar,
                timeframe varchar,
                bar_dt date,
                trade_date date,
                price_line varchar,
                adj_mode varchar,
                open_px double,
                high_px double,
                low_px double,
                close_px double,
                volume double,
                amount double,
                source_vendor varchar,
                source_batch_id varchar,
                source_revision varchar,
                source_path varchar,
                run_id varchar,
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        for idx in range(1, 32):
            base_symbol = f"{idx:06d}.SZ"
            for current_dt in full_dates:
                con.execute(
                    """
                    insert into market_base_bar values (
                        ?, 'stock', 'day', ?, ?, 'execution_price_line', 'none',
                        1, 1, 1, 1, 100, ?, 'legacy_lifespan', 'batch-001', 'rev-001',
                        'source-path', 'base-run-001', 'base-v1', timestamp '2026-05-12 00:00:00'
                    )
                    """,
                    [base_symbol, current_dt, current_dt, float(10 + idx)],
                )
        for current_dt in full_dates[:3]:
            con.execute(
                """
                insert into market_base_bar values (
                    '900001.SZ', 'stock', 'day', ?, ?, 'execution_price_line', 'none',
                    1, 1, 1, 1, 100, 999.0, 'legacy_lifespan', 'batch-001', 'rev-001',
                    'source-path', 'base-run-001', 'base-v1', timestamp '2026-05-12 00:00:00'
                )
                """,
                [current_dt, current_dt],
            )
        for current_dt in full_dates:
            con.execute(
                """
                insert into market_base_bar values (
                    '900002.SZ', 'stock', 'day', ?, ?, 'execution_price_line', 'none',
                    1, 1, 1, 1, 100, 999.0, 'legacy_lifespan', 'batch-001', 'rev-001',
                    'source-path', 'base-run-001', 'base-v1', timestamp '2026-05-12 00:00:00'
                )
                """,
                [current_dt, current_dt],
            )


def test_scope_freeze_selects_one_symbol_per_level1_and_preserves_terminal_truth(
    tmp_path: Path,
) -> None:
    repo_root = build_governance_repo(tmp_path)
    meta_db = tmp_path / "data" / "market_meta.duckdb"
    base_db = tmp_path / "data" / "market_base_day.duckdb"
    symbols = _seed_market_meta(meta_db)
    _seed_market_base(base_db, symbols)

    summary = run_v1_usage_validation_scope(
        UsageValidationScopeRequest(
            repo_root=repo_root,
            market_meta_db=meta_db,
            market_base_day_db=base_db,
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="v1-usage-validation-scope-card-20260512-01",
            start_date=date(2024, 1, 2),
            end_date=date(2024, 12, 31),
            research_question=(
                "Asteria 当前链路能否给出可解释、可审计的结构-信号-持仓-交易意图读出"
            ),
            report_shape="双层输出",
        )
    )

    assert summary.status == "completed"
    assert summary.live_next_card == "none / terminal"
    assert summary.live_next_card_preserved is True
    assert summary.level1_industry_count == 31
    assert summary.selected_symbol_count == 31
    assert summary.next_route_card == V1_APPLICATION_DB_READINESS_AUDIT_CARD

    manifest = json.loads(Path(summary.manifest_path).read_text(encoding="utf-8"))
    assert manifest["db_permission"] == "read_only"
    assert manifest["industry_schema"] == V1_USAGE_VALIDATION_SCOPE_INDUSTRY_SCHEMA
    assert manifest["industry_schema_source"] == V1_USAGE_VALIDATION_SCOPE_SOURCE_REFERENCE
    assert manifest["level1_industry_count"] == 31
    assert len(manifest["selected_entries"]) == 31
    chosen = {entry["level1_industry"]: entry["symbol"] for entry in manifest["selected_entries"]}
    assert chosen["行业01"] == "000001.SZ"
    assert chosen["行业02"] == "900002.SZ"


def test_scope_freeze_applies_manual_override_reason(tmp_path: Path) -> None:
    repo_root = build_governance_repo(tmp_path)
    meta_db = tmp_path / "data" / "market_meta.duckdb"
    base_db = tmp_path / "data" / "market_base_day.duckdb"
    symbols = _seed_market_meta(meta_db)
    _seed_market_base(base_db, symbols)
    override_path = tmp_path / "override.json"
    override_path.write_text(
        json.dumps(
            {
                "行业02": {
                    "symbol": "000002.SZ",
                    "reason": "人工保留更熟悉的行业代表股，作为读报告的默认样例。",
                }
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    summary = run_v1_usage_validation_scope(
        UsageValidationScopeRequest(
            repo_root=repo_root,
            market_meta_db=meta_db,
            market_base_day_db=base_db,
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="v1-usage-validation-scope-card-20260512-01",
            start_date=date(2024, 1, 2),
            end_date=date(2024, 12, 31),
            research_question=(
                "Asteria 当前链路能否给出可解释、可审计的结构-信号-持仓-交易意图读出"
            ),
            report_shape="双层输出",
            manual_override_path=override_path,
        )
    )

    manifest = json.loads(Path(summary.manifest_path).read_text(encoding="utf-8"))
    chosen = {entry["level1_industry"]: entry["symbol"] for entry in manifest["selected_entries"]}
    assert chosen["行业02"] == "000002.SZ"
    assert manifest["manual_overrides"] == [
        {
            "level1_industry": "行业02",
            "symbol": "000002.SZ",
            "reason": "人工保留更熟悉的行业代表股，作为读报告的默认样例。",
        }
    ]
