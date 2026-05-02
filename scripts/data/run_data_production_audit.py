from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.data.production_audit import run_data_production_audit


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Asteria Data Foundation production audit.")
    parser.add_argument("--data-root", type=Path, default=Path("H:/Asteria-data"))
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    summary = run_data_production_audit(data_root=args.data_root, run_id=args.run_id)
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
