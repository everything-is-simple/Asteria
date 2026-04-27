from __future__ import annotations

import json
import sys
from pathlib import Path

from asteria import __version__
from asteria.core.paths import AsteriaPaths


def main() -> int:
    paths = AsteriaPaths.from_env(Path(__file__).resolve().parents[2])
    payload = {
        "asteria_version": __version__,
        "python": sys.version.split()[0],
        "repo_root": str(paths.repo_root),
        "data_root": str(paths.data_root),
        "report_root": str(paths.report_root),
        "validated_root": str(paths.validated_root),
        "temp_root": str(paths.temp_root),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
