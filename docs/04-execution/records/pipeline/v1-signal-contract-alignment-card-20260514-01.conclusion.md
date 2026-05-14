# Signal/PAS Contract Alignment Conclusion

日期：2026-05-14

状态：`passed / signal contract aligned`

## 1. Conclusion

`v1-signal-contract-alignment-card-20260514-01` 已完成。

本卡新增独立 Signal/PAS alignment runtime，只读消费第 6 卡 PAS proof DB，把
`triggered` 与 `reentry_candidate` PAS candidate 聚合为 Signal 可消费的 aligned signal。

核心裁决是：

```text
Signal/PAS contract alignment passed.
Signal 可以消费新版 Alpha/PAS candidate surface，并保留 lineage 与 T+1 open execution hint.
本卡不是收益证明、不是 broker proof，也不写正式 signal.duckdb。
```

## 2. Gate Result

| item | result |
|---|---|
| PAS input candidates | `4395` |
| active PAS candidates | `1262` |
| aligned formal signals | `1262` |
| component ledger rows | `1262` |
| hard_fail_count | `0` |
| required fields missing | `0` |
| forbidden fields present | `0` |
| temp alignment DB | `H:\Asteria-temp\signal_pas\v1-signal-contract-alignment-card-20260514-01\signal_pas_alignment.duckdb` |
| report dir | `H:\Asteria-report\pipeline\2026-05-14\v1-signal-contract-alignment-card-20260514-01` |
| validated zip | `H:\Asteria-Validated\Asteria-v1-signal-contract-alignment-card-20260514-01.zip` |
| next route card | `v1-alpha-pas-t-plus-one-return-proof-card` |

## 3. Boundary

当前 live truth 仍保持：

```text
final-release-closeout-card = passed / v1 complete
current live next = none / terminal
```

本卡不修改 `governance/module_gate_registry.toml`，不写 `H:\Asteria-data`，
不修改正式 `signal.duckdb` 或 `formal_signal_ledger` schema，不运行收益 proof，不接 broker，
不输出 position size、portfolio allocation、broker order、fill、account state 或 profit claim。

## 4. Evidence

- [card](v1-signal-contract-alignment-card-20260514-01.card.md)
- [record](v1-signal-contract-alignment-card-20260514-01.record.md)
- [evidence-index](v1-signal-contract-alignment-card-20260514-01.evidence-index.md)
- report: `H:\Asteria-report\pipeline\2026-05-14\v1-signal-contract-alignment-card-20260514-01`
- validated_zip: `H:\Asteria-Validated\Asteria-v1-signal-contract-alignment-card-20260514-01.zip`

## 5. Next Route Card

```text
v1-alpha-pas-t-plus-one-return-proof-card
```

下一卡才允许在 T+1 open 语义下做研究收益 readout；仍不得接 broker 或宣称实盘能力。
