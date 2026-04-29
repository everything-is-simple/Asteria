# Alpha Bounded Proof Record

日期：2026-04-29

## 1. 卡信息

| 项 | 值 |
|---|---|
| module | `alpha` |
| run_id | `alpha-bounded-proof-20260429-01` |
| result | `passed` |

## 2. 执行顺序

1. 确认当前门禁为 `Alpha bounded proof build card opened`。
2. 实现 Alpha family schema、runner、audit runner 和 bounded proof orchestrator。
3. 用 `H:\Asteria-data\malf_service_day.duckdb` 先跑 BOF 真实样本。
4. 扩展运行 BOF / TST / PB / CPB / BPB 五个 family。
5. 对五个 family DB 跑硬审计，确认 hard fail 为 0。
6. 生成 `H:\Asteria-report` closeout / manifest / audit summary。
7. 生成 `H:\Asteria-Validated\Asteria-alpha-bounded-proof-20260429-01.zip`。
8. 更新 execution conclusion index、gate ledger 和 governance registries。

## 3. 关键验证

| family | event | score | candidate | qualified | rejected | hard fail |
|---|---:|---:|---:|---:|---:|---:|
| BOF | 619 | 619 | 619 | 91 | 528 | 0 |
| TST | 619 | 619 | 619 | 59 | 560 | 0 |
| PB | 619 | 619 | 619 | 51 | 568 | 0 |
| CPB | 619 | 619 | 619 | 380 | 239 | 0 |
| BPB | 619 | 619 | 619 | 442 | 177 | 0 |

## 4. 正式 Alpha DB

| DB | 路径 |
|---|---|
| BOF | `H:\Asteria-data\alpha_bof.duckdb` |
| TST | `H:\Asteria-data\alpha_tst.duckdb` |
| PB | `H:\Asteria-data\alpha_pb.duckdb` |
| CPB | `H:\Asteria-data\alpha_cpb.duckdb` |
| BPB | `H:\Asteria-data\alpha_bpb.duckdb` |

## 5. 门禁更新

| 项 | 结果 |
|---|---|
| Alpha bounded proof | `passed` |
| hard_fail_count | `0` |
| allowed next action after card | `Signal freeze review` |
| still blocked | `Signal construction; Position / Portfolio Plan / Trade / System construction; Alpha full build; full-chain pipeline` |
