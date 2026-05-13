from __future__ import annotations

import argparse
import json
from pathlib import Path

from asteria.pipeline.v1_application_db_readiness_audit import (
    run_v1_application_db_readiness_audit,
)
from asteria.pipeline.v1_application_db_readiness_audit_contracts import (
    V1_APPLICATION_DB_READINESS_AUDIT_RUN_ID,
    ApplicationDbReadinessAuditRequest,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only audit of the 25 formal DuckDBs for post-v1 usage validation."
    )
    parser.add_argument("--repo-root", default="H:/Asteria")
    parser.add_argument("--formal-data-root", default="H:/Asteria-data")
    parser.add_argument("--report-root", default="H:/Asteria-report")
    parser.add_argument("--validated-root", default="H:/Asteria-Validated")
    parser.add_argument("--run-id", default=V1_APPLICATION_DB_READINESS_AUDIT_RUN_ID)
    args = parser.parse_args()

    summary = run_v1_application_db_readiness_audit(
        ApplicationDbReadinessAuditRequest(
            repo_root=Path(args.repo_root),
            formal_data_root=Path(args.formal_data_root),
            report_root=Path(args.report_root),
            validated_root=Path(args.validated_root),
            run_id=args.run_id,
        )
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.status.startswith("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
