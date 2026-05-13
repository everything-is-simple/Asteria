from __future__ import annotations

import json
from pathlib import Path

import duckdb
from tests.unit.pipeline.support_repo_builders import build_governance_repo

from asteria.pipeline.v1_application_db_readiness_audit import (
    run_v1_application_db_readiness_audit,
)
from asteria.pipeline.v1_application_db_readiness_audit_contracts import (
    EXPECTED_FORMAL_DB_COUNT,
    REQUIRED_DB_TABLES,
    V1_USAGE_READOUT_REPORT_CARD,
    ApplicationDbReadinessAuditRequest,
)


def _write_minimal_db(path: Path, required_tables: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        for table in required_tables:
            con.execute(f"create table {_quote(table)}(id integer, value varchar)")
            con.execute(f"insert into {_quote(table)} values (1, 'ok')")


def _seed_formal_data(root: Path) -> None:
    for db_name, required_tables in REQUIRED_DB_TABLES.items():
        _write_minimal_db(root / db_name, required_tables)


def test_readiness_audit_passes_when_all_formal_dbs_open_read_only(tmp_path: Path) -> None:
    repo_root = build_governance_repo(tmp_path)
    formal_data_root = tmp_path / "Asteria-data"
    _seed_formal_data(formal_data_root)

    summary = run_v1_application_db_readiness_audit(
        ApplicationDbReadinessAuditRequest(
            repo_root=repo_root,
            formal_data_root=formal_data_root,
            report_root=tmp_path / "Asteria-report",
            validated_root=tmp_path / "Asteria-Validated",
        )
    )

    assert summary.status == "passed / application DB readiness audited"
    assert summary.live_next_card == "none / terminal"
    assert summary.live_next_card_preserved is True
    assert summary.db_count == EXPECTED_FORMAL_DB_COUNT
    assert summary.read_only_open_count == EXPECTED_FORMAL_DB_COUNT
    assert summary.application_input_db_count == 20
    assert summary.application_input_ready_count == 20
    assert summary.downstream_pipeline_readable_count == 5
    assert summary.issue_count == 0
    assert summary.next_route_card == V1_USAGE_READOUT_REPORT_CARD
    assert Path(summary.closeout_path).exists()
    assert Path(summary.validated_zip).exists()

    manifest = json.loads(Path(summary.manifest_path).read_text(encoding="utf-8"))
    assert manifest["route_type"] == "roadmap_only_read_only_post_terminal"
    assert manifest["groups"]["data"]["ready_count"] == 5
    assert manifest["databases"]["market_meta.duckdb"]["ready"] is True


def test_readiness_audit_blocks_missing_required_table(tmp_path: Path) -> None:
    repo_root = build_governance_repo(tmp_path)
    formal_data_root = tmp_path / "Asteria-data"
    _seed_formal_data(formal_data_root)
    (formal_data_root / "signal.duckdb").unlink()
    _write_minimal_db(formal_data_root / "signal.duckdb", ("signal_run",))

    summary = run_v1_application_db_readiness_audit(
        ApplicationDbReadinessAuditRequest(
            repo_root=repo_root,
            formal_data_root=formal_data_root,
            report_root=tmp_path / "Asteria-report",
            validated_root=tmp_path / "Asteria-Validated",
        )
    )

    assert summary.status == "blocked / DB readiness gaps found"
    assert summary.next_route_card == "v1-application-db-readiness-audit-card"
    assert any("signal.duckdb" in issue for issue in summary.issues)


def _quote(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'
