from __future__ import annotations

import json
from datetime import date
from typing import Any

from asteria.pipeline.v1_usage_readout_report_contracts import (
    V1_USAGE_READOUT_REPORT_CARD,
    UsageReadoutReportRequest,
)

SECTION_TITLES = {
    "market_structure": "市场结构",
    "opportunity": "机会在哪里",
    "position_portfolio": "持仓和组合解释",
    "trade_intent": "交易意图",
    "system_pipeline": "全链路自洽",
}

RETAINED_CAVEATS = [
    "fill_ledger source-bound gap retained",
    "ST / suspension / listing-delisting lifecycle source caveats retained",
    "historical industry lineage caveat retained",
    "calendar semantic gap remains a usage-readout caveat, not a release blocker",
    "this card does not open production daily incremental activation",
]


def manifest_payload(
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
) -> dict[str, Any]:
    return {
        "run_id": request.run_id,
        "card_id": V1_USAGE_READOUT_REPORT_CARD,
        "module": "pipeline",
        "stage": "v1_usage_readout_report",
        "status": status,
        "route_type": "roadmap_only_read_only_post_terminal",
        "live_next_card": live_next_card,
        "live_next_card_preserved": live_next_card == "none / terminal",
        "source_scope_run_id": scope_manifest.get("run_id"),
        "source_scope_manifest": str(request.scope_manifest_path),
        "formal_data_root": str(request.formal_data_root),
        "date_window": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "selected_symbol_count": len(symbols),
        "selected_symbols": symbols,
        "readout": readout,
        "issue_count": len(issues),
        "issues": issues,
        "caveats": RETAINED_CAVEATS,
        "next_route_card": next_route_card,
    }


def report_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# Asteria v1 Usage Readout Report",
        "",
        f"- run_id: `{manifest['run_id']}`",
        "- route_type: `roadmap_only_read_only_post_terminal`",
        f"- status: `{manifest['status']}`",
        f"- live_next_card: `{manifest['live_next_card']}`",
        f"- date_window: `{manifest['date_window']['start']}..{manifest['date_window']['end']}`",
        f"- selected_symbol_count: `{manifest['selected_symbol_count']}`",
        "",
        "## 人话结论",
        "",
        (
            "本卡已经把 v1 的结构、机会、持仓、组合、交易意图和全链路读出做成"
            "第一份只读研究报告；价值裁决留给下一张路线卡。"
            if manifest["status"].startswith("passed")
            else "本卡发现读出缺口，只登记 gap，不补库、不重建、不改 live gate。"
        ),
        "",
    ]
    for section, title in SECTION_TITLES.items():
        lines.extend([f"## {title}", ""])
        for table_name, payload in manifest["readout"].get(section, {}).items():
            lines.extend(_table_lines(table_name, payload))
        lines.append("")
    lines.extend(["## 保留 caveat", ""])
    lines.extend(f"- {caveat}" for caveat in manifest["caveats"])
    if manifest["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in manifest["issues"])
    lines.extend(["", f"下一张路线卡：`{manifest['next_route_card']}`", ""])
    return "\n".join(lines)


def closeout_markdown(manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# V1 Usage Readout Report Closeout",
            "",
            f"- run_id: `{manifest['run_id']}`",
            f"- status: `{manifest['status']}`",
            f"- live_next_card: `{manifest['live_next_card']}`",
            f"- next_route_card: `{manifest['next_route_card']}`",
            f"- selected_symbol_count: `{manifest['selected_symbol_count']}`",
            f"- issue_count: `{manifest['issue_count']}`",
            "- H:/Asteria-data mutation: `no`",
            "",
            "本卡只读消费正式 DB 并产出人读报告，不执行补库、重建、promote 或日更生产化。",
            "",
        ]
    )


def _table_lines(table_name: str, payload: dict[str, Any]) -> list[str]:
    lines = [
        f"### `{payload['db_name']}` / `{table_name}`",
        "",
        f"- row_count: `{payload['row_count']}`",
        f"- symbol_filter_applied: `{str(payload['symbol_filter_applied']).lower()}`",
        f"- date_filter_applied: `{str(payload['date_filter_applied']).lower()}`",
    ]
    if payload["scope_note"]:
        lines.append(f"- scope_note: `{payload['scope_note']}`")
    if payload["group_counts"]:
        top_group = payload["group_counts"][0]
        lines.append(f"- top_distribution: `{json.dumps(top_group, ensure_ascii=False)}`")
    if payload["reason_distribution"]:
        lines.append(
            "- reason_distribution: "
            f"`{json.dumps(payload['reason_distribution'], ensure_ascii=False)}`"
        )
    if payload["stage_distribution"]:
        lines.append(
            "- stage_distribution: "
            f"`{json.dumps(payload['stage_distribution'], ensure_ascii=False)}`"
        )
    if payload["lineage"]:
        lines.append(f"- lineage: `{json.dumps(payload['lineage'], ensure_ascii=False)}`")
    if payload["issue"]:
        lines.append(f"- issue: `{payload['issue']}`")
    lines.append("")
    return lines
