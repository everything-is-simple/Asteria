from __future__ import annotations

from typing import Any

CATEGORY_TITLES = {
    "usage_blocker": "usage blocker",
    "strategy_quality_issue": "strategy quality issue",
    "source_caveat": "source caveat",
    "future_enhancement": "future enhancement",
}


def report_markdown(manifest: dict[str, Any]) -> str:
    usage = manifest["input_evidence"]["usage_readout"]
    reference = manifest["input_evidence"]["downstream_reference"]
    lines = [
        "# Asteria v1 Usage Value Decision",
        "",
        f"- run_id: `{manifest['run_id']}`",
        "- route_type: `roadmap_only_read_only_post_terminal`",
        f"- status: `{manifest['status']}`",
        f"- live_next_card: `{manifest['live_next_card']}`",
        f"- value_decision: `{manifest['value_decision']}`",
        f"- next_route_card: `{manifest['next_route_card']}`",
        "- H:/Asteria-data mutation: `no`",
        "",
        "## 人话结论",
        "",
        manifest["human_conclusion"],
        "",
        "## Decision Evidence",
        "",
        f"- usage_blocker = {manifest['category_counts']['usage_blocker']}",
        f"- order_intent_ledger = {usage['order_intent_row_count']}",
        f"- order_rejection_ledger = {usage['order_rejection_row_count']}",
        f"- fill_ledger row_count = {reference['fill_ledger_row_count']}",
        (f"- rejection_scope_note: `{usage.get('order_rejection_scope_note', 'not available')}`"),
        "",
    ]
    for category, title in CATEGORY_TITLES.items():
        lines.extend([f"## {title}", ""])
        entries = manifest["decision_categories"][category]
        if entries:
            lines.extend(f"- {entry}" for entry in entries)
        else:
            lines.append("- none")
        lines.append("")
    if manifest["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in manifest["issues"])
        lines.append("")
    lines.extend(
        [
            "本卡只做研究使用价值裁决；不能宣称收益回测，不能宣称真实成交闭环，",
            "也不能宣称实盘自动交易能力。",
            "",
        ]
    )
    return "\n".join(lines)


def closeout_markdown(manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# V1 Usage Value Decision Closeout",
            "",
            f"- run_id: `{manifest['run_id']}`",
            f"- status: `{manifest['status']}`",
            f"- live_next_card: `{manifest['live_next_card']}`",
            f"- value_decision: `{manifest['value_decision']}`",
            f"- next_route_card: `{manifest['next_route_card']}`",
            f"- issue_count: `{manifest['issue_count']}`",
            "- formal_db_mutation: `no`",
            "",
            manifest["human_conclusion"],
            "",
        ]
    )
