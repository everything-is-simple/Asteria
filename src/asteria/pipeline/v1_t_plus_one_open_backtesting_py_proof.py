from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from asteria.pipeline.v1_t_plus_one_open_backtesting_py_proof_contracts import (
    V1_SIGNAL_EXPORT_CONTRACT_RUN_ID,
    V1_T_PLUS_ONE_OPEN_BACKTESTING_PY_PROOF_CARD,
    V1_USAGE_SCOPE_RUN_ID,
    V1_VECTORBT_PORTFOLIO_ANALYTICS_PROOF_CARD,
    TPlusOneOpenBacktestingPyProofRequest,
    TPlusOneOpenBacktestingPyProofSummary,
)
from asteria.pipeline.v1_t_plus_one_open_backtesting_py_proof_io import (
    write_tplus1_backtesting_py_artifacts,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


def run_v1_t_plus_one_open_backtesting_py_proof(
    request: TPlusOneOpenBacktestingPyProofRequest,
) -> TPlusOneOpenBacktestingPyProofSummary:
    live_next_card = _load_terminal_live_next_card(request.repo_root)
    route_issues = _collect_route_issues(request.repo_root)
    scope_manifest, scope_issues = _load_scope_manifest(request.scope_manifest_path)
    selected_symbols = _selected_symbols(scope_manifest)
    start_date, end_date, date_window_issue = _date_window(scope_manifest)
    issues = [*route_issues, *scope_issues]
    if date_window_issue is not None:
        issues.append(date_window_issue)

    dependency_issue = _backtesting_dependency_issue()
    if dependency_issue is not None:
        issues.append(dependency_issue)

    symbol_results: list[dict[str, Any]] = []
    signal_symbol_count = 0
    if not issues:
        symbol_results, signal_symbol_count = _run_symbol_proofs(
            request, selected_symbols, start_date, end_date
        )
        completed_count = sum(1 for result in symbol_results if result["status"] == "completed")
        if completed_count == 0:
            issues.append("no selected symbol completed a backtesting.py proof")
    aggregate = _aggregate(symbol_results)
    skip_reason_distribution = _skip_reason_distribution(symbol_results)
    status = (
        "passed / t+1 open backtesting.py proof completed"
        if not issues
        else "blocked / t+1 open backtesting.py proof gaps found"
    )
    next_route_card = (
        V1_VECTORBT_PORTFOLIO_ANALYTICS_PROOF_CARD
        if not issues
        else V1_T_PLUS_ONE_OPEN_BACKTESTING_PY_PROOF_CARD
    )

    manifest_path, report_path, closeout_path, temp_manifest_path, validated_zip = (
        write_tplus1_backtesting_py_artifacts(
            request=request,
            status=status,
            live_next_card=live_next_card,
            selected_symbols=selected_symbols,
            signal_symbol_count=signal_symbol_count,
            start_date=start_date,
            end_date=end_date,
            symbol_results=symbol_results,
            aggregate=aggregate,
            skip_reason_distribution=skip_reason_distribution,
            issues=issues,
            next_route_card=next_route_card,
        )
    )

    return TPlusOneOpenBacktestingPyProofSummary(
        run_id=request.run_id,
        status=status,
        live_next_card=live_next_card,
        live_next_card_preserved=live_next_card == "none / terminal",
        selected_symbol_count=len(selected_symbols),
        signal_symbol_count=signal_symbol_count,
        completed_backtest_count=int(aggregate["completed_backtest_count"]),
        skipped_symbol_count=int(aggregate["skipped_symbol_count"]),
        total_trade_count=int(aggregate["total_trade_count"]),
        date_window=f"{start_date.isoformat()}..{end_date.isoformat()}",
        issue_count=len(issues),
        issues=issues,
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
        raise ValueError("T+1 open proof requires final release closeout terminal state")
    if str(registry.get("current_allowed_next_card", "")) not in {"", "none"}:
        raise ValueError("T+1 open proof must not reopen live next card")
    return "none / terminal"


def _collect_route_issues(repo_root: Path) -> list[str]:
    roadmap_path = (
        repo_root / "docs" / "03-refactor" / "05-asteria-v1-usage-validation-roadmap-v1.md"
    )
    conclusion_path = repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    roadmap_text = roadmap_path.read_text(encoding="utf-8")
    conclusion_text = conclusion_path.read_text(encoding="utf-8")
    issues: list[str] = []
    route_line_options = {
        "| 3 | `v1-t-plus-one-open-backtesting-py-proof-card` | prepared next route card |",
        (
            "| 3 | `v1-t-plus-one-open-backtesting-py-proof-card` | "
            "passed / t+1 open backtesting.py proof completed |"
        ),
    }
    if not any(route_line in roadmap_text for route_line in route_line_options):
        issues.append("roadmap does not prepare v1-t-plus-one-open-backtesting-py-proof-card")
    if V1_SIGNAL_EXPORT_CONTRACT_RUN_ID not in conclusion_text:
        issues.append("signal export contract predecessor is not registered")
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


def _backtesting_dependency_issue() -> str | None:
    try:
        import backtesting  # noqa: F401
    except ModuleNotFoundError:
        return "backtesting.py dependency is not installed"
    return None


def _run_symbol_proofs(
    request: TPlusOneOpenBacktestingPyProofRequest,
    selected_symbols: list[str],
    start_date: date,
    end_date: date,
) -> tuple[list[dict[str, Any]], int]:
    signals = _load_signals(
        request.formal_data_root / "signal.duckdb", selected_symbols, start_date, end_date
    )
    signal_symbol_count = len(signals)
    results: list[dict[str, Any]] = []
    for symbol in selected_symbols:
        symbol_signals = signals.get(symbol, {})
        if not symbol_signals:
            results.append(_skipped_symbol(symbol, "no_active_signal_in_scope"))
            continue
        bars = _load_bars(
            request.formal_data_root / "market_base_day.duckdb", symbol, start_date, end_date
        )
        if len(bars) < 2:
            results.append(_skipped_symbol(symbol, "insufficient_execution_price_bars"))
            continue
        results.append(_run_backtest_for_symbol(request, symbol, bars, symbol_signals))
    return results, signal_symbol_count


def _load_signals(
    signal_db: Path,
    selected_symbols: list[str],
    start_date: date,
    end_date: date,
) -> dict[str, dict[pd.Timestamp, dict[str, Any]]]:
    if not signal_db.exists():
        return {}
    placeholders = ", ".join("?" for _ in selected_symbols)
    query = f"""
        select signal_id, symbol, signal_dt, signal_type, signal_bias, signal_strength,
               run_id, schema_version, signal_rule_version, source_alpha_release_version
        from formal_signal_ledger
        where timeframe = 'day'
          and signal_state = 'active'
          and symbol in ({placeholders})
          and signal_dt between ? and ?
        order by symbol, signal_dt, signal_id
    """
    params: list[Any] = [*selected_symbols, start_date, end_date]
    with duckdb.connect(str(signal_db), read_only=True) as con:
        rows = con.execute(query, params).fetchall()
    grouped: dict[str, dict[pd.Timestamp, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in rows:
        signal_dt = pd.Timestamp(row[2])
        grouped[str(row[1])][signal_dt].append(
            {
                "signal_id": row[0],
                "signal_type": row[3],
                "signal_bias": row[4],
                "signal_strength": float(row[5] or 0.0),
                "source_run_id": row[6],
                "schema_version": row[7],
                "signal_rule_version": row[8],
                "source_alpha_release_version": row[9],
            }
        )
    return {
        symbol: {
            signal_dt: _collapse_daily_signals(payloads) for signal_dt, payloads in by_date.items()
        }
        for symbol, by_date in grouped.items()
    }


def _collapse_daily_signals(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    signed_strength = 0.0
    for payload in payloads:
        direction = _bias_direction(str(payload["signal_bias"]))
        signed_strength += direction * abs(float(payload["signal_strength"]))
    direction = 1 if signed_strength > 0 else -1 if signed_strength < 0 else 0
    return {
        "direction": direction,
        "signal_count": len(payloads),
        "signal_ids": [payload["signal_id"] for payload in payloads],
        "signal_types": sorted({str(payload["signal_type"]) for payload in payloads}),
        "signal_family": sorted({str(payload["signal_type"]) for payload in payloads})[0],
        "source_run_ids": sorted({str(payload["source_run_id"]) for payload in payloads}),
        "signed_strength": signed_strength,
    }


def _bias_direction(signal_bias: str) -> int:
    if signal_bias == "up_opportunity":
        return 1
    if signal_bias == "down_opportunity":
        return -1
    return 0


def _load_bars(
    market_base_day_db: Path,
    symbol: str,
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    if not market_base_day_db.exists():
        return pd.DataFrame()
    with duckdb.connect(str(market_base_day_db), read_only=True) as con:
        rows = con.execute(
            """
            select trade_date, open_px, high_px, low_px, close_px, volume
            from market_base_bar
            where symbol = ?
              and timeframe = 'day'
              and price_line = 'execution_price_line'
              and adj_mode = 'none'
              and trade_date <= ?
              and (
                  trade_date >= ?
                  or trade_date = (
                      select max(trade_date)
                      from market_base_bar
                      where symbol = ?
                        and timeframe = 'day'
                        and price_line = 'execution_price_line'
                        and adj_mode = 'none'
                        and trade_date < ?
                  )
              )
            order by trade_date
            """,
            [symbol, end_date, start_date, symbol, start_date],
        ).fetchall()
    if not rows:
        return pd.DataFrame()
    frame = pd.DataFrame(rows, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    frame["Date"] = pd.to_datetime(frame["Date"])
    return frame.set_index("Date")


def _run_backtest_for_symbol(
    request: TPlusOneOpenBacktestingPyProofRequest,
    symbol: str,
    bars: pd.DataFrame,
    signals: dict[pd.Timestamp, dict[str, Any]],
) -> dict[str, Any]:
    from backtesting import Backtest, Strategy

    signal_map = {pd.Timestamp(key): int(value["direction"]) for key, value in signals.items()}

    class AsteriaTPlusOneOpenStrategy(Strategy):
        def init(self) -> None:
            return None

        def next(self) -> None:
            signal_date = pd.Timestamp(self.data.index[-1])
            direction = signal_map.get(signal_date, 0)
            if direction > 0 and not self.position:
                self.buy(size=request.position_fraction)
            elif direction < 0 and self.position:
                self.position.close()

    backtest = Backtest(
        bars,
        AsteriaTPlusOneOpenStrategy,
        cash=request.initial_cash,
        commission=request.commission,
        trade_on_close=False,
        exclusive_orders=True,
        finalize_trades=True,
    )
    stats = backtest.run()
    skip_audit = _audit_signal_skips(bars, signals)
    return {
        "symbol": symbol,
        "status": "completed",
        "return_pct": _series_float(stats, "Return [%]"),
        "max_drawdown_pct": _series_float(stats, "Max. Drawdown [%]"),
        "trade_count": int(stats.get("# Trades", 0)),
        "buy_and_hold_return_pct": _series_float(stats, "Buy & Hold Return [%]"),
        "equity_final": _series_float(stats, "Equity Final [$]"),
        "signal_count": len(signals),
        "t_plus_one_audit": skip_audit,
        "skip_reason": None,
    }


def _audit_signal_skips(
    bars: pd.DataFrame,
    signals: dict[pd.Timestamp, dict[str, Any]],
) -> dict[str, int]:
    bar_dates = list(bars.index)
    next_bar_by_date = {
        pd.Timestamp(current): pd.Timestamp(next_bar)
        for current, next_bar in zip(bar_dates, bar_dates[1:], strict=False)
    }
    counts: Counter[str] = Counter()
    has_position = False
    for signal_date in sorted(signals):
        direction = int(signals[signal_date]["direction"])
        if signal_date not in next_bar_by_date:
            counts["no_t_plus_one_open_bar"] += 1
        elif direction > 0 and has_position:
            counts["up_signal_already_in_position"] += 1
        elif direction > 0:
            has_position = True
            counts["up_signal_ordered_for_t_plus_one_open"] += 1
        elif direction < 0 and has_position:
            has_position = False
            counts["down_signal_close_ordered_for_t_plus_one_open"] += 1
        elif direction < 0:
            counts["down_signal_without_open_position"] += 1
        else:
            counts["neutral_signal_skipped"] += 1
    return dict(counts)


def _series_float(stats: Any, key: str) -> float | None:
    value = stats.get(key)
    if value is None or pd.isna(value):
        return None
    return float(value)


def _skipped_symbol(symbol: str, reason: str) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "status": "skipped",
        "return_pct": None,
        "max_drawdown_pct": None,
        "trade_count": 0,
        "buy_and_hold_return_pct": None,
        "equity_final": None,
        "signal_count": 0,
        "t_plus_one_audit": {},
        "skip_reason": reason,
    }


def _aggregate(symbol_results: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [result for result in symbol_results if result["status"] == "completed"]
    returns = [
        float(result["return_pct"]) for result in completed if result["return_pct"] is not None
    ]
    drawdowns = [
        float(result["max_drawdown_pct"])
        for result in completed
        if result["max_drawdown_pct"] is not None
    ]
    return {
        "completed_backtest_count": len(completed),
        "skipped_symbol_count": len(symbol_results) - len(completed),
        "total_trade_count": sum(int(result.get("trade_count", 0)) for result in completed),
        "mean_return_pct": float(pd.Series(returns).mean()) if returns else None,
        "median_return_pct": float(pd.Series(returns).median()) if returns else None,
        "worst_drawdown_pct": min(drawdowns) if drawdowns else None,
    }


def _skip_reason_distribution(symbol_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for result in symbol_results:
        if result.get("skip_reason"):
            counter[str(result["skip_reason"])] += 1
        for reason, count in result.get("t_plus_one_audit", {}).items():
            if reason.endswith("skipped") or "without" in reason or "no_t_plus_one" in reason:
                counter[reason] += int(count)
    return [
        {"reason": reason, "count": count}
        for reason, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]
