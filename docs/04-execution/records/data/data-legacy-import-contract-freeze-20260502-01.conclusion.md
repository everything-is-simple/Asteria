# Data Legacy Import Contract Freeze Conclusion

日期：2026-05-02

状态：`passed`

## 1. Conclusion

`data-legacy-import-contract-freeze-20260502-01` 通过。Data Foundation 已冻结旧版
Lifespan raw/base DuckDB 的首轮导入合同：

```text
stock-only + day/week/month + backward adjusted base
```

该结论只授权 foundation-only 的 legacy import runner working build，不声明完整 Data
Foundation full build released，不创建正式 Data DB，也不改变 MALF 当前 formal evidence。

## 2. Gate Result

| 项 | 结果 |
|---|---|
| Data import contract | `frozen for legacy source intake` |
| Data formal DB creation | `not performed` |
| allowed build scope | `working DB only until promotion evidence card` |
| index/block | `sidecar availability only` |
| MALF rebuild | `not performed` |
| allowed next action | `data legacy import runner working build` |
| downstream construction | `not opened` |

## 3. Next

下一卡：

```text
data-legacy-import-runner-working-build-20260502-01
```
