# Formal Full Rebuild And Daily Incremental Release Proof Card Evidence Index

日期：2026-05-12

## 1. Runtime Evidence Shape

| evidence | role |
|---|---|
| `H:\Asteria-report\pipeline\2026-05-12\formal-full-rebuild-and-daily-incremental-release-proof-card\summary.json` | proof summary |
| `H:\Asteria-report\pipeline\2026-05-12\formal-full-rebuild-and-daily-incremental-release-proof-card\closeout.md` | proof closeout |
| `H:\Asteria-temp\formal-release-proof\formal-full-rebuild-and-daily-incremental-release-proof-card\db-manifest.json` | DB manifest |
| `H:\Asteria-temp\formal-release-proof\formal-full-rebuild-and-daily-incremental-release-proof-card\backup-manifest.json` | backup manifest |
| `H:\Asteria-temp\formal-release-proof\formal-full-rebuild-and-daily-incremental-release-proof-card\staging-manifest.json` | staging manifest |
| `H:\Asteria-temp\formal-release-proof\formal-full-rebuild-and-daily-incremental-release-proof-card\promote-manifest.json` | promote manifest |
| `H:\Asteria-temp\formal-release-proof\formal-full-rebuild-and-daily-incremental-release-proof-card\resume-idempotence-manifest.json` | resume/idempotence manifest |
| `H:\Asteria-temp\formal-release-proof\formal-full-rebuild-and-daily-incremental-release-proof-card\final-release-evidence.json` | final release evidence |

## 2. Repo Evidence

| evidence | role |
|---|---|
| `src/asteria/pipeline/formal_release_source_proof.py` | source surface gap matrix runner |
| `scripts/pipeline/run_formal_release_source_proof.py` | source surface proof CLI entrypoint |
| `src/asteria/pipeline/formal_release_proof.py` | guarded proof runner |
| `scripts/pipeline/run_formal_release_proof.py` | CLI entrypoint |
| `tests/unit/pipeline/test_formal_release_source_proof.py` | source surface matrix coverage |
| `tests/unit/pipeline/test_formal_release_proof.py` | runner and CLI coverage |
| `tests/unit/pipeline/test_runner_surface.py` | runner allowlist coverage |
| `tests/unit/governance/test_formal_release_proof_gate_transition.py` | governance transition coverage |
| `governance/module_gate_registry.toml` | live next-card authority |
| `governance/module_api_contracts/pipeline.toml` | Pipeline contract authority |

## 3. Negative Evidence

| missing proof | evidence state |
|---|---|
| source surface gap matrix | `implemented / temp-report only` |
| formal full rebuild proof | `blocked / runner surface missing` |
| daily incremental release proof | `blocked / runner surface missing` |
| resume/idempotence release proof | `blocked / runner surface missing` |
| final release evidence complete | `retained gap` |
| System full build | not claimed |
| `v1 complete` | not claimed |
