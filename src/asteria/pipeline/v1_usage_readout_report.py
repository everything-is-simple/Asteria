from __future__ import annotations

import json
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import duckdb

from asteria.pipeline.v1_usage_readout_report_contracts import (
    USAGE_READOUT_TABLE_SPECS,
    V1_APPLICATION_DB_READINESS_AUDIT_CARD,
    V1_USAGE_READOUT_REPORT_CARD,
    V1_USAGE_SCOPE_RUN_ID,
    V1_USAGE_VALUE_DECISION_CARD,
    UsageReadoutReportRequest,
    UsageReadoutReportSummary,
    UsageReadoutTableSpec,
)
from asteria.pipeline.v1_usage_readout_report_render import (
    RETAINED_CAVEATS,
    closeout_markdown,
    manifest_payload,
    report_markdown,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


def run_v1_usage_readout_report(
    request: UsageReadoutReportRequest,
) -> UsageReadoutReportSummary:
    live_next_card = _load_terminal_live_next_card(request.repo_root)
    route_issues = _collect_route_issues(request.repo_root)
    scope_manifest, scope_issues = _load_scope_manifest(request.scope_manifest_path)
    symbols = _selected_symbols(scope_manifest)
    start_date, end_date, date_window_issue = _date_window(scope_manifest)
    issues = [*route_issues, *scope_issues]
    if date_window_issue is not None:
        issues.append(date_window_issue)

    readout = _build_readout(request.formal_data_root, symbols, start_date, end_date)
    issues.extend(_collect_readout_issues(readout))
    status = (
        "passed / usage readout report generated"
        if not issues
        else "blocked / usage readout report gaps found"
    )
    next_route_card = V1_USAGE_VALUE_DECISION_CARD if not issues else V1_USAGE_READOUT_REPORT_CARD

    manifest_path, report_path, closeout_path, temp_manifest_path, validated_zip = _write_artifacts(
        request=request,
        status=status,
        live_next_card=live_next_card,
        scope_manifest=scope_manifest,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        readout=readout,
        issues=issues,
        next_route_card=next_route_card,
    )

    return UsageReadoutReportSummary(
        run_id=request.run_id,
        status=status,
        live_next_card=live_next_card,
        live_next_card_preserved=live_next_card == "none / terminal",
        selected_symbol_count=len(symbols),
        date_window=f"{start_date.isoformat()}..{end_date.isoformat()}",
        issue_count=len(issues),
        issues=issues,
        caveats=RETAINED_CAVEATS,
        next_route_card=next_route_card,
        manifest_path=str(manifest_path),
        report_path=str(report_path),
        closeout_path=str(closeout_path),
        temp_manifest_path=str(temp_manifest_path),
        validated_zip=str(validated_zip),
    )


def _load_terminal_live_next_card(repo_root: Path) -> str:
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    if str(registry.get("latest_mainline_release_run_id", "")) != "final-release-closeout-card":
        raise ValueError("usage readout report requires final release closeout terminal state")
    if str(registry.get("current_allowed_next_card", "")) not in {"", "none"}:
        raise ValueError("usage readout report must not reopen live next card")
    return "none / terminal"


def _collect_route_issues(repo_root: Path) -> list[str]:
    issues: list[str] = []
    roadmap_path = (
        repo_root / "docs" / "03-refactor" / "05-asteria-v1-usage-validation-roadmap-v1.md"
    )
    conclusion_path = repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    roadmap_text = roadmap_path.read_text(encoding="utf-8")
    conclusion_text = conclusion_path.read_text(encoding="utf-8")
    route_line_options = {
        "| 3 | `v1-usage-readout-report-card` | prepared next route card |",
        "| 3 | `v1-usage-readout-report-card` | passed / usage readout report generated |",
    }
    if not any(route_line in roadmap_text for route_line in route_line_options):
        issues.append("roadmap does not prepare v1-usage-readout-report-card as route card 3")
    if V1_APPLICATION_DB_READINESS_AUDIT_CARD not in conclusion_text:
        issues.append("application DB readiness audit predecessor is not registered")
    return issues


def _load_scope_manifest(scope_manifest_path: Path) -> tuple[dict[str, Any], list[str]]:
    if not scope_manifest_path.exists():
        return {}, [f"scope manifest missing: {scope_manifest_path}"]
    manifest = json.loads(scope_manifest_path.read_text(encoding="utf-8"))
    issues: list[str] = []
    if manifest.get("run_id") != V1_USAGE_SCOPE_RUN_ID:
        issues.append("scope manifest run_id does not match frozen usage validation scope")
    if manifest.get("db_permission") != "read_only":
        issues.append("scope manifest db_permission must be read_only")
    if manifest.get("live_next_card") != "none / terminal":
        issues.append("scope manifest does not preserve terminal live next")
    if not manifest.get("selected_entries"):
        issues.append("scope manifest selected_entries is empty")
    return manifest, issues


def _selected_symbols(scope_manifest: dict[str, Any]) -> list[str]:
    entries = scope_manifest.get("selected_entries", [])
    symbols = [str(entry.get("symbol", "")).strip() for entry in entries if isinstance(entry, dict)]
    return [symbol for symbol in symbols if symbol]


def _date_window(scope_manifest: dict[str, Any]) -> tuple[date, date, str | None]:
    raw_window = scope_manifest.get("date_window", {})
    try:
        start_date = date.fromisoformat(str(raw_window["start"]))
        end_date = date.fromisoformat(str(raw_window["end"]))
    except (KeyError, TypeError, ValueError):
        return date(2024, 1, 2), date(2024, 12, 31), "scope manifest date_window is invalid"
    if start_date > end_date:
        return start_date, end_date, "scope manifest date_window start is after end"
    return start_date, end_date, None


def _build_readout(
    formal_data_root: Path,
    symbols: list[str],
    start_date: date,
    end_date: date,
) -> dict[str, dict[str, Any]]:
    sections: dict[str, dict[str, Any]] = defaultdict(dict)
    for spec in USAGE_READOUT_TABLE_SPECS:
        sections[spec.section][_readout_key(spec)] = _inspect_table(
            formal_data_root, spec, symbols, start_date, end_date
        )
    return dict(sections)


def _readout_key(spec: UsageReadoutTableSpec) -> str:
    return f"{spec.db_name}::{spec.table_name}"


def _inspect_table(
    formal_data_root: Path,
    spec: UsageReadoutTableSpec,
    symbols: list[str],
    start_date: date,
    end_date: date,
) -> dict[str, Any]:
    db_path = formal_data_root / spec.db_name
    if not db_path.exists():
        return _missing_table_payload(spec, f"database missing: {db_path}")
    try:
        with duckdb.connect(str(db_path), read_only=True) as con:
            columns = _columns(con, spec.table_name)
            if not columns:
                return _missing_table_payload(spec, f"table missing: {spec.table_name}")
            where_sql, params, symbol_filtered, date_filtered = _where_clause(
                columns, spec, symbols, start_date, end_date
            )
            row_count_row = con.execute(
                f"select count(*) from {_quote_ident(spec.table_name)}{where_sql}", params
            ).fetchone()
            if row_count_row is None:
                return _missing_table_payload(
                    spec, f"count query returned no rows: {spec.table_name}"
                )
            return {
                "db_name": spec.db_name,
                "table_name": spec.table_name,
                "row_count": int(row_count_row[0]),
                "symbol_filter_applied": symbol_filtered,
                "date_filter_applied": date_filtered,
                "scope_note": _scope_note(columns, symbols, symbol_filtered, date_filtered),
                "group_counts": _group_counts(con, spec, columns, where_sql, params),
                "reason_distribution": _distribution(
                    con,
                    spec.table_name,
                    columns,
                    where_sql,
                    params,
                    "rejection_reason",
                ),
                "stage_distribution": _distribution(
                    con,
                    spec.table_name,
                    columns,
                    where_sql,
                    params,
                    "rejection_stage",
                ),
                "lineage": _lineage(con, spec.table_name, columns, where_sql, params),
                "issue": None,
            }
    except duckdb.Error as exc:
        return _missing_table_payload(spec, str(exc))


def _missing_table_payload(spec: UsageReadoutTableSpec, issue: str) -> dict[str, Any]:
    return {
        "db_name": spec.db_name,
        "table_name": spec.table_name,
        "row_count": 0,
        "symbol_filter_applied": False,
        "date_filter_applied": False,
        "scope_note": None,
        "group_counts": [],
        "reason_distribution": [],
        "stage_distribution": [],
        "lineage": {},
        "issue": issue,
    }


def _columns(con: duckdb.DuckDBPyConnection, table_name: str) -> set[str]:
    try:
        return {
            str(row[1])
            for row in con.execute(f"pragma table_info({_quote_ident(table_name)})").fetchall()
        }
    except duckdb.Error:
        return set()


def _where_clause(
    columns: set[str],
    spec: UsageReadoutTableSpec,
    symbols: list[str],
    start_date: date,
    end_date: date,
) -> tuple[str, list[Any], bool, bool]:
    clauses: list[str] = []
    params: list[Any] = []
    symbol_filtered = bool(symbols) and "symbol" in columns
    if symbol_filtered:
        placeholders = ", ".join("?" for _ in symbols)
        clauses.append(f"symbol in ({placeholders})")
        params.extend(symbols)
    date_column = spec.date_column
    date_filtered = date_column is not None and date_column in columns
    if date_filtered:
        assert date_column is not None
        clauses.append(f"{_quote_ident(date_column)} between ? and ?")
        params.extend([start_date, end_date])
    if not clauses:
        return "", params, symbol_filtered, date_filtered
    return " where " + " and ".join(clauses), params, symbol_filtered, date_filtered


def _scope_note(
    columns: set[str],
    symbols: list[str],
    symbol_filtered: bool,
    date_filtered: bool,
) -> str | None:
    if symbols and not symbol_filtered and "symbol" not in columns:
        if date_filtered:
            return (
                "scope symbols were not applied because this table has no `symbol` field; "
                "row_count is a full-table readout inside the requested date window"
            )
        return (
            "scope symbols were not applied because this table has no `symbol` field; "
            "row_count is a full-table readout"
        )
    return None


def _group_counts(
    con: duckdb.DuckDBPyConnection,
    spec: UsageReadoutTableSpec,
    columns: set[str],
    where_sql: str,
    params: list[Any],
) -> list[dict[str, Any]]:
    group_columns = [column for column in spec.group_columns if column in columns][:3]
    if not group_columns:
        return []
    select_cols = ", ".join(_quote_ident(column) for column in group_columns)
    group_cols = ", ".join(_quote_ident(column) for column in group_columns)
    rows = con.execute(
        (
            f"select {select_cols}, count(*) as row_count "
            f"from {_quote_ident(spec.table_name)}{where_sql} "
            f"group by {group_cols} order by row_count desc limit 8"
        ),
        params,
    ).fetchall()
    return [
        {
            **{
                column: _json_value(value)
                for column, value in zip(group_columns, row[:-1], strict=True)
            },
            "row_count": int(row[-1]),
        }
        for row in rows
    ]


def _distribution(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    columns: set[str],
    where_sql: str,
    params: list[Any],
    column_name: str,
) -> list[dict[str, Any]]:
    if column_name not in columns:
        return []
    rows = con.execute(
        (
            f"select {_quote_ident(column_name)}, count(*) as row_count "
            f"from {_quote_ident(table_name)}{where_sql} "
            f"group by {_quote_ident(column_name)} "
            f"order by row_count desc, {_quote_ident(column_name)}"
        ),
        params,
    ).fetchall()
    return [{column_name: _json_value(row[0]), "row_count": int(row[1])} for row in rows]


def _lineage(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    columns: set[str],
    where_sql: str,
    params: list[Any],
) -> dict[str, list[Any]]:
    lineage_columns = [
        column
        for column in (
            "run_id",
            "schema_version",
            "source_core_run_id",
            "source_lifespan_run_id",
            "source_alpha_release_version",
            "source_chain_release_version",
        )
        if column in columns
    ]
    lineage: dict[str, list[Any]] = {}
    for column in lineage_columns:
        rows = con.execute(
            (
                f"select distinct {_quote_ident(column)} from {_quote_ident(table_name)}"
                f"{where_sql} limit 5"
            ),
            params,
        ).fetchall()
        lineage[column] = [_json_value(row[0]) for row in rows]
    return lineage


def _collect_readout_issues(readout: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    for section, tables in readout.items():
        for table_name, payload in tables.items():
            issue = payload.get("issue")
            if issue:
                issues.append(f"{section}.{table_name}: {issue}")
    return issues


def _write_artifacts(
    *,
    request: UsageReadoutReportRequest,
    status: str,
    live_next_card: str,
    scope_manifest: dict[str, Any],
    symbols: list[str],
    start_date: date,
    end_date: date,
    readout: dict[str, dict[str, Any]],
    issues: list[str],
    next_route_card: str,
) -> tuple[Path, Path, Path, Path, Path]:
    request.report_dir.mkdir(parents=True, exist_ok=True)
    request.temp_dir.mkdir(parents=True, exist_ok=True)
    manifest = manifest_payload(
        request,
        status,
        live_next_card,
        scope_manifest,
        symbols,
        start_date,
        end_date,
        readout,
        issues,
        next_route_card,
    )
    manifest_path = request.report_dir / "usage-readout-manifest.json"
    report_path = request.report_dir / "usage-readout-report.md"
    closeout_path = request.report_dir / "closeout.md"
    temp_manifest_path = request.temp_dir / "usage-readout-temp-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    temp_manifest_path.write_text(
        json.dumps(
            {
                "run_id": request.run_id,
                "status": status,
                "source_scope_manifest": str(request.scope_manifest_path),
                "report_manifest": str(manifest_path),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    report_path.write_text(report_markdown(manifest), encoding="utf-8")
    closeout_path.write_text(closeout_markdown(manifest), encoding="utf-8")
    validated_zip = request.validated_root / f"Asteria-{request.run_id}.zip"
    request.validated_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(validated_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in (manifest_path, report_path, closeout_path, temp_manifest_path):
            archive.write(path, arcname=path.name)
    return manifest_path, report_path, closeout_path, temp_manifest_path, validated_zip


def _quote_ident(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _json_value(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value
