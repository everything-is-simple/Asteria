# Validated 历史证据冷归档对齐卡

日期：2026-05-02

## 1. 基本信息

| 项 | 值 |
|---|---|
| module | `governance` |
| run_id | `validated-historical-evidence-rehydration-20260502-01` |
| stage | `validated-historical-evidence-layout-maintenance` |
| owner | `codex` |

## 2. 背景

`H:\Asteria-Validated` 根目录在多轮 closeout 后积累了大量历史 zip。为保持当前权威
资产更清晰，历史 passed evidence 可以冷归档到 `H:\Asteria-Validated\2.backups`。

本卡只处理历史 evidence 的可寻址路径和机器清单，不改变任何模块语义或门禁状态。

## 3. 允许动作

- 将历史 execution evidence index 中的历史 zip 路径对齐到 `2.backups`。
- 重建 `validated-asset-manifest-20260429-01.json`，记录当前根目录与 `2.backups` 布局。
- 生成治理维护 closeout、manifest 与 validated zip。
- 运行治理检查，确认历史证据路径仍可被机器检查解析。

## 4. 禁止动作

- 不删除 Validated 历史资产。
- 不把 `H:\Asteria-temp` 资产提升为权威资产。
- 不修改 Data / MALF / Alpha / Signal / Position 的门禁状态。
- 不打开 Position construction、下游施工或 full-chain pipeline。

## 5. 验收标准

| 项 | 要求 |
|---|---|
| historical evidence paths | `2.backups` 中可寻址 |
| validated manifest | 已存在并记录当前布局 |
| governance check | `scripts\governance\check_project_governance.py` 通过 |
| gate impact | `no module gate state changed` |
