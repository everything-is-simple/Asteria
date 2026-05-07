---
description: 对主线模块做 freeze review 前的标准代码审查
---

1. 用 `code_search` 找到目标模块的所有文件、入口、上下游依赖
2. 读取模块的权威设计文档（`docs/02-modules/<module>/`）
3. 逐项对照设计文档检查实现：接口契约、边界条件、数据流向
4. 检查 Python 文件行数（≤ 500 行）、脚本 wrapper 行数（≤ 240 行）
5. 运行治理检查：
   ```
   python scripts\governance\check_project_governance.py
   ruff check . --cache-dir H:\Asteria-temp\ruff-cache
   mypy src --cache-dir H:\Asteria-temp\mypy-cache
   ```
6. 给出 review 结论：通过 / 阻塞（列出具体阻塞项）
