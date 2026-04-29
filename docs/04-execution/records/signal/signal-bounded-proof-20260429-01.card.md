# Signal Bounded Proof Card

日期：2026-04-29

## 1. 基本信息

| 项 | 值 |
|---|---|
| module | `signal` |
| run_id | `signal-bounded-proof-20260429-01` |
| stage | `bounded-proof` |
| status | `executed` |

## 2. 授权来源

本卡由 `signal-bounded-proof-build-card-20260429-01` 打开。Signal freeze review 已通过，
Alpha bounded proof 已通过，当前仅授权 Signal bounded proof。

## 3. 输入范围

| 项 | 值 |
|---|---|
| source_alpha_release_version | `alpha-bounded-proof-20260429-01` |
| source DBs | `H:\Asteria-data\alpha_bof.duckdb`; `H:\Asteria-data\alpha_tst.duckdb`; `H:\Asteria-data\alpha_pb.duckdb`; `H:\Asteria-data\alpha_cpb.duckdb`; `H:\Asteria-data\alpha_bpb.duckdb` |
| source table | `alpha_signal_candidate` |
| sample scope | `day / 2024-01-01..2024-12-31 / symbol_limit=4` |
| target DB | `H:\Asteria-data\signal.duckdb` |

## 4. 允许动作

- 创建 Signal bounded proof 所需的 schema、runner、audit 和 unit tests。
- 只读消费五个 Alpha family DB 的 released candidate 表面。
- 写入 bounded proof 范围内的 `signal.duckdb`。
- 生成 report closeout、manifest、validated zip 和 repo 内四件套。

## 5. 禁止动作

- 不读取 MALF、filter、structure 或 legacy downstream 作为 Signal 正式输入。
- 不修改 Alpha DB，不回写 MALF。
- 不输出 position、portfolio、order、fill 语义。
- 不创建 Position / Portfolio Plan / Trade / System / Pipeline runner 或 DB。
- 不授权 Signal full build。
