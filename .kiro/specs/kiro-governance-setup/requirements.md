# Requirements Document

## Introduction

本特性用于在 `.kiro/` 下建立 Kiro Agent 的治理配置，使 Kiro 以**从属 agent** 的身份在既有 Codex / Windsurf 治理体系下运行。

项目主力开发 agent 是 Codex，治理权威由仓库根目录的 `AGENTS.md`、`docs/00-governance/`、`docs/01-architecture/`、`docs/03-refactor/00-module-gate-ledger-v1.md`、`docs/04-execution/00-conclusion-index-v1.md` 与 `governance/*.toml` 承担。Windsurf 的治理面（`.windsurfrules`、`.windsurf/workflows/*.md`）已存在；Kiro 侧目前仅有 `.kiro/settings/mcp.json`，`.kiro/steering/` 为空。

本特性的目标是：

- 让 Kiro 的每一次行动可被追溯回既有权威文档与治理登记。
- 让 Kiro 的 steering / hooks 只**引用并窄化**既有规则，不新增并行权威。
- 让 Kiro 的路径、环境、门禁、模块边界与 Codex / Windsurf 对齐，不产生漂移。

**本特性明确不做的事：**

- 不修改任何主线模块源码。
- 不修改 `AGENTS.md`、`docs/00-governance/`、`docs/03-refactor/00-module-gate-ledger-v1.md`、`docs/04-execution/00-conclusion-index-v1.md` 以及 `governance/*.toml`。
- 不改变现有门禁状态或已通过卡的结论。
- 不引入新的治理权威文档（只允许在 `.kiro/steering/` 下编写**引用型**配置）。

## Glossary

- **Kiro_Agent**：本 IDE 中运行的 Kiro AI 开发助手实例。
- **Codex_Agent**：项目的主力开发 agent；本仓库的主要代码作者。
- **Governance_Reviewer**：人工治理评审者；对门禁放行与结构性变更拥有最终裁决权。
- **Authority_Docs**：AGENTS.md 列出的 6 份必读文档，依次为 `README.md`、`docs/00-governance/00-asteria-refactor-charter-v1.md`、`docs/01-architecture/00-mainline-authoritative-map-v1.md`、`docs/01-architecture/01-database-topology-v1.md`、`docs/03-refactor/00-module-gate-ledger-v1.md`、`docs/04-execution/00-conclusion-index-v1.md`。
- **Governance_Registries**：`governance/module_gate_registry.toml`、`governance/database_topology_registry.toml`、`governance/historical_ledger_registry.toml`、`governance/module_api_contracts/` 目录下的契约文件。
- **Gate_Ledger**：`docs/03-refactor/00-module-gate-ledger-v1.md` 以及 `governance/module_gate_registry.toml` 共同描述的模块门禁账本。
- **Kiro_Steering_Set**：`.kiro/steering/` 下由本特性新增的 Kiro 指引文件集合（markdown）。
- **Kiro_Config**：`.kiro/settings/mcp.json` 与 `.kiro/steering/` 的并集；为本特性的可写范围。
- **Construction_Turn**：Kiro_Agent 的一次完整对话轮次，其间会对仓库文件或数据库产生写入。
- **Mainline_Module**：`governance/module_gate_registry.toml` 中 `mainline = true` 的模块集合（当前为 `malf`、`alpha`、`signal`、`position`、`portfolio_plan`、`trade`、`system_readout`）。
- **Allowed_Next_Card**：`governance/module_gate_registry.toml` 中 `current_allowed_next_card` 字段所指向的卡，以及 `AGENTS.md` 中“下一步允许动作”字段；两者不一致时以 Governance_Reviewer 裁决为准。
- **Formal_Data_Root**：`H:\Asteria-data`，正式 DuckDB 数据资产落位。
- **Temp_Build_Root**：`H:\Asteria-temp`，pytest cache、working DB、ruff/mypy cache、run-scoped 临时产物落位。
- **Validated_Asset_Root**：`H:\Asteria-Validated`，只读权威资产目录；不得作为 scratch。
- **Report_Root**：`H:\Asteria-report`，人读报告与导出结果落位。
- **Repo_Venv**：`H:\Asteria\.venv`，由 `D:\miniconda\py310` 创建的仓库本地虚拟环境。
- **Governance_Check**：命令 `python scripts\governance\check_project_governance.py`。
- **Release_Gate_Commands**：`ruff check`、`ruff format --check`、`mypy src`、`pytest`，均使用 `H:\Asteria-temp` 下的 run-scoped cache / basetemp 路径。
- **Hard_Rules**：AGENTS.md “硬规则” 小节 + `.windsurfrules` “编辑硬规则” 小节所列规则的并集。

## Requirements

### Requirement 1：Kiro 权威文档读取义务

**User Story:** 作为 Governance_Reviewer，我希望 Kiro_Agent 在任何 Construction_Turn 开始前已读过 Authority_Docs 与相关 Governance_Registries，以便保证 Kiro 的每一次行动都建立在与 Codex_Agent 相同的治理前提上。

#### Acceptance Criteria

1. WHEN Kiro_Agent 开始一次 Construction_Turn，THE Kiro_Agent SHALL 在产出任何文件写入之前完成对 Authority_Docs 全部 6 份文件的读取并能够引用其相关段落。
2. WHEN Construction_Turn 涉及门禁、模块 API 契约或数据库拓扑的判断，THE Kiro_Agent SHALL 额外读取 Governance_Registries 中与该判断相关的 TOML 条目。
3. IF Authority_Docs 中任何一份无法读取或内容不可解析，THEN THE Kiro_Agent SHALL 停止 Construction_Turn 并向 Governance_Reviewer 报告受影响的文档路径。
4. THE Kiro_Steering_Set SHALL 包含一份指引文件，列出 Authority_Docs 与 Governance_Registries 的完整路径清单并注明其为引用来源而非可复写来源。

### Requirement 2：Kiro Steering 的引用-窄化原则

**User Story:** 作为 Codex_Agent，我希望 Kiro_Steering_Set 不成为并行权威，以便主线治理仍只有一个事实来源。

#### Acceptance Criteria

1. THE Kiro_Steering_Set SHALL 只通过相对路径链接到 Authority_Docs 与 Governance_Registries，不得整段复制其规则正文。
2. WHERE Kiro_Steering_Set 需要对某条已有规则做**窄化**（例如限定到 Kiro 情境下的子集），THE Kiro_Steering_Set SHALL 明确标注原始条款位置并声明“本文件为引用与窄化，不覆盖原始权威”。
3. IF Kiro_Steering_Set 的条款与 AGENTS.md、`docs/00-governance/` 或 `governance/*.toml` 的条款冲突，THEN THE Kiro_Agent SHALL 以 AGENTS.md 与 `governance/*.toml` 为准并记录冲突。
4. THE Kiro_Agent SHALL NOT 在 `docs/00-governance/` 以外的任何位置创建新的“治理规则”型文档；`.kiro/steering/` 下的文件必须以引用型定位自述。

### Requirement 3：文件路径与数据落位边界

**User Story:** 作为 Governance_Reviewer，我希望 Kiro_Agent 的每一次写入都落在正确的根目录，以便正式数据、临时产物与已验证资产不被混淆。

#### Acceptance Criteria

1. WHEN Kiro_Agent 产出正式 DuckDB 数据资产，THE Kiro_Agent SHALL 将其写入 Formal_Data_Root。
2. WHEN Kiro_Agent 产出 pytest cache、working DB、ruff/mypy cache、report artifacts 或任何 run-scoped 临时产物，THE Kiro_Agent SHALL 将其写入 Temp_Build_Root 下 run-scoped 子目录。
3. WHEN Kiro_Agent 产出人读报告或导出结果，THE Kiro_Agent SHALL 将其写入 Report_Root。
4. THE Kiro_Agent SHALL 以只读方式访问 Validated_Asset_Root，并 SHALL NOT 向 Validated_Asset_Root 写入 scratch 或 working 产物。
5. THE Kiro_Agent SHALL NOT 在仓库根目录（`H:\Asteria`）新建 `.codex-tmp/`、`tmp/`、`temp/`、`reports/`、`artifacts/` 等临时目录。
6. IF 一次请求要求 Kiro_Agent 写入的路径不属于上述任一根目录，THEN THE Kiro_Agent SHALL 拒绝执行并说明受约束的规则条款。

### Requirement 4：Python 运行环境绑定

**User Story:** 作为 Codex_Agent，我希望 Kiro_Agent 与我共用同一套 Python 环境，以便依赖解析与测试结果可复现。

#### Acceptance Criteria

1. WHEN Kiro_Agent 需要执行 Python 命令，THE Kiro_Agent SHALL 使用 Repo_Venv 下的解释器（`H:\Asteria\.venv\Scripts\python.exe`）。
2. THE Kiro_Agent SHALL NOT 创建或激活除 Repo_Venv 与 `D:\miniconda\py310` 之外的 Python 环境。
3. IF Repo_Venv 缺失或损坏，THEN THE Kiro_Agent SHALL 提示使用 `D:\miniconda\py310\python.exe -m venv H:\Asteria\.venv` 与 `H:\Asteria\.venv\Scripts\python.exe -m pip install -e ".[dev]"` 重建，且 SHALL NOT 自动切换到系统 Python。
4. THE Kiro_Agent SHALL 在调用 pytest / ruff / mypy 时显式指定 Temp_Build_Root 下的 run-scoped cache 目录。

### Requirement 5：治理检查与 release gate 调用义务

**User Story:** 作为 Governance_Reviewer，我希望 Kiro_Agent 在任何结构性变更前自觉调用治理检查，以便门禁与路径约束不被绕过。

#### Acceptance Criteria

1. WHEN Construction_Turn 将要对 `src/`、`scripts/`、`governance/`、`docs/` 或仓库根目录结构产生新增、删除或移动，THE Kiro_Agent SHALL 先运行 Governance_Check 并将其退出码与输出记入本轮次的产出。
2. IF Governance_Check 返回非零退出码，THEN THE Kiro_Agent SHALL 停止该 Construction_Turn 并在回复中引用失败项。
3. WHEN 被请求进入 release gate 前核查，THE Kiro_Agent SHALL 在回复中列出 Release_Gate_Commands 的完整命令行，包括 Temp_Build_Root 下的 cache 与 basetemp 路径占位符（如 `H:\Asteria-temp\ruff-cache`、`H:\Asteria-temp\mypy-cache`、`H:\Asteria-temp\pytest-cache-<run_id>`、`H:\Asteria-temp\pytest-tmp-<run_id>`）。
4. THE Kiro_Agent SHALL NOT 将 pytest / ruff / mypy 的 cache 或临时文件写入仓库根目录。

### Requirement 6：当前门禁状态遵循

**User Story:** 作为 Governance_Reviewer，我希望 Kiro_Agent 只在 Allowed_Next_Card 范围内协助施工，以便 Gate_Ledger 不被绕过。

#### Acceptance Criteria

1. WHEN Kiro_Agent 被请求进行施工相关动作，THE Kiro_Agent SHALL 以 `governance/module_gate_registry.toml` 的 `current_allowed_next_card` 与 AGENTS.md “下一步允许动作” 作为授权边界；两者不一致时，THE Kiro_Agent SHALL 先向 Governance_Reviewer 报告分歧，不得自行选边。
2. IF 一次请求要求 Kiro_Agent 执行 Trade full build、Portfolio Plan full build、Position full build、System 下游施工或全链路 pipeline 构建，且 Gate_Ledger 未显式授权，THEN THE Kiro_Agent SHALL 拒绝执行并引用未授权的卡名。
3. WHERE 当前 Allowed_Next_Card 为 `trade_bounded_proof_build_card`，THE Kiro_Agent SHALL 仅协助该卡的**准备性**产出（设计引用、脚手架审阅、脚本草稿），不得将其升级为 Trade 的正式 build 或 full build。
4. THE Kiro_Agent SHALL NOT 修改 `docs/03-refactor/00-module-gate-ledger-v1.md`、`docs/04-execution/00-conclusion-index-v1.md` 与 `governance/module_gate_registry.toml` 的门禁结论字段。

### Requirement 7：模块边界与硬规则继承

**User Story:** 作为 Codex_Agent，我希望 Kiro_Agent 继承与我一致的 Hard_Rules，以便模块边界不被破坏。

#### Acceptance Criteria

1. THE Kiro_Agent SHALL 在一次 Construction_Turn 内最多编辑 Mainline_Module 集合中的一个模块的代码文件。
2. IF 一次请求要求 Kiro_Agent 在同一 Construction_Turn 内跨 Mainline_Module 修改代码，THEN THE Kiro_Agent SHALL 拆分为多次 Construction_Turn 或拒绝执行并说明原因。
3. THE Kiro_Agent SHALL NOT 在目标模块的权威设计文档冻结之前将 legacy code 迁入主线。
4. THE Kiro_Agent SHALL NOT 让下游模块重定义上游模块的语义。
5. THE Kiro_Agent SHALL NOT 将 `data` 模块当作策略模块；对 `data` 的任何扩展只能通过明确的 maintenance card 进行。
6. THE Kiro_Agent SHALL NOT 合并 `wave_core_state` 与 `system_state`。
7. THE Kiro_Agent SHALL NOT 让 Alpha、Signal、Portfolio、Trade、System 模块产生对 MALF 的写回路径。

### Requirement 8：文件长度与注释质量限制

**User Story:** 作为 Codex_Agent，我希望 Kiro_Agent 生成的代码与文档满足与我一致的长度与注释标准，以便两个 agent 的产出风格可被同一套审核流程处理。

#### Acceptance Criteria

1. THE Kiro_Agent SHALL 使新增或修改后的任意 Python 源文件行数不超过 500 行。
2. THE Kiro_Agent SHALL 使新增或修改后的任意脚本 wrapper 行数不超过 240 行。
3. THE Kiro_Agent SHALL 使新增或修改后的任意设计 / spec / steering markdown 文件行数不超过 1200 行；超过时按模块或章节拆分。
4. IF 一次修改将使某文件越过上述任一上限，THEN THE Kiro_Agent SHALL 拒绝该修改并提出拆分方案。
5. THE Kiro_Agent SHALL 在新增注释时解释意图、边界或不明显的不变量，SHALL NOT 产出仅复述代码字面含义的注释。

### Requirement 9：与 Codex / Windsurf 的非干扰共存

**User Story:** 作为 Codex_Agent，我希望 Kiro_Agent 的治理配置不干扰我的工作面，以便我可以继续以主力 agent 的身份施工。

#### Acceptance Criteria

1. THE Kiro_Agent SHALL 只在 `.kiro/` 目录内新增或修改配置性文件（steering、hooks、settings）；SHALL NOT 修改 `.codex/`、`.windsurf/`、`.windsurfrules`、`AGENTS.md`。
2. THE Kiro_Agent SHALL NOT 复写 `.windsurf/workflows/*.md` 的内容到 `.kiro/steering/` 下；如需引用，THE Kiro_Steering_Set SHALL 使用相对路径链接。
3. WHEN Codex_Agent 与 Kiro_Agent 对同一文件存在并发意图，THE Kiro_Agent SHALL 视 Codex_Agent 为主作者并让出。
4. THE Kiro_Agent SHALL NOT 更改 `governance/` 目录下任何 TOML 文件的已有结构字段；仅在 Governance_Reviewer 显式同意时才可新增 Kiro 专属的 optional 节。

### Requirement 10：可追溯性与幂等性

**User Story:** 作为 Governance_Reviewer，我希望 Kiro_Steering_Set 可以被反复重读而不产生行为漂移，且每一次 Kiro 动作都可以被追溯到具体规则条款，以便审计成本最低。

#### Acceptance Criteria

1. WHEN Kiro_Agent 给出一次治理相关的判断或拒绝，THE Kiro_Agent SHALL 同时引用该判断所依据的 Authority_Docs 或 Governance_Registries 的具体文件路径与条款关键词。
2. THE Kiro_Steering_Set SHALL 在重复加载时产生相同语义；任何条款 SHALL 具有明确的单一含义而不依赖加载顺序。
3. IF Kiro_Steering_Set 发现自身条款出现歧义或与 Authority_Docs 不同步，THEN THE Kiro_Agent SHALL 提示 Governance_Reviewer 更新 `.kiro/steering/` 而非就地重写规则。

## Correctness Properties

以下性质用作设计阶段生成属性测试或脚本化审计检查的输入。变量约定：`A` 表示一次 Kiro 动作；`T` 表示一次 Construction_Turn；`P` 表示一次文件写入路径。

- **P1（引用封闭性）：** 对任意 Kiro 动作 `A`，其所引用的治理文档集合 `D(A)` 满足 `D(A) ⊆ Authority_Docs ∪ Governance_Registries ∪ docs/` 的只读子树；`.kiro/steering/` 自身不得被当作权威来源。
- **P2（落位路径良构）：**
  - 对任意写入路径 `P`，若 `P` 是 DuckDB 正式资产，则 `P` 在 Formal_Data_Root 下；
  - 若 `P` 是 run-scoped 临时产物（pytest cache、working DB、ruff/mypy cache、report artifact），则 `P` 在 Temp_Build_Root 下；
  - 若 `P` 是人读报告，则 `P` 在 Report_Root 下；
  - `P` 绝不位于 Validated_Asset_Root 之下；
  - `P` 绝不位于仓库根目录 `H:\Asteria\` 直接下的 `.codex-tmp/` / `tmp/` / `temp/` / `reports/` / `artifacts/`。
- **P3（单模块构造约束）：** 对任意 Construction_Turn `T`，设 `modules_edited(T)` 为该轮次写入过的代码文件所属模块集合，则 `|modules_edited(T) ∩ Mainline_Module| ≤ 1`。
- **P4（门禁边界约束）：** 对任意被请求的施工动作 `A`，令 `allowed_next_cards(s)` 为治理登记当前状态 `s` 下允许的下一卡集合；则 `A` 的目标卡 `∈ allowed_next_cards(s)`。当前状态下，`allowed_next_cards(s) = { trade_bounded_proof_build_card }`（引用自 AGENTS.md；若 `governance/module_gate_registry.toml` 的 `current_allowed_next_card` 与其分歧，则依赖 Governance_Reviewer 裁决，而非 Kiro 自决）。
- **P5（非并行权威）：** 对任意 Kiro_Steering_Set 文件 `s`，`s` 的规则性语句集合 `R(s)` 不得包含与 Authority_Docs 或 `governance/*.toml` 中同义条款语义矛盾的陈述；`R(s)` 仅允许是原始条款的**引用**或其**严格窄化**（即 Kiro 的约束至少和原始条款一样强，不得更宽松）。
- **P6（幂等性）：** 对 Kiro_Steering_Set 的任意加载操作 `L`，`L ∘ L` 与 `L` 在 Kiro_Agent 行为上等价（重复读取不产生漂移）。
- **P7（可追溯性）：** 对任意治理相关的回复 `R`，存在一个非空引用集合 `C(R)` 指向 Authority_Docs、Governance_Registries 或既有 conclusion/evidence 文件，使得 `R` 的每一条治理主张都能映射到 `C(R)` 中至少一个条款。

### Property 测试适用性说明

- P2、P3、P5、P6 以**属性测试**方式实现最有价值：路径、模块集合、文本规则、加载幂等性均可用生成器覆盖多种输入。
- P4 取决于 Gate_Ledger 的当前状态快照，更适合用**示例测试 + 注册表扫描**，而非属性测试。
- P1、P7 适合以**脚本化审计**（扫描回复样本或 steering 文件引用）实现，而非通用属性测试。
- 具体实现方式、生成器与抽样策略将在 design 阶段给出。
