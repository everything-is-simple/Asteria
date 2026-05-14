from __future__ import annotations

from typing import Any

from asteria.pipeline.v1_vectorbt_portfolio_analytics_proof_contracts import (
    V1_VECTORBT_PORTFOLIO_ANALYTICS_PROOF_CARD,
    VectorbtPortfolioAnalyticsProofRequest,
)


def manifest_payload(
    request: VectorbtPortfolioAnalyticsProofRequest,
    *,
    status: str,
    live_next_card: str,
    selected_symbols: list[str],
    signal_symbol_count: int,
    date_window: dict[str, str],
    aggregate: dict[str, Any],
    matrix_audit: dict[str, Any],
    skip_reason_distribution: list[dict[str, Any]],
    issues: list[str],
    next_route_card: str,
) -> dict[str, Any]:
    return {
        "run_id": request.run_id,
        "card_id": V1_VECTORBT_PORTFOLIO_ANALYTICS_PROOF_CARD,
        "module": "pipeline",
        "stage": "v1_vectorbt_portfolio_analytics_proof",
        "status": status,
        "route_type": "roadmap_only_read_only_post_terminal_vectorbt_portfolio_proof",
        "live_next_card": live_next_card,
        "live_next_card_preserved": live_next_card == "none / terminal",
        "formal_db_mutation": "no",
        "formal_data_root": str(request.formal_data_root),
        "source_scope_manifest": str(request.scope_manifest_path),
        "selected_symbol_count": len(selected_symbols),
        "selected_symbols": selected_symbols,
        "signal_symbol_count": signal_symbol_count,
        "date_window": date_window,
        "engine": "vectorbt",
        "execution_semantics": {
            "signal_timing": "T+0 signal",
            "execution_hint": "T_PLUS_1_OPEN",
            "trade_date_policy": "next_trading_day_after_signal_date",
            "order_price_field": "open",
            "valuation_price_field": "close",
            "portfolio_mode": "multi_asset_matrix_cash_shared",
        },
        "parameters": {
            "initial_cash": request.initial_cash,
            "fees": request.fees,
        },
        "aggregate": aggregate,
        "matrix_audit": matrix_audit,
        "skip_reason_distribution": skip_reason_distribution,
        "issue_count": len(issues),
        "issues": issues,
        "non_claims": [
            "not a production portfolio backtest",
            "not a real fill ledger",
            "not an account update loop",
            "not a broker adapter",
            "not live trading capability",
        ],
        "next_route_card": next_route_card,
    }


def report_markdown(manifest: dict[str, Any]) -> str:
    aggregate = manifest["aggregate"]
    lines = [
        "# Asteria v1 Vectorbt Portfolio Analytics Proof",
        "",
        f"- run_id: `{manifest['run_id']}`",
        f"- status: `{manifest['status']}`",
        f"- live_next_card: `{manifest['live_next_card']}`",
        f"- formal_db_mutation: `{manifest['formal_db_mutation']}`",
        f"- engine: `{manifest['engine']}`",
        (f"- date_window: `{manifest['date_window']['start']}..{manifest['date_window']['end']}`"),
        f"- selected_symbol_count: `{manifest['selected_symbol_count']}`",
        f"- signal_symbol_count: `{manifest['signal_symbol_count']}`",
        "",
        "## 人话结论",
        "",
        _human_conclusion(manifest),
        "",
        "## 执行语义",
        "",
        "- `T+0 signal -> T+1 open execution`",
        "- `vectorbt` uses `close` for valuation and `open` for order price.",
        "- 本 proof 是组合级绩效 / 持仓暴露 / 换手 / 回撤研究读数，不是实盘交易能力。",
        "",
        "## Portfolio Analytics",
        "",
        f"- portfolio_total_return_pct: `{_fmt(aggregate.get('portfolio_total_return_pct'))}`",
        f"- portfolio_max_drawdown_pct: `{_fmt(aggregate.get('portfolio_max_drawdown_pct'))}`",
        f"- total_trade_count: `{aggregate.get('total_trade_count', 0)}`",
        f"- order_activity_count: `{aggregate.get('order_activity_count', 0)}`",
        f"- active_position_day_count: `{aggregate.get('active_position_day_count', 0)}`",
        f"- mean_active_position_count: `{_fmt(aggregate.get('mean_active_position_count'))}`",
        f"- exposure_time_pct: `{_fmt(aggregate.get('exposure_time_pct'))}`",
        f"- turnover_proxy: `{_fmt(aggregate.get('turnover_proxy'))}`",
        "",
        "## Matrix Coverage",
        "",
        f"- completed_portfolio_matrix: `{aggregate.get('completed_portfolio_matrix')}`",
        f"- price_symbol_count: `{manifest['matrix_audit'].get('price_symbol_count', 0)}`",
        f"- entry_order_count: `{manifest['matrix_audit'].get('entry_order_count', 0)}`",
        f"- exit_order_count: `{manifest['matrix_audit'].get('exit_order_count', 0)}`",
    ]
    if manifest["skip_reason_distribution"]:
        lines.extend(["", "## Skip Reasons", ""])
        for payload in manifest["skip_reason_distribution"]:
            lines.append(f"- `{payload['reason']}`: `{payload['count']}`")
    if manifest["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in manifest["issues"])
    lines.extend(["", "## Non Claims", ""])
    lines.extend(f"- {claim}" for claim in manifest["non_claims"])
    lines.extend(["", f"下一张路线卡：`{manifest['next_route_card']}`", ""])
    return "\n".join(lines)


def closeout_markdown(manifest: dict[str, Any]) -> str:
    aggregate = manifest["aggregate"]
    return "\n".join(
        [
            "# V1 Vectorbt Portfolio Analytics Proof Closeout",
            "",
            f"- run_id: `{manifest['run_id']}`",
            f"- status: `{manifest['status']}`",
            f"- live_next_card: `{manifest['live_next_card']}`",
            f"- next_route_card: `{manifest['next_route_card']}`",
            f"- completed_portfolio_matrix: `{aggregate.get('completed_portfolio_matrix')}`",
            f"- total_trade_count: `{aggregate.get('total_trade_count', 0)}`",
            f"- issue_count: `{manifest['issue_count']}`",
            "- H:/Asteria-data mutation: `no`",
            "",
            "本卡只读消费正式 Signal 与 Data 行情账本，运行 vectorbt 组合矩阵 proof。",
            "它不证明真实成交闭环、账户更新、broker adapter 或实盘交易能力。",
            "",
        ]
    )


def _human_conclusion(manifest: dict[str, Any]) -> str:
    if manifest["status"].startswith("passed"):
        return (
            "本卡已经证明 Asteria Signal 可以被 `vectorbt` 以多资产矩阵方式消费，"
            "并产出组合级收益、回撤、持仓暴露和换手代理读数。"
        )
    return "本卡未能完成 vectorbt 组合矩阵 proof；已按 issue 分类登记，不补库、不打开 live gate。"


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)
