from __future__ import annotations

import json

from asteria.signal.bootstrap import run_signal_audit
from scripts.signal.run_signal_build import _add_common_args, _request_from_args


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run Signal audit.")
    _add_common_args(parser)
    args = parser.parse_args()
    summary = run_signal_audit(_request_from_args(args))
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.hard_fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
