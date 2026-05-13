from __future__ import annotations

import json
from typing import Any

CATEGORY_LABELS = {
    "covered": "已覆盖",
    "expression_risk": "表达风险",
    "real_gap": "真实缺口",
    "not_applicable_reference": "不适用外部参考",
}


def report_markdown(manifest: dict[str, Any]) -> str:
    usage = manifest["usage_readout_semantics"]
    lines = [
        "# Asteria Downstream Reference Audit",
        "",
        f"- run_id: `{manifest['run_id']}`",
        "- route_type: `roadmap_only_read_only_post_terminal_supplement`",
        f"- status: `{manifest['status']}`",
        f"- live_next_card: `{manifest['live_next_card']}`",
        f"- next_route_card: `{manifest['next_route_card']}`",
        "- H:/Asteria-data mutation: `no`",
        "",
        "## 人话结论",
        "",
        (
            "下游四层的基本职责拆法没有明显偏离同类量化系统；真正要带入第 4 卡的是"
            "表达口径、真实成交证据和生产交易边界，而不是重写 Position / Portfolio / "
            "Trade / System。"
        ),
        "",
        "## Usage Readout Sanity",
        "",
        f"- order_intent_ledger = {usage['order_intent_row_count']}",
        f"- order_rejection_ledger = {usage['order_rejection_row_count']}",
        f"- rejection_scope_note: `{usage['order_rejection_scope_note']}`",
        (
            "- rejection_reason_distribution: "
            f"`{json.dumps(usage['rejection_reason_distribution'], ensure_ascii=False)}`"
        ),
        "",
        "## Benchmark Matrix",
        "",
        "| dimension | category | decision_bucket | judgment |",
        "|---|---|---|---|",
    ]
    for row in manifest["benchmark_rows"]:
        label = CATEGORY_LABELS[row["category"]]
        lines.append(
            "| "
            f"`{row['dimension']}` | {label} | `{row['decision_bucket']}` | "
            f"{row['audit_judgment']} |"
        )
    lines.extend(
        [
            "",
            "## Category Counts",
            "",
        ]
    )
    for category, count in manifest["category_counts"].items():
        lines.append(f"- {CATEGORY_LABELS[category]}: `{count}`")
    if manifest["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in manifest["issues"])
    lines.extend(["", "本报告只作为第 4 卡裁决输入，不修改 live gate，不写正式 DB。", ""])
    return "\n".join(lines)


def closeout_markdown(manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Downstream Reference Audit Closeout",
            "",
            f"- run_id: `{manifest['run_id']}`",
            f"- status: `{manifest['status']}`",
            f"- live_next_card: `{manifest['live_next_card']}`",
            f"- next_route_card: `{manifest['next_route_card']}`",
            f"- issue_count: `{manifest['issue_count']}`",
            "- formal_db_mutation: `no`",
            "",
            "结论：本输入只读对照下游语义，不重定义业务模块，不打开 production trading。",
            "",
        ]
    )
