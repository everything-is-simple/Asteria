from __future__ import annotations

import hashlib
import re
from datetime import date, datetime, timezone
from pathlib import Path

from asteria.data.contracts import ParsedTdxFile, RawMarketBar, TdxSourceFile

_ADJ_FOLDER_BY_MODE = {
    "backward": "Backward-Adjusted",
    "forward": "Forward-Adjusted",
    "none": "Non-Adjusted",
}
_MODE_BY_ADJ_FOLDER = {value: key for key, value in _ADJ_FOLDER_BY_MODE.items()}


def discover_tdx_text_files(
    source_root: Path,
    *,
    asset_type: str,
    adj_mode: str,
    symbol_limit: int | None = None,
) -> tuple[TdxSourceFile, ...]:
    modes = tuple(_ADJ_FOLDER_BY_MODE) if adj_mode == "all" else (adj_mode,)
    discovered: list[TdxSourceFile] = []
    for mode in modes:
        folder = Path(source_root) / f"{asset_type}-day" / _ADJ_FOLDER_BY_MODE[mode]
        mode_paths = sorted(folder.glob("*.txt"))
        if symbol_limit is not None:
            mode_paths = mode_paths[:symbol_limit]
        for source_path in mode_paths:
            discovered.append(_source_file_from_path(source_path, asset_type=asset_type))
    return tuple(discovered)


def parse_tdx_text_file(source: TdxSourceFile) -> ParsedTdxFile:
    text = source.source_path.read_text(encoding="gbk")
    lines = text.splitlines()
    if len(lines) < 2:
        raise ValueError(f"Unexpected TDX text format: {source.source_path}")

    header = lines[0].strip()
    header_parts = header.split()
    name = header_parts[1] if len(header_parts) > 1 else source.symbol
    bars: list[RawMarketBar] = []
    for line in lines[1:]:
        parts = [part for part in re.split(r"\s+", line.strip()) if part]
        if len(parts) < 7 or not _looks_like_date(parts[0]):
            continue
        trade_date = _parse_date(parts[0])
        bars.append(
            RawMarketBar(
                symbol=source.symbol,
                asset_type=source.asset_type,
                timeframe="day",
                bar_dt=trade_date,
                trade_date=trade_date,
                adj_mode=source.adj_mode,
                open_px=_parse_float(parts[1]),
                high_px=_parse_float(parts[2]),
                low_px=_parse_float(parts[3]),
                close_px=_parse_float(parts[4]),
                volume=_parse_float(parts[5]),
                amount=_parse_float(parts[6]),
            )
        )
    return ParsedTdxFile(source=source, name=name, header=header, bars=tuple(bars))


def _source_file_from_path(path: Path, *, asset_type: str) -> TdxSourceFile:
    stat = path.stat()
    return TdxSourceFile(
        asset_type=asset_type,
        adj_mode=_MODE_BY_ADJ_FOLDER[path.parent.name],
        symbol=_normalize_symbol(path),
        source_path=path,
        source_size_bytes=stat.st_size,
        source_mtime=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
        source_content_hash=hashlib.sha256(path.read_bytes()).hexdigest(),
    )


def _normalize_symbol(path: Path) -> str:
    if "#" not in path.stem:
        raise ValueError(f"Unexpected TDX source name: {path.name}")
    exchange, code = path.stem.split("#", 1)
    return f"{code}.{exchange.upper()}"


def _looks_like_date(value: str) -> bool:
    parts = re.split(r"[-/]", value)
    return len(parts) == 3 and all(part.isdigit() for part in parts)


def _parse_date(value: str) -> date:
    normalized = value.replace("/", "-")
    first, second, third = normalized.split("-")
    if len(first) == 4:
        return date.fromisoformat(normalized)
    return date(int(third), int(second), int(first))


def _parse_float(value: str) -> float | None:
    candidate = value.strip().replace(",", "")
    return None if candidate == "" else float(candidate)
