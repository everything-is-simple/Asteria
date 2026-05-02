# Data Foundation Production Baseline Seal Card

日期：2026-05-02

状态：`passed`

## 1. 目标

本卡不重建 DB，不新增 runner，不扩展参考事实，只把当前已经通过审计的 Data
Foundation 正式库封为主线输入底座：

```text
data-foundation-production-baseline-seal-20260502-01
```

封印后，Data 不再作为 Position freeze review reentry 前的泛化补数入口。后续 Data
只能通过明确 maintenance card 扩展。

## 2. 允许范围

| 项 | 裁决 |
|---|---|
| live Data DB 只读复核 | 允许 |
| Data production audit | 允许 |
| Data 六件套状态更新 | 允许 |
| governance registry / conclusion index 同步 | 允许 |
| 外部 report 与 validated zip | 允许 |

## 3. 禁止范围

| 项 | 裁决 |
|---|---|
| 重建或改写正式 Data DB | 禁止 |
| 新增 Data runner 或 schema | 禁止 |
| 补 ST、停牌、上市退市、历史行业沿革 | 禁止 |
| MALF / Alpha / Signal / Position 语义修改 | 禁止 |
| Position construction 或下游施工 | 禁止 |
