from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from asteria.build_orchestration.batching import SymbolBatch
from asteria.build_orchestration.scope import BuildScope


@dataclass(frozen=True)
class BuildManifest:
    run_id: str
    module_id: str
    mode: str
    db_names: tuple[str, ...]
    scope: BuildScope
    schema_version: str
    rule_versions: dict[str, str]
    source_run_id: str | None
    batches: tuple[SymbolBatch, ...]

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["db_names"] = list(self.db_names)
        payload["scope"] = self.scope.as_dict()
        payload["batches"] = [batch.as_dict() for batch in self.batches]
        return payload


@dataclass(frozen=True)
class BatchLedgerEntry:
    run_id: str
    batch_id: str
    status: str
    started_at: str | None = None
    completed_at: str | None = None
    promoted_at: str | None = None
    row_counts: dict[str, int] | None = None
    audit_summary_path: str | None = None
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def write_manifest(path: Path, manifest: BuildManifest) -> None:
    _write_json(path, manifest.as_dict())


def write_checkpoint(path: Path, payload: dict[str, Any]) -> None:
    _write_json(path, {**payload, "updated_at": utc_now_iso()})


def append_batch_ledger(path: Path, entry: BatchLedgerEntry) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry.as_dict(), ensure_ascii=False, sort_keys=True))
        handle.write("\n")


def completed_batch_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    latest: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        latest[str(payload["batch_id"])] = str(payload["status"])
    return {batch_id for batch_id, status in latest.items() if status == "promoted"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
