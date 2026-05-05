from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class SymbolBatch:
    batch_id: str
    symbols: tuple[str, ...]
    batch_index: int
    batch_count: int

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["symbols"] = list(self.symbols)
        return payload


def load_symbols_file(path: Path) -> tuple[str, ...]:
    symbols = _dedupe_stable(line.strip() for line in path.read_text(encoding="utf-8").splitlines())
    if not symbols:
        raise ValueError("symbols file must contain at least one symbol")
    return symbols


def build_symbol_batches(
    universe: tuple[str, ...],
    *,
    batch_size: int = 100,
    symbols: tuple[str, ...] | None = None,
    symbols_file: Path | None = None,
    symbol_start: str | None = None,
    symbol_end: str | None = None,
) -> tuple[SymbolBatch, ...]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    selected = tuple(sorted(_dedupe_stable(symbols or universe)))
    if symbols_file is not None:
        selected = tuple(sorted(load_symbols_file(symbols_file)))
    if symbol_start is not None:
        selected = tuple(symbol for symbol in selected if symbol >= symbol_start)
    if symbol_end is not None:
        selected = tuple(symbol for symbol in selected if symbol <= symbol_end)
    if not selected:
        raise ValueError("symbol scope resolved to zero symbols")

    raw_batches = [
        selected[index : index + batch_size] for index in range(0, len(selected), batch_size)
    ]
    batch_count = len(raw_batches)
    return tuple(
        SymbolBatch(
            batch_id=f"batch-{index + 1:04d}",
            symbols=tuple(batch),
            batch_index=index + 1,
            batch_count=batch_count,
        )
        for index, batch in enumerate(raw_batches)
    )


def _dedupe_stable(symbols: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    output: list[str] = []
    for raw in symbols:
        symbol = str(raw).strip()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        output.append(symbol)
    return tuple(output)
