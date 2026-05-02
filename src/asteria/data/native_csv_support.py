from __future__ import annotations

import json
from datetime import datetime

import duckdb

from asteria.data.contracts import DataBootstrapRequest, DataBootstrapSummary, TdxSourceFile


def normalized_path(source: TdxSourceFile) -> str:
    return str(source.source_path).replace("\\", "/")


def sql_file_list(chunk: tuple[TdxSourceFile, ...]) -> str:
    return ", ".join(f"'{normalized_path(source)}'" for source in chunk)


def source_has_data_rows(source: TdxSourceFile) -> bool:
    with source.source_path.open("r", encoding="gbk") as handle:
        for index, line in enumerate(handle):
            if index < 2:
                continue
            if looks_like_data_row(line.strip()):
                return True
    return False


def looks_like_data_row(value: str) -> bool:
    if not value or value.startswith("#"):
        return False
    first_token = value.split()[0]
    normalized = first_token.replace("/", "-")
    parts = normalized.split("-")
    return len(parts) == 3 and all(part.isdigit() for part in parts)


def chunked(
    sources: tuple[TdxSourceFile, ...],
    size: int,
) -> tuple[tuple[TdxSourceFile, ...], ...]:
    return tuple(sources[index : index + size] for index in range(0, len(sources), size))


def create_temp_source_manifest(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("drop table if exists temp_source_manifest")
    con.execute(
        """
        create temp table temp_source_manifest (
            source_file_key varchar,
            asset_type varchar,
            symbol varchar,
            adj_mode varchar,
            source_path varchar,
            source_path_normalized varchar,
            source_size_bytes bigint,
            source_mtime timestamp,
            source_content_hash varchar
        )
        """
    )


def price_line_for_adj_mode(adj_mode: str) -> str:
    return "execution_price_line" if adj_mode == "none" else "analysis_price_line"


def scalar(con: duckdb.DuckDBPyConnection, sql: str) -> int:
    row = con.execute(sql).fetchone()
    if row is None:
        return 0
    return int(row[0])


def save_checkpoint(
    request: DataBootstrapRequest,
    summary: DataBootstrapSummary,
    *,
    now: datetime,
) -> None:
    request.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": summary.status,
        "summary": summary.as_dict(),
        "created_at": now.isoformat(),
    }
    request.checkpoint_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
