# Signal Bounded Proof Record

日期：2026-04-29

## 1. 执行摘要

`signal-bounded-proof-20260429-01` 已完成 Signal bounded proof。实现采用确定性最小聚合规则：
按 `symbol + timeframe + bar_dt` 聚合五个 Alpha family candidate，生成 input snapshot、
formal signal ledger、component ledger 和 audit ledger。

## 2. 前辈系统参考

| 来源 | 使用方式 |
|---|---|
| `H:\history-lifespan\astock_lifespan-alpha` | 参考 runner wrapper、schema bootstrap、unit fixture 组织 |
| `H:\history-lifespan\lifespan-0.01` | 参考 formal signal materialization、run/event ledger、审计思想 |
| `H:\history-lifespan\MarketLifespan-Quant` | 参考 PAS trigger/formal signal 测试场景 |
| `H:\history-lifespan\EmotionQuant-gamma` | 仅作为研究旁证，不进入本卡代码 |

前辈系统未成为 Asteria Signal 语义权威；本卡未继承旧 PAS/MALF/alpha_signal 合并语义。

## 3. 执行命令

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\signal\run_signal_bounded_proof.py --run-id signal-bounded-proof-20260429-01 --source-alpha-root H:/Asteria-data --target-signal-db H:/Asteria-data/signal.duckdb --report-root H:/Asteria-report --validated-root H:/Asteria-Validated --temp-root H:/Asteria-temp --source-alpha-release-version alpha-bounded-proof-20260429-01 --start-dt 2024-01-01 --end-dt 2024-12-31 --symbol-limit 4
```

## 4. 结果

| 项 | 值 |
|---|---:|
| input_candidate_count | 3095 |
| formal_signal_count | 619 |
| active_signal_count | 598 |
| rejected_signal_count | 21 |
| component_count | 3095 |
| hard_fail_count | 0 |

## 5. 边界确认

- Signal 只读 Alpha family DB。
- Signal 未读取 MALF / filter / structure。
- Signal 未修改 Alpha DB，未回写 MALF。
- Signal 未创建 Position / Portfolio Plan / Trade / System / Pipeline DB。
- `component_weight` 仅为解释权重，不是资金权重。
