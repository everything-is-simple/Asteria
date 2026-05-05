# Data 卡后 MALF 重跑判定口径 v1

日期：2026-05-05

## 1. 目的

本口径用于在看完任意一张 `Data` 卡后，快速判断当前 `MALF day` 三库是否需要重跑。

它回答：

| 问题 | 回答 |
|---|---|
| `Data` 改了，当前 `MALF day` 要不要重跑 | 是 |
| 应该由谁来重跑 `MALF` | 是 |
| 哪些变化只算 future week/month 依赖 | 是 |
| 是否自动打开 MALF 施工权限 | 否 |

本口径是治理判定，不是执行授权。若结论为 `rerun`，仍必须由 `MALF` 自己在被授权的卡内执行
`core -> lifespan -> service -> audit`，不能由 `Data` runner 代写 MALF 库。

## 2. 一句话规则

```text
Data 负责产出正式事实。
MALF 只消费正式事实，并在自己的 runner 链路里自行 rerun/rebuild。
```

当前 `MALF day` 的正式输入只认：

```text
H:\Asteria-data\market_base_day.duckdb
```

当前不允许直接作为 `MALF` 正式输入的来源：

```text
raw_market.duckdb
legacy_malf_day.duckdb
mock_formal_data
```

## 3. 快速判定表

| Data 卡结果 | 当前 MALF day 是否消费 | 裁决 | 当前动作 |
|---|---|---|---|
| `market_base_day.duckdb` 的 day 行集变化 | 是 | `rerun` | 由 `MALF` 自己重跑 `core -> lifespan -> service -> audit` |
| `market_base_day.duckdb` 的 `symbol / timeframe / bar_dt / high_px / low_px` 变化 | 是 | `rerun` | 同上 |
| `market_base_day.duckdb` 仅 `open_px / close_px / volume / amount` 变化，且 day 行集不变 | 当前 runtime 不直接消费 | `no rerun` | 记录为观察项即可 |
| `raw_market.duckdb` 变化，但尚未 formalize 到 `market_base_day.duckdb` | 否 | `no rerun` | 不直接触发 MALF |
| `market_meta.duckdb` 变化 | 当前 runtime 不消费 | `no rerun` | 不直接触发 MALF day |
| `market_base_week.duckdb` 或 `market_base_month.duckdb` 变化 | 不消费当前 day | `future dependency` | 记为 future MALF week/month 依赖 |
| `legacy_malf_day.duckdb` 相关变化 | forbidden input | `not applicable` | 不纳入当前正式判定 |

## 4. 三步使用法

1. 先看 `Data` 卡是否真的改变了正式输出，而不只是改变 `raw_market` 或 working DB。
2. 若改变的是正式输出，再看是否落到当前 `MALF day` 实际消费的 `market_base_day` day 行集或读取面。
3. 最终只输出三种结论之一：

```text
rerun
no rerun
future dependency
```

## 5. 当前 runtime truth

当前 `MALF day` 的实际依赖链是：

```text
market_base_day
-> malf_core_day
-> malf_lifespan_day
-> malf_service_day
-> audit
```

这意味着一旦当前 `MALF day` 输入变化，不是只补最后一层，而是整条 day 链一起重跑。

### 5.1 当前代码实际读取面

当前 day runtime 真实读取的是：

| 层 | 直接读取对象 | 当前读取面 |
|---|---|---|
| Core | `market_base_day.market_base_bar` | `symbol / bar_dt / high_px / low_px` |
| Lifespan | `market_base_day.market_base_bar` | `symbol / bar_dt` |
| Service | `malf_core_day` + `malf_lifespan_day` | 不再回读 Data |

因此当前 runtime 下，`high_px / low_px / bar_dt / symbol / timeframe` 或 day 行集变化，
都应按 `rerun` 处理。

### 5.2 合同面与 runtime 的观察项

当前合同仍把 `close_px` 列为 `MALF` official input required field 的一部分，但当前 day runtime
并不实际读取 `close_px`。

裁决：

- 这属于 `合同面 > 当前 runtime truth` 的观察项。
- 本口径以当前 runtime truth 作为重跑判断主依据。
- 该观察项本身不构成修合同或修代码授权。

### 5.3 `price_line / adj_mode` 的特殊性

当前 `MALF day` 查询没有显式按 `price_line / adj_mode` 过滤，但它们仍属于
`market_base_day` 的自然键维度。

裁决：

- 如果 `price_line / adj_mode` 的变化导致 day 行集变化，应按 `rerun` 处理。
- 如果它们的变化不改变当前 day 行集，可先判为 `no rerun`。

## 6. 不在本口径内的内容

以下内容不由本口径裁决：

- `MALF week/month` 是否施工
- `MALF v1.4 runtime sync` 是否打开
- 是否修改 `market_meta` 在架构图中的未来消费者表述
- 是否修正 `close_px` 的合同与代码差异
- 是否自动打开新的 `MALF` build card

当前 `MALF week/month` 仍是：

```text
not performed / 需另开卡
```

## 7. 证据锚点

- `governance/module_api_contracts/data.toml`
- `governance/module_api_contracts/malf.toml`
- `docs/02-modules/malf/03-runner-contract-v1.md`
- `docs/04-execution/records/malf/malf-v1-3-formal-rebuild-closeout-20260502-01.record.md`
- `src/asteria/malf/core_engine.py`
- `src/asteria/malf/lifespan_engine.py`
- `src/asteria/malf/bootstrap.py`
