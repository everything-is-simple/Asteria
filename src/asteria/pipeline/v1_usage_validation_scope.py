from __future__ import annotations

import json
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

import duckdb

from asteria.pipeline.v1_usage_validation_scope_contracts import (
    V1_APPLICATION_DB_READINESS_AUDIT_CARD,
    V1_USAGE_VALIDATION_SCOPE_CARD,
    UsageValidationScopeManualOverride,
    UsageValidationScopeRequest,
    UsageValidationScopeSelectionEntry,
    UsageValidationScopeSummary,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


def run_v1_usage_validation_scope(
    request: UsageValidationScopeRequest,
) -> UsageValidationScopeSummary:
    live_next_card = _load_terminal_live_next_card(request.repo_root)
    _assert_roadmap_route_registered(request.repo_root)
    manual_overrides = _load_manual_overrides(request.manual_override_path)
    selected_entries, total_trading_days = _select_entries(request, manual_overrides)
    manifest_path, closeout_path, validated_zip = _write_scope_artifacts(
        request=request,
        live_next_card=live_next_card,
        selected_entries=selected_entries,
        total_trading_days=total_trading_days,
        manual_overrides=manual_overrides,
    )
    return UsageValidationScopeSummary(
        run_id=request.run_id,
        status="completed",
        live_next_card=live_next_card,
        live_next_card_preserved=(live_next_card == "none / terminal"),
        next_route_card=V1_APPLICATION_DB_READINESS_AUDIT_CARD,
        level1_industry_count=len(selected_entries),
        selected_symbol_count=len(selected_entries),
        total_trading_days=total_trading_days,
        manifest_path=str(manifest_path),
        closeout_path=str(closeout_path),
        validated_zip=str(validated_zip),
    )


def _load_terminal_live_next_card(repo_root: Path) -> str:
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    latest_release = str(registry.get("latest_mainline_release_run_id", ""))
    current_allowed_next_card = str(registry.get("current_allowed_next_card", ""))
    if latest_release != "final-release-closeout-card":
        raise ValueError("v1 usage validation route requires final release closeout terminal state")
    if current_allowed_next_card not in {"", "none"}:
        raise ValueError("v1 usage validation scope card must not reopen live next card")
    return "none / terminal"


def _assert_roadmap_route_registered(repo_root: Path) -> None:
    roadmap_text = (
        repo_root / "docs" / "03-refactor" / "05-asteria-v1-usage-validation-roadmap-v1.md"
    ).read_text(encoding="utf-8")
    for token in (
        V1_USAGE_VALIDATION_SCOPE_CARD,
        V1_APPLICATION_DB_READINESS_AUDIT_CARD,
        "只读使用验证",
    ):
        if token not in roadmap_text:
            raise ValueError(f"v1 usage validation roadmap is missing token: {token}")


def _load_manual_overrides(
    override_path: Path | None,
) -> dict[str, UsageValidationScopeManualOverride]:
    if override_path is None:
        return {}
    payload = json.loads(override_path.read_text(encoding="utf-8"))
    output: dict[str, UsageValidationScopeManualOverride] = {}
    for level1_industry, raw in payload.items():
        symbol = str(raw["symbol"]).strip()
        reason = str(raw["reason"]).strip()
        if not symbol or not reason:
            raise ValueError("manual override entries require non-empty symbol and reason")
        output[str(level1_industry).strip()] = UsageValidationScopeManualOverride(
            level1_industry=str(level1_industry).strip(),
            symbol=symbol,
            reason=reason,
        )
    return output


def _select_entries(
    request: UsageValidationScopeRequest,
    manual_overrides: dict[str, UsageValidationScopeManualOverride],
) -> tuple[list[UsageValidationScopeSelectionEntry], int]:
    rows = _load_candidate_rows(request)
    if not rows:
        raise ValueError("no v1 usage validation scope candidates were found")
    output: list[UsageValidationScopeSelectionEntry] = []
    seen_level1: set[str] = set()
    total_trading_days = _as_int(rows[0]["total_trading_days"])
    for row in rows:
        level1 = str(row["level1_industry"])
        if level1 in seen_level1:
            continue
        override = manual_overrides.get(level1)
        chosen = row if override is None else _resolve_override(level1, override, rows)
        output.append(_build_selection_entry(chosen, override))
        seen_level1.add(level1)
    if len(output) != request.expected_industry_count:
        raise ValueError(
            f"expected {request.expected_industry_count} level-1 industries but selected "
            f"{len(output)}"
        )
    return sorted(output, key=lambda item: item.level1_industry), total_trading_days


def _load_candidate_rows(request: UsageValidationScopeRequest) -> list[dict[str, object]]:
    query = """
    with calendar as (
        select count(*) as total_trading_days
        from meta.trade_calendar
        where calendar_code = 'CN_A_SHARE'
          and is_open = true
          and trade_date between ? and ?
    ),
    bar as (
        select
            symbol,
            count(distinct trade_date) as coverage_days_2024,
            avg(amount) as amount_rank_metric,
            sum(amount) as total_amount_2024,
            min(trade_date) as observed_start_2024,
            max(trade_date) as observed_end_2024
        from base.market_base_bar
        where asset_type = 'stock'
          and timeframe = 'day'
          and price_line = 'execution_price_line'
          and adj_mode = 'none'
          and trade_date between ? and ?
        group by symbol
    )
    select
        split_part(ic.industry_name, '|', 1) as level1_industry,
        ic.industry_code,
        im.symbol,
        im.first_seen_date,
        im.latest_seen_date,
        cast(bar.coverage_days_2024 as bigint) as coverage_days_2024,
        cast((select total_trading_days from calendar) as bigint) as total_trading_days,
        cast(bar.amount_rank_metric as double) as amount_rank_metric,
        cast(bar.total_amount_2024 as double) as total_amount_2024,
        bar.observed_start_2024,
        bar.observed_end_2024
    from meta.industry_classification ic
    join meta.instrument_master im on im.instrument_id = ic.instrument_id
    join bar on bar.symbol = im.symbol
    where ic.industry_schema = ?
      and im.asset_type = 'stock'
    order by
        level1_industry,
        coverage_days_2024 desc,
        amount_rank_metric desc,
        im.symbol asc
    """
    with duckdb.connect(":memory:") as con:
        con.execute(f"attach '{request.market_meta_db.as_posix()}' as meta")
        con.execute(f"attach '{request.market_base_day_db.as_posix()}' as base")
        result = con.execute(
            query,
            [
                request.start_date.isoformat(),
                request.end_date.isoformat(),
                request.start_date.isoformat(),
                request.end_date.isoformat(),
                request.industry_schema,
            ],
        )
        columns = [desc[0] for desc in result.description]
        return [dict(zip(columns, row, strict=True)) for row in result.fetchall()]


def _resolve_override(
    level1_industry: str,
    override: UsageValidationScopeManualOverride,
    rows: list[dict[str, object]],
) -> dict[str, object]:
    for row in rows:
        if str(row["level1_industry"]) == level1_industry and str(row["symbol"]) == override.symbol:
            return row
    raise ValueError(
        f"manual override symbol {override.symbol} is not available in level1 industry "
        f"{level1_industry}"
    )


def _build_selection_entry(
    row: dict[str, object],
    override: UsageValidationScopeManualOverride | None,
) -> UsageValidationScopeSelectionEntry:
    coverage_days = _as_int(row["coverage_days_2024"])
    total_trading_days = _as_int(row["total_trading_days"])
    return UsageValidationScopeSelectionEntry(
        level1_industry=str(row["level1_industry"]),
        industry_code=str(row["industry_code"]),
        symbol=str(row["symbol"]),
        first_seen_date=_date_text(row["first_seen_date"]),
        latest_seen_date=_date_text(row["latest_seen_date"]),
        coverage_days_2024=coverage_days,
        total_trading_days=total_trading_days,
        coverage_complete=(coverage_days == total_trading_days),
        amount_rank_metric=_as_float(row["amount_rank_metric"]),
        total_amount_2024=_as_float(row["total_amount_2024"]),
        observed_start_2024=_date_text(row["observed_start_2024"]),
        observed_end_2024=_date_text(row["observed_end_2024"]),
        manual_override_reason=None if override is None else override.reason,
    )


def _write_scope_artifacts(
    *,
    request: UsageValidationScopeRequest,
    live_next_card: str,
    selected_entries: list[UsageValidationScopeSelectionEntry],
    total_trading_days: int,
    manual_overrides: dict[str, UsageValidationScopeManualOverride],
) -> tuple[Path, Path, Path]:
    report_dir = request.report_root / "pipeline" / _utc_now().date().isoformat() / request.run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    manual_override_items = [entry.as_dict() for entry in manual_overrides.values()]
    manifest = {
        "run_id": request.run_id,
        "module": "pipeline",
        "stage": "v1_usage_validation_scope_freeze",
        "status": "completed",
        "route_type": "roadmap_only_read_only_post_terminal",
        "live_next_card": live_next_card,
        "latest_mainline_release_run_id": "final-release-closeout-card",
        "next_route_card": V1_APPLICATION_DB_READINESS_AUDIT_CARD,
        "industry_schema": request.industry_schema,
        "industry_schema_source": request.industry_source_reference,
        "date_window": {
            "start": request.start_date.isoformat(),
            "end": request.end_date.isoformat(),
            "total_trading_days": total_trading_days,
        },
        "research_question": request.research_question,
        "report_shape": request.report_shape,
        "db_permission": request.db_permission,
        "selection_rule": request.selection_rule,
        "appendix_policy": request.appendix_policy,
        "level1_industry_count": len(selected_entries),
        "selected_entries": [entry.as_dict() for entry in selected_entries],
        "manual_overrides": manual_override_items,
        "caveats": [
            "This scope card does not claim formal ST coverage.",
            "This scope card does not claim formal long-suspension coverage.",
            "This scope card does not claim full listing or delisting lifecycle coverage.",
            (
                "This scope card only freezes a read-only usage-validation scope "
                "and must not mutate H:/Asteria-data."
            ),
        ],
    }
    manifest_path = report_dir / "scope-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    appendix_candidates = ", ".join(entry.symbol for entry in selected_entries[:5])
    closeout_path = report_dir / "closeout.md"
    closeout_path.write_text(
        "\n".join(
            [
                "# V1 Usage Validation Scope Freeze Closeout",
                "",
                f"- run_id: `{request.run_id}`",
                "- route_type: `roadmap_only_read_only_post_terminal`",
                f"- live_next_card: `{live_next_card}`",
                f"- next_route_card: `{V1_APPLICATION_DB_READINESS_AUDIT_CARD}`",
                f"- level1_industry_count: `{len(selected_entries)}`",
                f"- selected_symbol_count: `{len(selected_entries)}`",
                (
                    "- date_window: "
                    f"`{request.start_date.isoformat()}..{request.end_date.isoformat()}`"
                ),
                f"- report_shape: `{request.report_shape}`",
                f"- db_permission: `{request.db_permission}`",
                f"- appendix_policy: `{request.appendix_policy}`",
                f"- appendix_candidate_pool_head: `{appendix_candidates}`",
                "",
                "## Caveat",
                "",
                "- 不宣称正式 ST、停牌、完整上市退市或历史行业沿革 coverage 已补齐。",
                "- 本卡只冻结范围，不改 `governance/module_gate_registry.toml` 的 terminal truth。",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    validated_zip = request.validated_root / f"Asteria-{request.run_id}.zip"
    validated_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(validated_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(manifest_path, arcname="scope-manifest.json")
        archive.write(closeout_path, arcname="closeout.md")
    return manifest_path, closeout_path, validated_zip


def _date_text(value: object) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _as_int(value: object) -> int:
    return int(str(value))


def _as_float(value: object) -> float:
    return float(str(value))


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
