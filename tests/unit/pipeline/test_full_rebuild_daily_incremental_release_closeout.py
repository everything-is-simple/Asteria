from __future__ import annotations

import json
from pathlib import Path

from scripts.pipeline.run_full_rebuild_daily_incremental_release_closeout import (
    _request_from_args,
    build_parser,
)

from asteria.pipeline.full_rebuild_daily_incremental_release_closeout import (
    FULL_REBUILD_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_CARD,
    FullRebuildDailyIncrementalReleaseCloseoutRequest,
    run_full_rebuild_daily_incremental_release_closeout,
)

RUN_ID = "full-rebuild-and-daily-incremental-release-closeout-card"


def _repo_with_passed_chain(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    records = repo_root / "docs" / "04-execution" / "records" / "pipeline"
    records.mkdir(parents=True)
    (records / "pipeline-full-daily-incremental-chain-build-card.conclusion.md").write_text(
        "\n".join(
            [
                "# Pipeline Full Daily Incremental Chain Build Card Conclusion",
                "",
                "状态：`passed / pipeline full daily incremental chain proof passed`",
                "",
                "| allowed next action | "
                "`full_rebuild_and_daily_incremental_release_closeout_card` |",
                "| formal full rebuild not executed | `true` |",
                "| daily incremental release closeout not executed | `true` |",
            ]
        ),
        encoding="utf-8",
    )
    (records / "pipeline-full-daily-incremental-chain-build-card.evidence-index.md").write_text(
        "formal full rebuild not executed\n",
        encoding="utf-8",
    )
    return repo_root


def _request(tmp_path: Path) -> FullRebuildDailyIncrementalReleaseCloseoutRequest:
    return FullRebuildDailyIncrementalReleaseCloseoutRequest(
        repo_root=_repo_with_passed_chain(tmp_path),
        temp_root=tmp_path / "asteria-temp",
        report_root=tmp_path / "asteria-report",
        validated_root=tmp_path / "Asteria-Validated",
        run_id=RUN_ID,
        mode="audit-only",
    )


def test_closeout_blocks_release_when_formal_proofs_are_missing(tmp_path: Path) -> None:
    summary = run_full_rebuild_daily_incremental_release_closeout(_request(tmp_path))

    assert summary.card_id == FULL_REBUILD_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_CARD
    assert summary.status == "blocked / formal release evidence incomplete"
    assert summary.decisions["pipeline_chain_proof"] == "passed"
    assert summary.decisions["formal_full_rebuild_proof"] == "blocked"
    assert summary.decisions["daily_incremental_release_proof"] == "blocked"
    assert summary.decisions["v1_complete_claim"] == "forbidden / not claimed"
    assert summary.boundaries["formal_data_mutation"] is False
    assert summary.boundaries["pipeline_semantic_repair"] is False
    assert (tmp_path / "asteria-data").exists() is False

    payload = json.loads(Path(summary.summary_path).read_text(encoding="utf-8"))
    closeout = Path(summary.closeout_path).read_text(encoding="utf-8")

    assert payload["status"] == "blocked / formal release evidence incomplete"
    assert payload["decisions"]["formal_full_rebuild_proof"] == "blocked"
    assert "full rebuild passed: no" in closeout
    assert "daily incremental release passed: no" in closeout
    assert "v1 complete: no" in closeout


def test_closeout_fails_when_pipeline_chain_proof_is_missing(tmp_path: Path) -> None:
    request = FullRebuildDailyIncrementalReleaseCloseoutRequest(
        repo_root=tmp_path / "empty-repo",
        temp_root=tmp_path / "asteria-temp",
        report_root=tmp_path / "asteria-report",
        validated_root=tmp_path / "Asteria-Validated",
        run_id=RUN_ID,
        mode="audit-only",
    )

    summary = run_full_rebuild_daily_incremental_release_closeout(request)

    assert summary.status == "blocked / prerequisite chain proof missing"
    assert summary.decisions["pipeline_chain_proof"] == "blocked"
    assert summary.decisions["formal_full_rebuild_proof"] == "not evaluated"
    assert summary.boundaries["formal_data_mutation"] is False


def test_closeout_cli_defaults_to_repo_external_paths() -> None:
    args = build_parser().parse_args([])
    request = _request_from_args(args)

    assert request.repo_root == Path("H:/Asteria")
    assert request.temp_root == Path("H:/Asteria-temp")
    assert request.report_root == Path("H:/Asteria-report")
    assert request.validated_root == Path("H:/Asteria-Validated")
    assert request.mode == "audit-only"
    assert request.run_id == RUN_ID
