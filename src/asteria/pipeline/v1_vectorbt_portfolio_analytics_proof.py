from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from asteria.pipeline.v1_vectorbt_portfolio_analytics_proof_contracts import (
    V1_BROKER_ADAPTER_FEASIBILITY_CARD,
    V1_T_PLUS_ONE_OPEN_BACKTESTING_PY_PROOF_RUN_ID,
    V1_USAGE_SCOPE_RUN_ID,
    V1_VECTORBT_PORTFOLIO_ANALYTICS_PROOF_CARD,
    VectorbtPortfolioAnalyticsProofRequest,
    VectorbtPortfolioAnalyticsProofSummary,
)
from asteria.pipeline.v1_vectorbt_portfolio_analytics_proof_io import (
    write_vectorbt_portfolio_analytics_artifacts,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


def run_v1_vectorbt_portfolio_analytics_proof(
    request: VectorbtPortfolioAnalyticsProofRequest,
) -> VectorbtPortfolioAnalyticsProofSummary:
    live_next_card = _load_terminal_live_next_card(request.repo_root)
    route_issues = _collect_route_issues(request.repo_root)
    scope_manifest, scope_issues = _load_scope_manifest(request.scope_manifest_path)
    selected_symbols = _selected_symbols(scope_manifest)
    start_date, end_date, date_window_issue = _date_window(scope_manifest)
    issues = [*route_issues, *scope_issues]
    if date_window_issue is not None:
        issues.append(date_window_issue)

    dependency_issue = _vectorbt_dependency_issue()
    if dependency_issue is not None:
        issues.append(dependency_issue)

    signal_symbol_count = 0
    aggregate = _empty_aggregate()
    matrix_audit: dict[str, Any] = {}
    skip_reason_distribution: list[dict[str, Any]] = []
    if not issues:
        signals = _load_signals(
            request.formal_data_root / "signal.duckdb", selected_symbols, start_date, end_date
        )
        signal_symbol_count = len(signals)
        if signal_symbol_count == 0:
            issues.append("no active signal available for vectorbt portfolio matrix")
        else:
            bars = _load_price_bars(
                request.formal_data_root / "market_base_day.duckdb",
                selected_symbols,
                start_date,
                end_date,
            )
            proof = _run_vectorbt_matrix(request, selected_symbols, signals, bars)
            aggregate = proof["aggregate"]
            matrix_audit = proof["matrix_audit"]
            skip_reason_distribution = proof["skip_reason_distribution"]
            if not aggregate["completed_portfolio_matrix"]:
                issues.append("vectorbt portfolio matrix did not complete")

    status = (
        "passed / vectorbt portfolio analytics proof completed"
        if not issues
        else "blocked / vectorbt portfolio analytics proof gaps found"
    )
    next_route_card = (
        V1_BROKER_ADAPTER_FEASIBILITY_CARD
        if not issues
        else V1_VECTORBT_PORTFOLIO_ANALYTICS_PROOF_CARD
    )
    manifest_path, report_path, closeout_path, temp_manifest_path, validated_zip = (
        write_vectorbt_portfolio_analytics_artifacts(
            request=request,
            status=status,
            live_next_card=live_next_card,
            selected_symbols=selected_symbols,
            signal_symbol_count=signal_symbol_count,
            start_date=start_date,
            end_date=end_date,
            aggregate=aggregate,
            matrix_audit=matrix_audit,
            skip_reason_distribution=skip_reason_distribution,
            issues=issues,
            next_route_card=next_route_card,
        )
    )

    return VectorbtPortfolioAnalyticsProofSummary(
        run_id=request.run_id,
        status=status,
        live_next_card=live_next_card,
        live_next_card_preserved=live_next_card == "none / terminal",
        selected_symbol_count=len(selected_symbols),
        signal_symbol_count=signal_symbol_count,
        completed_portfolio_matrix=bool(aggregate["completed_portfolio_matrix"]),
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
        raise ValueError("vectorbt proof requires final release closeout terminal state")
    if str(registry.get("current_allowed_next_card", "")) not in {"", "none"}:
        raise ValueError("vectorbt proof must not reopen live next card")
    return "none / terminal"


def _collect_route_issues(repo_root: Path) -> list[str]:
    roadmap_path = (
        repo_root / "docs" / "03-refactor" / "05-asteria-v1-usage-validation-roadmap-v1.md"
    )
    conclusion_path = repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    roadmap_text = roadmap_path.read_text(encoding="utf-8")
    conclusion_text = conclusion_path.read_text(encoding="utf-8")
    issues: list[str] = []
    if (
        "| 4 | `v1-vectorbt-portfolio-analytics-proof-card` | prepared next route card |"
        not in roadmap_text
        and (
            "| 4 | `v1-vectorbt-portfolio-analytics-proof-card` | "
            "passed / vectorbt portfolio analytics proof completed |"
        )
        not in roadmap_text
    ):
        issues.append("roadmap does not prepare v1-vectorbt-portfolio-analytics-proof-card")
    if V1_T_PLUS_ONE_OPEN_BACKTESTING_PY_PROOF_RUN_ID not in conclusion_text:
        issues.append("T+1 open backtesting.py predecessor is not registered")
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


def _vectorbt_dependency_issue() -> str | None:
    try:
        import vectorbt  # noqa: F401
    except ModuleNotFoundError:
        return "vectorbt dependency is not installed"
    return None


def _load_signals(
    signal_db: Path,
    selected_symbols: list[str],
    start_date: date,
    end_date: date,
) -> dict[str, dict[pd.Timestamp, dict[str, Any]]]:
    if not signal_db.exists() or not selected_symbols:
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
        grouped[str(row[1])][pd.Timestamp(row[2])].append(
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
        signed_strength += _bias_direction(str(payload["signal_bias"])) * abs(
            float(payload["signal_strength"])
        )
    direction = 1 if signed_strength > 0 else -1 if signed_strength < 0 else 0
    return {
        "direction": direction,
        "signal_count": len(payloads),
        "signal_ids": [payload["signal_id"] for payload in payloads],
        "signal_types": sorted({str(payload["signal_type"]) for payload in payloads}),
        "source_run_ids": sorted({str(payload["source_run_id"]) for payload in payloads}),
        "signed_strength": signed_strength,
    }


def _bias_direction(signal_bias: str) -> int:
    if signal_bias == "up_opportunity":
        return 1
    if signal_bias == "down_opportunity":
        return -1
    return 0


def _load_price_bars(
    market_base_day_db: Path,
    selected_symbols: list[str],
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    if not market_base_day_db.exists() or not selected_symbols:
        return pd.DataFrame()
    placeholders = ", ".join("?" for _ in selected_symbols)
    query = f"""
        select symbol, trade_date, open_px, close_px
        from market_base_bar
        where timeframe = 'day'
          and price_line = 'execution_price_line'
          and adj_mode = 'none'
          and symbol in ({placeholders})
          and trade_date between ? and ?
        order by symbol, trade_date
    """
    params: list[Any] = [*selected_symbols, start_date, end_date]
    with duckdb.connect(str(market_base_day_db), read_only=True) as con:
        rows = con.execute(query, params).fetchall()
    if not rows:
        return pd.DataFrame()
    frame = pd.DataFrame(rows, columns=["symbol", "trade_date", "open", "close"])
    frame["trade_date"] = pd.to_datetime(frame["trade_date"])
    return frame


def _run_vectorbt_matrix(
    request: VectorbtPortfolioAnalyticsProofRequest,
    selected_symbols: list[str],
    signals: dict[str, dict[pd.Timestamp, dict[str, Any]]],
    bars: pd.DataFrame,
) -> dict[str, Any]:
    import vectorbt as vbt

    if bars.empty:
        return _blocked_matrix("no_execution_price_bars")
    close_df = _pivot_price(bars, "close", selected_symbols)
    open_df = _pivot_price(bars, "open", selected_symbols)
    entries, exits, matrix_audit, skip_counter = _build_execution_matrices(
        selected_symbols, close_df.index, signals
    )
    if not bool(entries.to_numpy().any() or exits.to_numpy().any()):
        return _blocked_matrix("no_t_plus_one_orders")

    group_by = pd.Index(["asteria_sample"] * len(close_df.columns), name="portfolio")
    portfolio = vbt.Portfolio.from_signals(
        close_df,
        entries,
        exits,
        price=open_df,
        init_cash=request.initial_cash,
        fees=request.fees,
        direction="longonly",
        cash_sharing=True,
        group_by=group_by,
        freq="1D",
    )
    aggregate = _portfolio_aggregate(portfolio, entries, exits, request.initial_cash)
    matrix_audit.update(
        {
            "price_symbol_count": len(close_df.columns),
            "price_row_count": len(close_df),
            "entry_order_count": int(entries.sum().sum()),
            "exit_order_count": int(exits.sum().sum()),
        }
    )
    skip_counter.update(_no_signal_skip_counts(selected_symbols, signals))
    return {
        "aggregate": aggregate,
        "matrix_audit": matrix_audit,
        "skip_reason_distribution": _skip_reason_distribution(skip_counter),
    }


def _pivot_price(bars: pd.DataFrame, column: str, selected_symbols: list[str]) -> pd.DataFrame:
    frame = bars.pivot(index="trade_date", columns="symbol", values=column).sort_index()
    return frame.reindex(columns=selected_symbols).dropna(axis=1, how="all")


def _build_execution_matrices(
    selected_symbols: list[str],
    trade_dates: pd.Index,
    signals: dict[str, dict[pd.Timestamp, dict[str, Any]]],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any], Counter[str]]:
    entries = pd.DataFrame(False, index=trade_dates, columns=selected_symbols)
    exits = pd.DataFrame(False, index=trade_dates, columns=selected_symbols)
    skip_counter: Counter[str] = Counter()
    execution_dates: dict[str, dict[str, str]] = {}
    trade_date_list = [pd.Timestamp(value) for value in trade_dates]
    next_date_by_date = {
        pd.Timestamp(current): pd.Timestamp(next_date)
        for current, next_date in zip(trade_date_list, trade_date_list[1:], strict=False)
    }
    for symbol in selected_symbols:
        symbol_mapping: dict[str, str] = {}
        for signal_date, payload in sorted(signals.get(symbol, {}).items()):
            signal_ts = pd.Timestamp(signal_date)
            execution_date = next_date_by_date.get(signal_ts)
            if execution_date is None:
                skip_counter["no_t_plus_one_open_bar"] += 1
                continue
            direction = int(payload["direction"])
            if direction > 0:
                entries.loc[execution_date, symbol] = True
                symbol_mapping[signal_ts.date().isoformat()] = execution_date.date().isoformat()
            elif direction < 0:
                exits.loc[execution_date, symbol] = True
                symbol_mapping[signal_ts.date().isoformat()] = execution_date.date().isoformat()
            else:
                skip_counter["neutral_signal_skipped"] += 1
        if symbol_mapping:
            execution_dates[symbol] = symbol_mapping
    return (
        entries,
        exits,
        {"execution_dates_by_signal_date": execution_dates},
        skip_counter,
    )


def _portfolio_aggregate(
    portfolio: Any,
    entries: pd.DataFrame,
    exits: pd.DataFrame,
    initial_cash: float,
) -> dict[str, Any]:
    active = _active_position_matrix(entries, exits)
    order_activity_count = _metric_int(portfolio.orders.count())
    total_trade_count = _metric_int(portfolio.trades.count())
    total_order_value = _orders_value_sum(portfolio)
    value_mean = _metric_float(portfolio.value().mean())
    turnover_base = value_mean if value_mean and value_mean > 0 else initial_cash
    return {
        "completed_portfolio_matrix": True,
        "portfolio_total_return_pct": _metric_float(portfolio.total_return()) * 100.0,
        "portfolio_max_drawdown_pct": _metric_float(portfolio.max_drawdown()) * 100.0,
        "total_trade_count": total_trade_count,
        "order_activity_count": order_activity_count,
        "total_order_value": total_order_value,
        "turnover_proxy": total_order_value / turnover_base if turnover_base else None,
        "active_position_day_count": int((active.sum(axis=1) > 0).sum()),
        "mean_active_position_count": float(active.sum(axis=1).mean()),
        "exposure_time_pct": float(active.to_numpy().mean() * 100.0),
    }


def _active_position_matrix(entries: pd.DataFrame, exits: pd.DataFrame) -> pd.DataFrame:
    active = pd.DataFrame(False, index=entries.index, columns=entries.columns)
    for symbol in entries.columns:
        in_position = False
        for trade_date in entries.index:
            if bool(entries.loc[trade_date, symbol]):
                in_position = True
            if bool(exits.loc[trade_date, symbol]):
                in_position = False
            active.loc[trade_date, symbol] = in_position
    return active


def _orders_value_sum(portfolio: Any) -> float:
    records = portfolio.orders.records_readable
    if hasattr(records, "empty") and records.empty:
        return 0.0
    if "Size" in records and "Price" in records:
        return float((records["Size"].abs() * records["Price"]).sum())
    raw = portfolio.orders.records
    if getattr(raw, "size", 0) == 0:
        return 0.0
    return float((pd.Series(raw["size"]).abs() * pd.Series(raw["price"])).sum())


def _metric_float(value: Any) -> float:
    if isinstance(value, pd.Series):
        return float(value.iloc[0])
    return float(value)


def _metric_int(value: Any) -> int:
    if isinstance(value, pd.Series):
        return int(value.iloc[0])
    return int(value)


def _blocked_matrix(reason: str) -> dict[str, Any]:
    return {
        "aggregate": _empty_aggregate(),
        "matrix_audit": {},
        "skip_reason_distribution": [{"reason": reason, "count": 1}],
    }


def _empty_aggregate() -> dict[str, Any]:
    return {
        "completed_portfolio_matrix": False,
        "portfolio_total_return_pct": None,
        "portfolio_max_drawdown_pct": None,
        "total_trade_count": 0,
        "order_activity_count": 0,
        "total_order_value": 0.0,
        "turnover_proxy": None,
        "active_position_day_count": 0,
        "mean_active_position_count": 0.0,
        "exposure_time_pct": 0.0,
    }


def _no_signal_skip_counts(
    selected_symbols: list[str],
    signals: dict[str, dict[pd.Timestamp, dict[str, Any]]],
) -> Counter[str]:
    counter: Counter[str] = Counter()
    for symbol in selected_symbols:
        if not signals.get(symbol):
            counter["no_active_signal_in_scope"] += 1
    return counter


def _skip_reason_distribution(counter: Counter[str]) -> list[dict[str, Any]]:
    return [
        {"reason": reason, "count": count}
        for reason, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]
