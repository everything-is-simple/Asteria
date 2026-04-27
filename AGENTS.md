# Asteria Agent Rules

This repository is the new Asteria refactor workspace.

Before changing code, every agent must read:

1. `README.md`
2. `docs/00-governance/00-asteria-refactor-charter-v1.md`
3. `docs/01-architecture/00-mainline-authoritative-map-v1.md`
4. `docs/01-architecture/01-database-topology-v1.md`
5. `docs/03-refactor/00-module-gate-ledger-v1.md`

Hard rules:

- Do not migrate legacy code into the mainline before the target module has a frozen design document.
- Do not edit more than one mainline module in one construction turn.
- Do not let a downstream module redefine an upstream module's semantics.
- Do not treat `data` as a strategy module. It is foundation infrastructure and source-fact service.
- Do not merge `wave_core_state` and `system_state`.
- Do not let Alpha, Signal, Portfolio, Trade, or System write back to MALF.
- Put formal databases under `H:\Asteria-data`.
- Put temporary build artifacts under `H:\Asteria-temp`.
- Keep `H:\Asteria-Validated` as validated input/output assets, not as a casual scratch directory.

