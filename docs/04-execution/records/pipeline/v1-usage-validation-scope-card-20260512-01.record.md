# V1 Usage Validation Scope Record

日期：2026-05-12

## 1. 卡信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `v1-usage-validation-scope-card-20260512-01` |
| result | `passed / scope frozen / roadmap-only route` |

## 2. 执行内容

1. 重读 Asteria live authority，确认 `final-release-closeout-card` 已通过且当前 live next 仍为 `none / terminal`。
2. 复核 `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md`，确认本卡是 post-terminal 只读路线卡，不改 live gate。
3. 新增只读 scope freeze 实现与 CLI，读取 `market_meta.duckdb` 的 `industry_classification / instrument_master` 与 `market_base_day.duckdb` 的 `market_base_bar`。
4. 以 `2024-01-02..2024-12-31` 为窗口，对 `sw2021_level3_snapshot` 归并出的 31 个申万一级行业执行“覆盖完整度优先、平均 amount 次优先”的代表股冻结。
5. 生成 `scope-manifest.json` 与 `closeout.md`，并把 freeze 结果归档到 repo 四件套、`H:\Asteria-report` 与 `H:\Asteria-Validated`。

## 3. Freeze Result

| 项 | 值 |
|---|---|
| live next preserved | `yes` |
| current live next | `none / terminal` |
| next route card | `v1-application-db-readiness-audit-card` |
| level1 industry count | `31` |
| selected symbol count | `31` |
| trading days in window | `242` |
| manual override used | `no` |

## 4. 31 行业冻结结果

| 一级行业 | 代表股 | 2024 覆盖天数 | 平均 amount（亿元） |
|---|---|---:|---:|
| 交通运输 | `000099.SZ` | 242 | 16.17 |
| 传媒 | `300418.SZ` | 242 | 23.85 |
| 公用事业 | `600900.SH` | 242 | 25.00 |
| 农林牧渔 | `002714.SZ` | 242 | 11.76 |
| 医药生物 | `603259.SH` | 242 | 31.06 |
| 商贸零售 | `601888.SH` | 242 | 16.85 |
| 国防军工 | `002625.SZ` | 242 | 13.40 |
| 基础化工 | `600309.SH` | 242 | 12.20 |
| 家用电器 | `600839.SH` | 242 | 23.16 |
| 建筑材料 | `002271.SZ` | 242 | 7.61 |
| 建筑装饰 | `000628.SZ` | 242 | 17.85 |
| 房地产 | `000002.SZ` | 242 | 16.80 |
| 有色金属 | `601899.SH` | 242 | 27.25 |
| 机械设备 | `001696.SZ` | 242 | 17.79 |
| 汽车 | `601127.SH` | 242 | 48.47 |
| 煤炭 | `601088.SH` | 242 | 11.56 |
| 环保 | `300210.SZ` | 242 | 3.44 |
| 电力设备 | `300750.SZ` | 242 | 53.18 |
| 电子 | `601138.SH` | 242 | 36.02 |
| 石油石化 | `601857.SH` | 242 | 17.48 |
| 社会服务 | `002261.SZ` | 242 | 15.92 |
| 纺织服饰 | `600630.SH` | 242 | 4.78 |
| 综合 | `002175.SZ` | 242 | 2.73 |
| 美容护理 | `300896.SZ` | 242 | 8.05 |
| 计算机 | `603019.SH` | 242 | 37.24 |
| 轻工制造 | `002229.SZ` | 242 | 10.14 |
| 通信 | `300308.SZ` | 242 | 41.18 |
| 钢铁 | `600010.SH` | 242 | 5.86 |
| 银行 | `600036.SH` | 242 | 23.84 |
| 非银金融 | `300059.SZ` | 242 | 86.80 |
| 食品饮料 | `600519.SH` | 242 | 52.86 |

## 5. 边界与 caveat

| 项 | 裁决 |
|---|---|
| 正式 DB mutation | `not executed` |
| ST / 停牌 / 上市退市 | `retained source gap; not claimed as formally covered` |
| 历史行业沿革 | `not opened` |
| appendix 策略 | `仅从冻结 31 只中挑少量样例，不扩成 31 份逐股册` |

## 6. 验收口径

本卡的完成只代表：使用验证的范围已经冻结，后续读库审计和人读报告不需要再重新决定
股票池、时间窗和研究问题。它不代表：

- Asteria 主线重新打开；
- live next card 被改写；
- 正式 Data gap 被修复；
- 日更生产化已经放行。
