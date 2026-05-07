from __future__ import annotations

import json

from asteria.position.bootstrap import run_position_audit
from scripts.position.run_position_build import _add_common_args, _request_from_args


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run Position audit.")
    _add_common_args(parser)
    args = parser.parse_args()
    summary = run_position_audit(_request_from_args(args))
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.hard_fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
