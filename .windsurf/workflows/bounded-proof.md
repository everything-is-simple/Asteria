---
description: 对主线模块运行 bounded proof 构建验证
---

1. 用 `code_search` 定位模块的 builder 和 proof 脚本
2. 确认临时输出路径设置为 `H:\Asteria-temp`，不得写入 `H:\Asteria-data`
3. 运行 bounded proof 构建（限定时间窗口，如 day 级）
4. 检查输出表面：schema、行数、空值率、边界完整性
5. 运行 pytest 验证（cache 放 `H:\Asteria-temp`）：

   ```powershell
   H:\Asteria\.venv\Scripts\python.exe -m pytest tests/ -x --cache-clear --basetemp=H:\Asteria-temp\pytest-tmp
   ```

6. 记录 proof 通过状态，更新 `docs/03-refactor/00-module-gate-ledger-v1.md`
