# 去除行情与价格档位的形态迁移实验
截至2026-10-20；加载766/775；按开发目标选中shape_template。
**这是回溯开发实验；事件留一可能使用较晚行情，且选模使用了这些结果，不是历史可执行或最终独立验证。**
四组对照：全背景控制；去除绝对价格、绝对量、手套/探员类别、大盘背景和同类整体动量；进一步按自身历史波动与前期区间标准化；标准化形态的正负案例近邻模板。
人工案例身份只构造训练标签，不输入模型。所有单日特征不使用该日之后数据。
选模按三事件最差前30覆盖、平均事件覆盖、AP依次比较，不能对每件商品事后换一个模型。
模板以训练样本拟合缺失值和缩放，仅用训练负例确定固定随机子样本；分数不是概率。
成本为买入0、卖出1%、零滑点。±7日最好名次是事后诊断，首次入榜日期和后续收益同时保留。

| 事件 | 模型 | 方法 | 可评估 | 前30覆盖 |
|---|---|---|---:|---:|
| 2026-02-09 | full_context_control | event_holdout | 24/24 | 0 |
| 2026-02-09 | full_context_control | apparent_fit | 24/24 | 24 |
| 2026-02-09 | shape_only | event_holdout | 24/24 | 1 |
| 2026-02-09 | shape_only | apparent_fit | 24/24 | 23 |
| 2026-02-09 | volatility_scaled | event_holdout | 24/24 | 1 |
| 2026-02-09 | volatility_scaled | apparent_fit | 24/24 | 24 |
| 2026-02-09 | shape_template | event_holdout | 24/24 | 2 |
| 2026-02-09 | shape_template | apparent_fit | 24/24 | 23 |
| 2026-05-27 | full_context_control | event_holdout | 4/4 | 0 |
| 2026-05-27 | full_context_control | apparent_fit | 4/4 | 4 |
| 2026-05-27 | shape_only | event_holdout | 4/4 | 0 |
| 2026-05-27 | shape_only | apparent_fit | 4/4 | 4 |
| 2026-05-27 | volatility_scaled | event_holdout | 4/4 | 0 |
| 2026-05-27 | volatility_scaled | apparent_fit | 4/4 | 4 |
| 2026-05-27 | shape_template | event_holdout | 4/4 | 1 |
| 2026-05-27 | shape_template | apparent_fit | 4/4 | 4 |
| 2026-08-22 | full_context_control | event_holdout | 3/3 | 0 |
| 2026-08-22 | full_context_control | apparent_fit | 3/3 | 3 |
| 2026-08-22 | shape_only | event_holdout | 3/3 | 0 |
| 2026-08-22 | shape_only | apparent_fit | 3/3 | 3 |
| 2026-08-22 | volatility_scaled | event_holdout | 3/3 | 3 |
| 2026-08-22 | volatility_scaled | apparent_fit | 3/3 | 3 |
| 2026-08-22 | shape_template | event_holdout | 3/3 | 3 |
| 2026-08-22 | shape_template | apparent_fit | 3/3 | 3 |

训练拟合覆盖不代表泛化；跨事件有改善也仍需冻结后的独立行情验证。生产评分保持不变。
