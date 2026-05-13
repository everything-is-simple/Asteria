# V1 Usage Validation Scope Conclusion

日期：2026-05-12

状态：`passed / scope frozen / roadmap-only route`

## 1. 结论

`v1-usage-validation-scope-card-20260512-01` 已通过。本卡在不改动 Asteria 主线
terminal truth 的前提下，完成了 v1 后使用验证路线的第一张 scope freeze。

当前冻结结果是：

- 股票池固定为 `31` 个申万一级行业各取 `1` 只代表股；
- 时间窗固定为 `2024-01-02..2024-12-31`；
- 研究问题固定为“当前链路能否给出可解释、可审计的结构-信号-持仓-交易意图读出”；
- 报告形态固定为 `双层输出`；
- 正式 DB 权限固定为 `read_only`。

## 2. 放行影响

| 项 | 结果 |
|---|---|
| live next action | `none / terminal` |
| live next reopened by this card | `no` |
| next route card | `v1-application-db-readiness-audit-card` |
| 31-industry sample frozen | `yes` |
| H:\Asteria-data mutation | `no` |

## 3. 仍保留的 caveat

| 项 | 状态 |
|---|---|
| ST / 停牌正式 coverage | retained |
| 完整上市 / 退市生命周期 | retained |
| 历史行业沿革 | retained |
| fill source gap | retained |

## 4. 证据入口

- [evidence-index](v1-usage-validation-scope-card-20260512-01.evidence-index.md)
- [record](v1-usage-validation-scope-card-20260512-01.record.md)
- `H:\Asteria-report\pipeline\2026-05-13\v1-usage-validation-scope-card-20260512-01\scope-manifest.json`
