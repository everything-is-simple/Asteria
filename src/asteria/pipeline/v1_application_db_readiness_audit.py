from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

import duckdb

from asteria.pipeline.v1_application_db_readiness_audit_contracts import (
    APPLICATION_INPUT_GROUPS,
    EXPECTED_FORMAL_DB_COUNT,
    FORMAL_DB_GROUPS,
    REQUIRED_DB_TABLES,
    V1_APPLICATION_DB_READINESS_AUDIT_CARD,
    V1_USAGE_READOUT_REPORT_CARD,
    ApplicationDbReadinessAuditRequest,
    ApplicationDbReadinessAuditSummary,
    DbReadinessEntry,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


def run_v1_application_db_readiness_audit(
    request: ApplicationDbReadinessAuditRequest,
) -> ApplicationDbReadinessAuditSummary:
    live_next_card = _load_terminal_live_next_card(request.repo_root)
    _assert_route_prepared(request.repo_root)
    entries = [_inspect_db(request.formal_data_root, group, db) for group, db in _expected_dbs()]
    issues = _collect_issues(entries)
    summary = _build_summary(request, live_next_card, entries, issues)
    _write_artifacts(request, summary, entries)
    return summary


def _load_terminal_live_next_card(repo_root: Path) -> str:
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    if str(registry.get("latest_mainline_release_run_id", "")) != "final-release-closeout-card":
        raise ValueError("DB readiness audit requires final release closeout terminal state")
    if str(registry.get("current_allowed_next_card", "")) not in {"", "none"}:
        raise ValueError("DB readiness audit must not reopen live next card")
    return "none / terminal"


def _assert_route_prepared(repo_root: Path) -> None:
    roadmap_text = (
        repo_root / "docs" / "03-refactor" / "05-asteria-v1-usage-validation-roadmap-v1.md"
    ).read_text(encoding="utf-8")
    required_tokens = [
        "v1-usage-validation-scope-card",
        V1_APPLICATION_DB_READINESS_AUDIT_CARD,
        "当前 25 个 DuckDB 可被只读打开",
    ]
    for token in required_tokens:
        if token not in roadmap_text:
            raise ValueError(f"v1 usage validation roadmap is missing token: {token}")


def _expected_dbs() -> list[tuple[str, str]]:
    return [(group, db) for group, dbs in FORMAL_DB_GROUPS.items() for db in dbs]


def _inspect_db(root: Path, group: str, db_name: str) -> DbReadinessEntry:
    db_path = root / db_name
    required_tables = list(REQUIRED_DB_TABLES[db_name])
    if not db_path.exists():
        return DbReadinessEntry(
            db_name=db_name,
            group=group,
            path=str(db_path),
            exists=False,
            read_only_opened=False,
            table_count=0,
            row_counts={},
            required_tables=required_tables,
            missing_required_tables=required_tables,
            zero_required_tables=[],
            schema_versions={},
            rule_versions={},
            error="missing formal DuckDB",
        )
    try:
        with duckdb.connect(str(db_path), read_only=True) as con:
            tables = _table_names(con)
            row_counts = {table: _row_count(con, table) for table in tables}
            missing = [table for table in required_tables if table not in row_counts]
            zero_required = [
                table for table in required_tables if table in row_counts and row_counts[table] == 0
            ]
            return DbReadinessEntry(
                db_name=db_name,
                group=group,
                path=str(db_path),
                exists=True,
                read_only_opened=True,
                table_count=len(tables),
                row_counts=row_counts,
                required_tables=required_tables,
                missing_required_tables=missing,
                zero_required_tables=zero_required,
                schema_versions=_version_tables(con, tables, "schema_version"),
                rule_versions=_version_tables(con, tables, "rule_version"),
            )
    except Exception as exc:
        return DbReadinessEntry(
            db_name=db_name,
            group=group,
            path=str(db_path),
            exists=True,
            read_only_opened=False,
            table_count=0,
            row_counts={},
            required_tables=required_tables,
            missing_required_tables=required_tables,
            zero_required_tables=[],
            schema_versions={},
            rule_versions={},
            error=f"{type(exc).__name__}: {exc}",
        )


def _table_names(con: duckdb.DuckDBPyConnection) -> list[str]:
    return [
        str(row[0])
        for row in con.execute(
            "select table_name from information_schema.tables "
            "where table_schema = 'main' and table_type = 'BASE TABLE' "
            "order by table_name"
        ).fetchall()
    ]


def _row_count(con: duckdb.DuckDBPyConnection, table: str) -> int:
    row = con.execute(f"select count(*) from {_quote_identifier(table)}").fetchone()
    return int(row[0]) if row is not None else 0


def _version_tables(
    con: duckdb.DuckDBPyConnection,
    tables: list[str],
    token: str,
) -> dict[str, list[str]]:
    versions: dict[str, list[str]] = {}
    for table in tables:
        if token not in table:
            continue
        rows = con.execute(f"select * from {_quote_identifier(table)} limit 20").fetchall()
        versions[table] = [str(row[0]) for row in rows]
    return versions


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _collect_issues(entries: list[DbReadinessEntry]) -> list[str]:
    issues: list[str] = []
    if len(entries) != EXPECTED_FORMAL_DB_COUNT:
        issues.append(f"expected {EXPECTED_FORMAL_DB_COUNT} DBs but inspected {len(entries)}")
    for entry in entries:
        if not entry.exists:
            issues.append(f"{entry.db_name}: missing")
        elif not entry.read_only_opened:
            issues.append(f"{entry.db_name}: cannot be opened read-only ({entry.error})")
        if entry.missing_required_tables:
            issues.append(f"{entry.db_name}: missing tables {entry.missing_required_tables}")
        if entry.zero_required_tables:
            issues.append(f"{entry.db_name}: zero-row required tables {entry.zero_required_tables}")
    return issues


def _build_summary(
    request: ApplicationDbReadinessAuditRequest,
    live_next_card: str,
    entries: list[DbReadinessEntry],
    issues: list[str],
) -> ApplicationDbReadinessAuditSummary:
    input_entries = [entry for entry in entries if entry.group in APPLICATION_INPUT_GROUPS]
    downstream_entries = [entry for entry in entries if entry.group == "downstream_pipeline"]
    status = (
        "passed / application DB readiness audited"
        if not issues
        else "blocked / DB readiness gaps found"
    )
    return ApplicationDbReadinessAuditSummary(
        run_id=request.run_id,
        status=status,
        live_next_card=live_next_card,
        live_next_card_preserved=(live_next_card == "none / terminal"),
        db_count=len(entries),
        read_only_open_count=sum(1 for entry in entries if entry.read_only_opened),
        application_input_db_count=len(input_entries),
        application_input_ready_count=sum(1 for entry in input_entries if entry.ready),
        downstream_pipeline_readable_count=sum(1 for entry in downstream_entries if entry.ready),
        issue_count=len(issues),
        issues=issues,
        caveats=[
            (
                "fill_ledger remains a retained source caveat and is not treated as "
                "a usage blocker here."
            ),
            (
                "ST, long suspension, full listing lifecycle, and historical industry "
                "lineage remain source caveats."
            ),
            "This card is read-only and does not rebuild, patch, or promote H:/Asteria-data.",
            (
                "Passing this card only unlocks the next usage-validation report route, "
                "not production daily activation."
            ),
        ],
        next_route_card=V1_USAGE_READOUT_REPORT_CARD
        if not issues
        else V1_APPLICATION_DB_READINESS_AUDIT_CARD,
        manifest_path=str(request.report_dir / "db-readiness-manifest.json"),
        closeout_path=str(request.report_dir / "closeout.md"),
        validated_zip=str(request.validated_root / f"Asteria-{request.run_id}.zip"),
    )


def _write_artifacts(
    request: ApplicationDbReadinessAuditRequest,
    summary: ApplicationDbReadinessAuditSummary,
    entries: list[DbReadinessEntry],
) -> None:
    request.report_dir.mkdir(parents=True, exist_ok=True)
    request.validated_root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": request.run_id,
        "card_id": V1_APPLICATION_DB_READINESS_AUDIT_CARD,
        "status": summary.status,
        "route_type": "roadmap_only_read_only_post_terminal",
        "live_next_card": summary.live_next_card,
        "formal_data_root": str(request.formal_data_root),
        "summary": summary.as_dict(),
        "groups": _group_summary(entries),
        "databases": {entry.db_name: entry.as_dict() for entry in entries},
    }
    manifest_path = Path(summary.manifest_path)
    closeout_path = Path(summary.closeout_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    closeout_path.write_text(_closeout_text(summary), encoding="utf-8")
    with zipfile.ZipFile(summary.validated_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(manifest_path, arcname="db-readiness-manifest.json")
        archive.write(closeout_path, arcname="closeout.md")


def _group_summary(entries: list[DbReadinessEntry]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for group in FORMAL_DB_GROUPS:
        group_entries = [entry for entry in entries if entry.group == group]
        output[group] = {
            "db_count": len(group_entries),
            "ready_count": sum(1 for entry in group_entries if entry.ready),
            "read_only_open_count": sum(1 for entry in group_entries if entry.read_only_opened),
        }
    return output


def _closeout_text(summary: ApplicationDbReadinessAuditSummary) -> str:
    issues = "; ".join(summary.issues) if summary.issues else "none"
    caveats = "\n".join(f"- {item}" for item in summary.caveats)
    return (
        "\n".join(
            [
                f"# V1 Application DB Readiness Audit: {summary.run_id}",
                "",
                f"- status: `{summary.status}`",
                f"- live_next_card: `{summary.live_next_card}`",
                f"- formal_db_count: `{summary.db_count}`",
                f"- read_only_open_count: `{summary.read_only_open_count}`",
                (
                    "- application_input_ready: "
                    f"`{summary.application_input_ready_count}` / "
                    f"`{summary.application_input_db_count}`"
                ),
                (
                    "- downstream_pipeline_readable: "
                    f"`{summary.downstream_pipeline_readable_count}` / `5`"
                ),
                f"- issue_count: `{summary.issue_count}`",
                f"- issues: {issues}",
                f"- next_route_card: `{summary.next_route_card}`",
                "",
                "## Caveats",
                "",
                caveats,
            ]
        )
        + "\n"
    )
