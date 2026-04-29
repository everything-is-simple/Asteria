# Asteria System Design Set Refresh Card

日期：2026-04-29

## 1. 背景

本卡创建 `H:\Asteria-Validated\Asteria_System_Design_Set_v1_0` 和同名 zip，把
Asteria 当前全系统模块设计状态整理成一个 validated design set。该资产类似 MALF
终稿包的阅读入口，但不修改 MALF 终稿，也不改变当前施工门禁。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `governance` |
| run_id | `asteria-system-design-set-refresh-20260429-01` |
| stage | `system-design-set-refresh` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| current docs/code snapshot | `H:\Asteria-Validated\Asteria-docs-code-20260429-130309.zip` |
| MALF authority directory | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` |
| module docs | `docs/02-modules` |
| API contracts | `governance/module_api_contracts` |
| topology registry | `governance/database_topology_registry.toml` |

## 4. 允许动作

- 创建 `Asteria_System_Design_Set_v1_0` 目录和同名 zip。
- 为 Data、MALF、Alpha、Signal、Position、Portfolio Plan、Trade、System Readout、Pipeline
  写入当前状态设计文件。
- 为每个模块补齐 `Data Model` 与 `API Contract` 章节。
- 生成 `MANIFEST.json`，记录设计包文件 SHA256。
- 更新 repo 资产清单、执行索引和 Validated 根 README / manifest。
- 生成本卡 closeout、manifest 和 Validated evidence zip。

## 5. 禁止动作

- 不修改 `MALF_Three_Part_Design_Set_v1_2` 终稿。
- 不把下游 pre-gate 模块标为 frozen / released。
- 不创建正式 DB。
- 不打开 Alpha 或下游代码施工。
- 不建立 full-chain pipeline。
- 不让下游模块写回 MALF。

## 6. 当前门禁

| 项 | 值 |
|---|---|
| latest passed gate | `MALF day bounded proof` |
| allowed next action | `Alpha freeze review` |
| construction still blocked | `Alpha code / formal DB / downstream / full-chain pipeline` |
