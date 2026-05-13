from __future__ import annotations

import json
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

import duckdb

from asteria.pipeline.v1_downstream_reference_audit_contracts import (
    BENCHMARK_ROWS,
    V1_USAGE_READOUT_REPORT_RUN_ID,
    V1_USAGE_VALUE_DECISION_CARD,
    DownstreamReferenceAuditRequest,
    DownstreamReferenceAuditSummary,
)
from asteria.pipeline.v1_downstream_reference_audit_render import (
    closeout_markdown,
    report_markdown,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


def run_downstream_reference_audit(
    request: DownstreamReferenceAuditRequest,
) -> DownstreamReferenceAuditSummary:
    live_next_card = _load_terminal_live_next_card(request.repo_root)
    route_issues = _collect_route_issues(request.repo_root)
    usage_manifest, usage_issues = _load_usage_manifest(request.usage_readout_manifest_path)
    usage_semantics = _usage_readout_semantics(usage_manifest)
    schema_payload, schema_issues = _formal_trade_schema(request.formal_data_root)
    issues = [*route_issues, *usage_issues, *schema_issues]
    category_counts = dict(Counter(row.category for row in BENCHMARK_ROWS))
    status = (
        "passed / downstream semantics benchmark input generated"
        if not issues
        else "blocked / downstream semantics benchmark input gaps found"
    )

    manifest_path, report_path, closeout_path, temp_manifest_path, validated_zip = _write_artifacts(
        request=request,
        status=status,
        live_next_card=live_next_card,
        usage_semantics=usage_semantics,
        schema_payload=schema_payload,
        category_counts=category_counts,
        issues=issues,
    )
    return DownstreamReferenceAuditSummary(
        run_id=request.run_id,
        status=status,
        live_next_card=live_next_card,
        live_next_card_preserved=live_next_card == "none / terminal",
        issue_count=len(issues),
        issues=issues,
        category_counts=category_counts,
        next_route_card=V1_USAGE_VALUE_DECISION_CARD,
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
        raise ValueError("downstream reference audit requires terminal final release closeout")
    if str(registry.get("current_allowed_next_card", "")) not in {"", "none"}:
        raise ValueError("downstream reference audit must not reopen live next card")
    return "none / terminal"


def _collect_route_issues(repo_root: Path) -> list[str]:
    roadmap_path = (
        repo_root / "docs" / "03-refactor" / "05-asteria-v1-usage-validation-roadmap-v1.md"
    )
    conclusion_path = repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    roadmap_text = roadmap_path.read_text(encoding="utf-8")
    conclusion_text = conclusion_path.read_text(encoding="utf-8")
    issues: list[str] = []
    if "| 4 | `v1-usage-value-decision-card` | prepared next route card |" not in roadmap_text:
        issues.append("roadmap does not preserve v1-usage-value-decision-card as route card 4")
    if V1_USAGE_READOUT_REPORT_RUN_ID not in conclusion_text:
        issues.append("usage readout report predecessor is not registered")
    return issues


def _load_usage_manifest(path: Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {}, [f"usage readout manifest missing: {path}"]
    manifest = json.loads(path.read_text(encoding="utf-8"))
    issues: list[str] = []
    if manifest.get("run_id") != V1_USAGE_READOUT_REPORT_RUN_ID:
        issues.append("usage readout manifest run_id does not match card 3")
    if manifest.get("live_next_card") != "none / terminal":
        issues.append("usage readout manifest does not preserve terminal live next")
    if not str(manifest.get("status", "")).startswith("passed"):
        issues.append("usage readout manifest is not passed")
    return manifest, issues


def _usage_readout_semantics(manifest: dict[str, Any]) -> dict[str, Any]:
    trade_readout = manifest.get("readout", {}).get("trade_intent", {})
    intent = trade_readout.get("trade.duckdb::order_intent_ledger", {})
    rejection = trade_readout.get("trade.duckdb::order_rejection_ledger", {})
    return {
        "source_manifest": manifest.get("run_id"),
        "order_intent_row_count": int(intent.get("row_count", 0)),
        "order_intent_symbol_filter_applied": bool(intent.get("symbol_filter_applied")),
        "order_rejection_row_count": int(rejection.get("row_count", 0)),
        "order_rejection_symbol_filter_applied": bool(rejection.get("symbol_filter_applied")),
        "order_rejection_scope_note": rejection.get("scope_note"),
        "rejection_reason_distribution": rejection.get("reason_distribution", []),
    }


def _formal_trade_schema(formal_data_root: Path) -> tuple[dict[str, Any], list[str]]:
    db_path = formal_data_root / "trade.duckdb"
    if not db_path.exists():
        return {}, [f"trade database missing: {db_path}"]
    payload: dict[str, Any] = {}
    issues: list[str] = []
    with duckdb.connect(str(db_path), read_only=True) as con:
        for table_name in ("order_rejection_ledger", "fill_ledger"):
            table_key = f"trade.duckdb::{table_name}"
            columns = _columns(con, table_name)
            if not columns:
                issues.append(f"trade schema table missing: {table_name}")
                payload[table_key] = {"columns": [], "has_symbol": False, "row_count": 0}
                continue
            payload[table_key] = {
                "columns": sorted(columns),
                "has_symbol": "symbol" in columns,
                "row_count": _row_count(con, table_name),
            }
    return payload, issues


def _columns(con: duckdb.DuckDBPyConnection, table_name: str) -> set[str]:
    try:
        return {
            str(row[1])
            for row in con.execute(f"pragma table_info({_quote_ident(table_name)})").fetchall()
        }
    except duckdb.Error:
        return set()


def _row_count(con: duckdb.DuckDBPyConnection, table_name: str) -> int:
    row = con.execute(f"select count(*) from {_quote_ident(table_name)}").fetchone()
    if row is None:
        return 0
    return int(row[0])


def _write_artifacts(
    *,
    request: DownstreamReferenceAuditRequest,
    status: str,
    live_next_card: str,
    usage_semantics: dict[str, Any],
    schema_payload: dict[str, Any],
    category_counts: dict[str, int],
    issues: list[str],
) -> tuple[Path, Path, Path, Path, Path]:
    request.report_dir.mkdir(parents=True, exist_ok=True)
    request.temp_dir.mkdir(parents=True, exist_ok=True)
    manifest = _manifest_payload(
        request,
        status,
        live_next_card,
        usage_semantics,
        schema_payload,
        category_counts,
        issues,
    )
    manifest_path = request.report_dir / "downstream-reference-audit-manifest.json"
    report_path = request.report_dir / "downstream-reference-audit-report.md"
    closeout_path = request.report_dir / "closeout.md"
    temp_manifest_path = request.temp_dir / "downstream-reference-audit-temp-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path.write_text(report_markdown(manifest), encoding="utf-8")
    closeout_path.write_text(closeout_markdown(manifest), encoding="utf-8")
    temp_manifest_path.write_text(
        json.dumps(
            {
                "run_id": request.run_id,
                "status": status,
                "source_usage_readout_manifest": str(request.usage_readout_manifest_path),
                "report_manifest": str(manifest_path),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    validated_zip = request.validated_root / f"Asteria-{request.run_id}.zip"
    request.validated_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(validated_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in (manifest_path, report_path, closeout_path, temp_manifest_path):
            archive.write(path, arcname=path.name)
    return manifest_path, report_path, closeout_path, temp_manifest_path, validated_zip


def _manifest_payload(
    request: DownstreamReferenceAuditRequest,
    status: str,
    live_next_card: str,
    usage_semantics: dict[str, Any],
    schema_payload: dict[str, Any],
    category_counts: dict[str, int],
    issues: list[str],
) -> dict[str, Any]:
    return {
        "run_id": request.run_id,
        "module": "pipeline",
        "stage": "v1_downstream_reference_audit",
        "status": status,
        "route_type": "roadmap_only_read_only_post_terminal_supplement",
        "live_next_card": live_next_card,
        "live_next_card_preserved": live_next_card == "none / terminal",
        "formal_db_mutation": "no",
        "formal_data_root": str(request.formal_data_root),
        "source_usage_readout_manifest": str(request.usage_readout_manifest_path),
        "usage_readout_semantics": usage_semantics,
        "formal_schema": schema_payload,
        "external_reference_sources": _external_reference_sources(),
        "benchmark_rows": [row.__dict__ for row in BENCHMARK_ROWS],
        "category_counts": category_counts,
        "issue_count": len(issues),
        "issues": issues,
        "next_route_card": V1_USAGE_VALUE_DECISION_CARD,
    }


def _external_reference_sources() -> list[dict[str, str]]:
    return [
        {
            "project": "hikyuu",
            "url": "https://github.com/fasiondog/hikyuu",
            "role": "system trading component decomposition",
        },
        {
            "project": "hikyuu_sys",
            "url": "https://hikyuu.readthedocs.io/zh-cn/latest/trade_sys/system.html",
            "role": "SYS / Signal / MoneyManager / Slippage / TradeRequest reference",
        },
        {
            "project": "hikyuu_portfolio",
            "url": "https://hikyuu.readthedocs.io/zh-cn/latest/trade_portfolio/trade_portfolio.html",
            "role": "PF / selector / allocation reference",
        },
        {
            "project": "finhack",
            "url": "https://github.com/everything-is-simple/finhack",
            "role": "research to backtest to live access workflow reference",
        },
        {
            "project": "easytrader_miniqmt",
            "url": "https://easytrader.readthedocs.io/zh-cn/master/miniqmt/",
            "role": "broker order / entrust / trade callback boundary reference",
        },
    ]


def _quote_ident(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'
