# Validated 历史证据冷归档对齐 Record

日期：2026-05-02

## 1. 执行动作

1. 确认治理检查失败根因是历史 evidence zip 已从 Validated 根目录移入
   `H:\Asteria-Validated\2.backups`，而历史 evidence index 仍指向旧根目录路径。
2. 将历史 passed execution evidence index 中的历史 zip 路径改为 `2.backups` 路径。
3. 重建 `H:\Asteria-Validated\validated-asset-manifest-20260429-01.json`，记录根目录与
   `2.backups` 的当前资产布局和 SHA256。
4. 生成本卡 report closeout、manifest 与 validated zip。
5. 运行治理检查确认路径闭环通过。

## 2. 影响范围

| 范围 | 结果 |
|---|---|
| repo execution evidence indexes | 历史 zip 路径改为 `2.backups` |
| Validated manifest | 已重建 |
| formal DB | 未创建 |
| module gate | 未改变 |
| current allowed next action | `Position freeze review reentry` |

## 3. 边界说明

本次是 Validated 资产布局维护，不是 Data、MALF、Alpha、Signal 或 Position 的业务卡。
历史 evidence 的语义、状态和结论不因冷归档位置变化而改变。
