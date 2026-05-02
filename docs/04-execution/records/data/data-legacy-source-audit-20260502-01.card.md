# Data Legacy Source Audit Card

日期：2026-05-02

状态：`audit-only / source-fact intake review`

## 1. Scope

本卡只读审计上一版系统的本地 raw/base DuckDB：

```text
H:\Lifespan-data\raw
H:\Lifespan-data\base
```

审计范围为 stock / index / block 的 day / week / month legacy facts。其中只有
`stock + backward + day/week/month` 被列为后续 Asteria Data Foundation 首轮主输入；
index/block 只登记为 sidecar availability，不进入首轮 MALF v1.3 formal rebuild。

## 2. Allowed

- 只读连接 legacy DuckDB。
- 输出 row count、symbol count、raw/base 覆盖差异。
- 生成 `H:\Asteria-report\data\2026-05-02\data-legacy-source-audit-20260502-01` 报告。
- 落档 repo execution record。

## 3. Forbidden

- 不写 `H:\Asteria-data`。
- 不创建正式 Data Foundation DB。
- 不把旧库解释为策略语义权威。
- 不打开 Position、Portfolio、Trade、System 或 full-chain pipeline。

## 4. Acceptance

本卡通过条件：

- stock backward day/week/month raw/base row count 对齐。
- stock backward day/week/month symbol count 对齐。
- raw-only/base-only symbol count 为 0。
- index/block 仅作为 sidecar availability 登记。
