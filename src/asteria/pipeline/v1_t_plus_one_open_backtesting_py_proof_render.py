from __future__ import annotations

from typing import Any

from asteria.pipeline.v1_t_plus_one_open_backtesting_py_proof_contracts import (
    V1_T_PLUS_ONE_OPEN_BACKTESTING_PY_PROOF_CARD,
    TPlusOneOpenBacktestingPyProofRequest,
)


def manifest_payload(
    request: TPlusOneOpenBacktestingPyProofRequest,
    *,
    status: str,
    live_next_card: str,
    selected_symbols: list[str],
    signal_symbol_count: int,
    date_window: dict[str, str],
    symbol_results: list[dict[str, Any]],
    aggregate: dict[str, Any],
    skip_reason_distribution: list[dict[str, Any]],
    issues: list[str],
    next_route_card: str,
) -> dict[str, Any]:
    return {
        "run_id": request.run_id,
        "card_id": V1_T_PLUS_ONE_OPEN_BACKTESTING_PY_PROOF_CARD,
        "module": "pipeline",
        "stage": "v1_t_plus_one_open_backtesting_py_proof",
        "status": status,
        "route_type": "roadmap_only_read_only_post_terminal_backtesting_py_proof",
        "live_next_card": live_next_card,
        "live_next_card_preserved": live_next_card == "none / terminal",
        "formal_db_mutation": "no",
        "formal_data_root": str(request.formal_data_root),
        "source_scope_manifest": str(request.scope_manifest_path),
        "selected_symbol_count": len(selected_symbols),
        "selected_symbols": selected_symbols,
        "signal_symbol_count": signal_symbol_count,
        "date_window": date_window,
        "execution_semantics": {
            "signal_timing": "T+0 signal",
            "execution_hint": "T_PLUS_1_OPEN",
            "trade_date_policy": "next_trading_day_after_signal_date",
            "price_field": "open",
            "engine": "backtesting.py",
            "engine_trade_on_close": False,
            "engine_finalize_trades": True,
            "positioning": "long_only_single_symbol",
        },
        "parameters": {
            "initial_cash": request.initial_cash,
            "commission": request.commission,
            "position_fraction": request.position_fraction,
        },
        "aggregate": aggregate,
        "symbol_results": symbol_results,
        "skip_reason_distribution": skip_reason_distribution,
        "issue_count": len(issues),
        "issues": issues,
        "non_claims": [
            "not a portfolio-level production backtest",
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
        "# Asteria v1 T+1 Open Backtesting.py Proof",
        "",
        f"- run_id: `{manifest['run_id']}`",
        f"- status: `{manifest['status']}`",
        f"- live_next_card: `{manifest['live_next_card']}`",
        f"- formal_db_mutation: `{manifest['formal_db_mutation']}`",
        (f"- date_window: `{manifest['date_window']['start']}..{manifest['date_window']['end']}`"),
        f"- selected_symbol_count: `{manifest['selected_symbol_count']}`",
        f"- completed_backtest_count: `{aggregate['completed_backtest_count']}`",
        f"- total_trade_count: `{aggregate['total_trade_count']}`",
        "",
        "## 人话结论",
        "",
        _human_conclusion(manifest),
        "",
        "## 执行语义",
        "",
        "- `T+0 signal -> T+1 open execution`",
        "- `backtesting.py` uses `trade_on_close=False`, so orders placed on the signal bar "
        "execute on the next bar open.",
        "- 本 proof 是逐股 long-only 研究验证，不是组合层生产回测。",
        "",
        "## Aggregate",
        "",
        f"- mean_return_pct: `{_fmt(aggregate.get('mean_return_pct'))}`",
        f"- median_return_pct: `{_fmt(aggregate.get('median_return_pct'))}`",
        f"- worst_drawdown_pct: `{_fmt(aggregate.get('worst_drawdown_pct'))}`",
        f"- total_trade_count: `{aggregate['total_trade_count']}`",
        f"- completed_backtest_count: `{aggregate['completed_backtest_count']}`",
        f"- skipped_symbol_count: `{aggregate['skipped_symbol_count']}`",
        "",
        "## Per Symbol Results",
        "",
        "| symbol | status | return_pct | max_drawdown_pct | trades | skip_reason |",
        "|---|---|---:|---:|---:|---|",
    ]
    for result in manifest["symbol_results"]:
        lines.append(
            "| {symbol} | {status} | {return_pct} | {drawdown} | {trades} | {skip} |".format(
                symbol=result["symbol"],
                status=result["status"],
                return_pct=_fmt(result.get("return_pct")),
                drawdown=_fmt(result.get("max_drawdown_pct")),
                trades=result.get("trade_count", 0),
                skip=result.get("skip_reason") or "",
            )
        )
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
            "# V1 T+1 Open Backtesting.py Proof Closeout",
            "",
            f"- run_id: `{manifest['run_id']}`",
            f"- status: `{manifest['status']}`",
            f"- live_next_card: `{manifest['live_next_card']}`",
            f"- next_route_card: `{manifest['next_route_card']}`",
            f"- completed_backtest_count: `{aggregate['completed_backtest_count']}`",
            f"- total_trade_count: `{aggregate['total_trade_count']}`",
            f"- issue_count: `{manifest['issue_count']}`",
            "- H:/Asteria-data mutation: `no`",
            "",
            "本卡只读消费正式 Signal 与 Data 行情账本，运行逐股 T+1 open proof。",
            "它不证明真实成交闭环、账户更新、broker adapter 或实盘交易能力。",
            "",
        ]
    )


def _human_conclusion(manifest: dict[str, Any]) -> str:
    if manifest["status"].startswith("passed"):
        return (
            "本卡已经证明 Asteria Signal 可以被外部 `backtesting.py` 以 T+1 open "
            "语义消费，并产出基础 PnL / drawdown / trade count 读数。"
        )
    return "本卡未能完成 T+1 open proof；已按 issue 分类登记，不补库、不打开 live gate。"


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)
