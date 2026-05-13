from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

from asteria.pipeline.v1_usage_value_decision_contracts import (
    V1_DAILY_INCREMENTAL_PRODUCTION_SCOPE_CARD,
    V1_DOWNSTREAM_REFERENCE_AUDIT_RUN_ID,
    V1_USAGE_READOUT_REPORT_RUN_ID,
    VALUE_DECISION_INSUFFICIENT,
    VALUE_DECISION_RESEARCH_USABLE,
    UsageValueDecisionRequest,
    UsageValueDecisionSummary,
)
from asteria.pipeline.v1_usage_value_decision_render import (
    closeout_markdown,
    report_markdown,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


def run_v1_usage_value_decision(
    request: UsageValueDecisionRequest,
) -> UsageValueDecisionSummary:
    live_next_card = _load_terminal_live_next_card(request.repo_root)
    route_issues = _collect_route_issues(request.repo_root)
    usage_manifest, usage_issues = _load_usage_readout_manifest(request.usage_readout_manifest_path)
    reference_manifest, reference_issues = _load_downstream_reference_manifest(
        request.downstream_reference_manifest_path
    )
    issues = [*route_issues, *usage_issues, *reference_issues]
    input_evidence = _input_evidence(usage_manifest, reference_manifest)
    decision_categories = _decision_categories(issues)
    category_counts = {key: len(value) for key, value in decision_categories.items()}
    value_decision = VALUE_DECISION_RESEARCH_USABLE if not issues else VALUE_DECISION_INSUFFICIENT
    status = (
        "passed / usage value decision completed"
        if not issues
        else "blocked / usage value decision input gaps found"
    )
    human_conclusion = _human_conclusion(value_decision)

    manifest_path, report_path, closeout_path, temp_manifest_path, validated_zip = _write_artifacts(
        request=request,
        status=status,
        live_next_card=live_next_card,
        value_decision=value_decision,
        human_conclusion=human_conclusion,
        input_evidence=input_evidence,
        decision_categories=decision_categories,
        category_counts=category_counts,
        issues=issues,
    )
    return UsageValueDecisionSummary(
        run_id=request.run_id,
        status=status,
        live_next_card=live_next_card,
        live_next_card_preserved=live_next_card == "none / terminal",
        value_decision=value_decision,
        human_conclusion=human_conclusion,
        issue_count=len(issues),
        issues=issues,
        category_counts=category_counts,
        next_route_card=V1_DAILY_INCREMENTAL_PRODUCTION_SCOPE_CARD,
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
        raise ValueError("usage value decision requires terminal final release closeout")
    if str(registry.get("current_allowed_next_card", "")) not in {"", "none"}:
        raise ValueError("usage value decision must not reopen live next card")
    return "none / terminal"


def _collect_route_issues(repo_root: Path) -> list[str]:
    roadmap_path = (
        repo_root / "docs" / "03-refactor" / "05-asteria-v1-usage-validation-roadmap-v1.md"
    )
    conclusion_path = repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    roadmap_text = roadmap_path.read_text(encoding="utf-8")
    conclusion_text = conclusion_path.read_text(encoding="utf-8")
    issues: list[str] = []
    if "`v1-usage-value-decision-card`" not in roadmap_text:
        issues.append("roadmap does not register v1-usage-value-decision-card")
    if "`daily-incremental-production-scope-card`" not in roadmap_text:
        issues.append("roadmap does not register daily-incremental-production-scope-card")
    if V1_USAGE_READOUT_REPORT_RUN_ID not in conclusion_text:
        issues.append("usage readout report predecessor is not registered")
    if V1_DOWNSTREAM_REFERENCE_AUDIT_RUN_ID not in conclusion_text:
        issues.append("downstream reference audit input is not registered")
    return issues


def _load_usage_readout_manifest(path: Path) -> tuple[dict[str, Any], list[str]]:
    manifest, issues = _load_json_manifest(path, "usage readout manifest")
    if issues:
        return manifest, issues
    if manifest.get("run_id") != V1_USAGE_READOUT_REPORT_RUN_ID:
        issues.append("usage readout manifest run_id does not match card 3")
    if not str(manifest.get("status", "")).startswith("passed"):
        issues.append("usage readout manifest is not passed")
    if manifest.get("live_next_card") != "none / terminal":
        issues.append("usage readout manifest does not preserve terminal live next")
    issues.extend(str(issue) for issue in manifest.get("issues", []))
    return manifest, issues


def _load_downstream_reference_manifest(path: Path) -> tuple[dict[str, Any], list[str]]:
    manifest, issues = _load_json_manifest(path, "downstream reference audit manifest")
    if issues:
        return manifest, issues
    if manifest.get("run_id") != V1_DOWNSTREAM_REFERENCE_AUDIT_RUN_ID:
        issues.append("downstream reference audit manifest run_id does not match")
    if not str(manifest.get("status", "")).startswith("passed"):
        issues.append("downstream reference audit manifest is not passed")
    if manifest.get("live_next_card") != "none / terminal":
        issues.append("downstream reference audit does not preserve terminal live next")
    issues.extend(str(issue) for issue in manifest.get("issues", []))
    return manifest, issues


def _load_json_manifest(path: Path, label: str) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {}, [f"{label} missing: {path}"]
    return json.loads(path.read_text(encoding="utf-8")), []


def _input_evidence(
    usage_manifest: dict[str, Any],
    reference_manifest: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    trade = usage_manifest.get("readout", {}).get("trade_intent", {})
    intent = trade.get("trade.duckdb::order_intent_ledger", {})
    rejection = trade.get("trade.duckdb::order_rejection_ledger", {})
    formal_schema = reference_manifest.get("formal_schema", {})
    fill = formal_schema.get("trade.duckdb::fill_ledger", {})
    return {
        "usage_readout": {
            "source_run_id": usage_manifest.get("run_id"),
            "selected_symbol_count": int(usage_manifest.get("selected_symbol_count", 0)),
            "date_window": usage_manifest.get("date_window", {}),
            "order_intent_row_count": int(intent.get("row_count", 0)),
            "order_rejection_row_count": int(rejection.get("row_count", 0)),
            "order_rejection_symbol_filter_applied": bool(rejection.get("symbol_filter_applied")),
            "order_rejection_scope_note": rejection.get("scope_note"),
            "caveats": usage_manifest.get("caveats", []),
        },
        "downstream_reference": {
            "source_run_id": reference_manifest.get("run_id"),
            "benchmark_category_counts": reference_manifest.get("category_counts", {}),
            "fill_ledger_row_count": int(fill.get("row_count", 0)),
            "fill_ledger_has_symbol": bool(fill.get("has_symbol", False)),
        },
    }


def _decision_categories(issues: list[str]) -> dict[str, list[str]]:
    return {
        "usage_blocker": list(issues),
        "strategy_quality_issue": [
            (
                "order_intent_ledger = 1 and order_rejection_ledger = 1158 use "
                "different scopes; this must stay visible in research reports."
            ),
            (
                "Signal -> Portfolio admission -> Trade intent conversion is conservative "
                "and should be evaluated as strategy quality, not runtime failure."
            ),
        ],
        "source_caveat": [
            "fill_ledger row_count = 0, so v1 cannot prove real fill closure.",
            "ST / suspension / listing-delisting lifecycle source facts remain retained.",
            "calendar semantic gap remains retained and is not a release blocker.",
        ],
        "future_enhancement": [
            "Richer money management and portfolio risk models.",
            "Broker adapter and live order operation integration.",
            "Strategy return backtest and PnL attribution.",
            "Production daily incremental activation after a separate scope card.",
        ],
    }


def _human_conclusion(value_decision: str) -> str:
    if value_decision == VALUE_DECISION_RESEARCH_USABLE:
        return (
            "Asteria 当前 v1 有研究使用价值，但带有明确 caveat：它能解释结构、"
            "机会、持仓、组合和交易意图，不能宣称收益回测、真实成交闭环或实盘交易能力。"
        )
    return "Asteria 当前 v1 使用价值裁决证据不足；必须先补齐输入证据再进入下一张路线卡。"


def _write_artifacts(
    *,
    request: UsageValueDecisionRequest,
    status: str,
    live_next_card: str,
    value_decision: str,
    human_conclusion: str,
    input_evidence: dict[str, dict[str, Any]],
    decision_categories: dict[str, list[str]],
    category_counts: dict[str, int],
    issues: list[str],
) -> tuple[Path, Path, Path, Path, Path]:
    request.report_dir.mkdir(parents=True, exist_ok=True)
    request.temp_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": request.run_id,
        "card_id": "v1-usage-value-decision-card",
        "module": "pipeline",
        "stage": "v1_usage_value_decision",
        "status": status,
        "route_type": "roadmap_only_read_only_post_terminal",
        "live_next_card": live_next_card,
        "live_next_card_preserved": live_next_card == "none / terminal",
        "formal_db_mutation": "no",
        "source_usage_readout_manifest": str(request.usage_readout_manifest_path),
        "source_downstream_reference_manifest": str(request.downstream_reference_manifest_path),
        "value_decision": value_decision,
        "human_conclusion": human_conclusion,
        "input_evidence": input_evidence,
        "decision_categories": decision_categories,
        "category_counts": category_counts,
        "issue_count": len(issues),
        "issues": issues,
        "next_route_card": V1_DAILY_INCREMENTAL_PRODUCTION_SCOPE_CARD,
    }
    manifest_path = request.report_dir / "usage-value-decision-manifest.json"
    report_path = request.report_dir / "usage-value-decision-report.md"
    closeout_path = request.report_dir / "closeout.md"
    temp_manifest_path = request.temp_dir / "usage-value-decision-temp-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path.write_text(report_markdown(manifest), encoding="utf-8")
    closeout_path.write_text(closeout_markdown(manifest), encoding="utf-8")
    temp_manifest_path.write_text(
        json.dumps(
            {
                "run_id": request.run_id,
                "status": status,
                "source_usage_readout_manifest": str(request.usage_readout_manifest_path),
                "source_downstream_reference_manifest": str(
                    request.downstream_reference_manifest_path
                ),
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
