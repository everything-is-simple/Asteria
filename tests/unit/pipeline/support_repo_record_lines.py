from __future__ import annotations


def pipeline_record_line(field: str, run_id: str, suffix: str) -> str:
    return f'{field} = "docs/04-execution/records/pipeline/{run_id}.{suffix}.md"'


def active_card_line(run_id: str) -> str:
    return pipeline_record_line("active_card", run_id, "card")


def release_conclusion_line(run_id: str) -> str:
    return pipeline_record_line("release_conclusion", run_id, "conclusion")


def evidence_index_line(run_id: str) -> str:
    return pipeline_record_line("evidence_index", run_id, "evidence-index")
