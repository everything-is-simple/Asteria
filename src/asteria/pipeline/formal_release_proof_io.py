from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import duckdb

SOURCE_PROOF_MANIFEST = "formal-release-proof-manifest.json"


def build_db_manifest(root: Path) -> dict[str, Any]:
    databases: dict[str, Any] = {}
    for db_path in sorted(root.glob("*.duckdb")):
        inspection = _inspect_duckdb(db_path)
        databases[db_path.name] = {
            "path": str(db_path),
            "sha256": sha256(db_path),
            **inspection,
        }
    return {
        "root": str(root),
        "databases": databases,
    }


def backup_formal_dbs(request: Any) -> dict[str, Any]:
    request.backup_root.mkdir(parents=True, exist_ok=True)
    copied = _copy_duckdbs(request.formal_data_root, request.backup_root)
    manifest = {
        "status": "completed",
        "source_root": str(request.formal_data_root),
        "backup_root": str(request.backup_root),
        "databases": copied,
    }
    write_json(request.backup_manifest_path, manifest)
    return manifest


def stage_formal_dbs(request: Any, source_db_root: Path) -> dict[str, Any]:
    if request.staging_root.exists():
        shutil.rmtree(request.staging_root)
    request.staging_root.mkdir(parents=True, exist_ok=True)
    copied = _copy_duckdbs(source_db_root, request.staging_root)
    manifest = {
        "status": "passed",
        "source_db_root": str(source_db_root),
        "staging_root": str(request.staging_root),
        "databases": copied,
    }
    write_json(request.staging_manifest_path, manifest)
    return manifest


def promote_staging_dbs(request: Any) -> dict[str, Any]:
    request.formal_data_root.mkdir(parents=True, exist_ok=True)
    copied = _copy_duckdbs(request.staging_root, request.formal_data_root)
    manifest = {
        "status": "promoted",
        "staging_root": str(request.staging_root),
        "formal_data_root": str(request.formal_data_root),
        "databases": copied,
        "promote_attempt_count": 1,
    }
    write_json(request.promote_manifest_path, manifest)
    return manifest


def load_source_proof_manifest(source_root: Path) -> dict[str, Any]:
    path = source_root / SOURCE_PROOF_MANIFEST
    if not path.exists():
        return {}
    return read_json(path)


def source_manifest_passes(manifest: dict[str, Any]) -> bool:
    return (
        manifest.get("proof_scope") == "formal_release"
        and manifest.get("sample_proof") is False
        and manifest.get("full_rebuild_proof") == "passed"
        and manifest.get("daily_incremental_release_proof") == "passed"
        and manifest.get("resume_idempotence_proof") == "passed"
        and bool(manifest.get("source_db_root"))
    )


def source_db_root(source_root: Path, manifest: dict[str, Any]) -> Path:
    raw_path = Path(str(manifest["source_db_root"]))
    return raw_path if raw_path.is_absolute() else source_root / raw_path


def write_skipped_staging_and_promote(request: Any, reason: str) -> None:
    write_json(request.staging_manifest_path, {"status": "skipped", "reason": reason})
    write_promote_skipped(request, reason)


def write_staging_failed(request: Any, source_db_root: Path) -> None:
    write_json(
        request.staging_manifest_path,
        {
            "status": "blocked",
            "reason": "source formal DB root missing or empty",
            "source_db_root": str(source_db_root),
        },
    )


def write_promote_skipped(request: Any, reason: str) -> None:
    write_json(
        request.promote_manifest_path,
        {
            "status": "skipped",
            "reason": reason,
            "promote_attempt_count": 0,
        },
    )


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def sha256(path: Path) -> str:
    if not path.exists():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inspect_duckdb(path: Path) -> dict[str, Any]:
    row_counts: dict[str, int] = {}
    schema_versions: dict[str, list[str]] = {}
    rule_versions: dict[str, list[str]] = {}
    with duckdb.connect(str(path), read_only=True) as con:
        tables = [
            row[0]
            for row in con.execute(
                "select table_name from information_schema.tables "
                "where table_schema = 'main' and table_type = 'BASE TABLE'"
            ).fetchall()
        ]
        for table in sorted(tables):
            quoted = _quote_identifier(table)
            count_row = con.execute(f"select count(*) from {quoted}").fetchone()
            row_counts[table] = int(count_row[0]) if count_row is not None else 0
            if "schema_version" in table:
                schema_versions[table] = _first_column_values(con, quoted)
            if "rule_version" in table:
                rule_versions[table] = _first_column_values(con, quoted)
    return {
        "row_counts": row_counts,
        "schema_versions": schema_versions,
        "rule_versions": rule_versions,
    }


def _first_column_values(con: Any, quoted_table: str) -> list[str]:
    return [str(row[0]) for row in con.execute(f"select * from {quoted_table}").fetchall()]


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _copy_duckdbs(source_root: Path, target_root: Path) -> list[dict[str, str]]:
    copied: list[dict[str, str]] = []
    target_root.mkdir(parents=True, exist_ok=True)
    for source_path in sorted(source_root.glob("*.duckdb")):
        target_path = target_root / source_path.name
        shutil.copy2(source_path, target_path)
        copied.append(
            {
                "db_name": source_path.name,
                "source": str(source_path),
                "target": str(target_path),
                "sha256": sha256(target_path),
            }
        )
    return copied
