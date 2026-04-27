from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AsteriaPaths:
    repo_root: Path
    data_root: Path
    report_root: Path
    validated_root: Path
    temp_root: Path

    @classmethod
    def from_env(cls, repo_root: Path | None = None) -> AsteriaPaths:
        resolved_repo = Path(os.environ.get("ASTERIA_REPO_ROOT", repo_root or Path.cwd())).resolve()
        return cls(
            repo_root=resolved_repo,
            data_root=Path(os.environ.get("ASTERIA_DATA_ROOT", "H:/Asteria-data")).resolve(),
            report_root=Path(os.environ.get("ASTERIA_REPORT_ROOT", "H:/Asteria-report")).resolve(),
            validated_root=Path(
                os.environ.get("ASTERIA_VALIDATED_ROOT", "H:/Asteria-Validated")
            ).resolve(),
            temp_root=Path(os.environ.get("ASTERIA_TEMP_ROOT", "H:/Asteria-temp")).resolve(),
        )

    def database_path(self, name: str) -> Path:
        if not name.endswith(".duckdb"):
            name = f"{name}.duckdb"
        return self.data_root / name

    def temp_run_root(self, module: str, run_id: str) -> Path:
        return self.temp_root / module / run_id
