from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.data.contracts import MarketMetaBuildRequest
from asteria.data.market_meta import run_market_meta_build


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Asteria Data Foundation market meta DB.")
    parser.add_argument("--data-root", type=Path, default=Path("H:/Asteria-data"))
    parser.add_argument("--temp-root", type=Path, default=Path("H:/Asteria-temp"))
    parser.add_argument("--mode", choices=("full", "bounded", "audit-only"), required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    summary = run_market_meta_build(
        MarketMetaBuildRequest(
            data_root=args.data_root,
            temp_root=args.temp_root,
            mode=args.mode,
            run_id=args.run_id,
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
