# 已知龙头形态学习：开发拟合与事件留一
截至2026-10-20；加载766/775；特征78项；复杂度15叶。
**本报告是回溯开发研究，不是历史上可交易的独立验证。**
人工案例身份仅用来构建训练标签，绝不作为模型输入；同时剔除尚未完成后续结果的训练样本。
正例要求已知案例当日之后仍有>=15%拉升潜力且14日净收益为正；同日失败商品作负例，未标注的赢家不强行当成负例。
轮流拿掉整段2月/5月/8月行情，用其余两段训练再排序该段；早期留一可能使用较晚事件，须与按时间滚动v3明确分开。
另列known_case_apparent_fit，直接反映开发模型能否记住这些形态；其效果不能当作样本外成绩。
±7日最佳名次为事后诊断，首次前30及其后收益同时保留。卖出1%、买入0、零滑点。

| 事件 | 方法 | 可评估 | ±7日前30覆盖 |
|---|---|---:|---:|
| 2026-02-09 | event_holdout_retrospective | 24/24 | 0 |
| 2026-02-09 | known_case_apparent_fit | 24/24 | 24 |
| 2026-05-27 | event_holdout_retrospective | 4/4 | 0 |
| 2026-05-27 | known_case_apparent_fit | 4/4 | 4 |
| 2026-08-22 | event_holdout_retrospective | 3/3 | 0 |
| 2026-08-22 | known_case_apparent_fit | 3/3 | 3 |

## 三段行情同方向的描述性特征
这些是已选案例与失败对照的分布差异，不是因果证明；没有同方向特征时不强行宣称手法一致。
| 特征 | 成功案例相对对照 | 三事件最小差异/IQR |
|---|---|---:|
| peer_momentum_21 | lower | 0.753 |
| peer_relative_7 | higher | 0.287 |
| peer_relative_14 | higher | 0.245 |
| peer_relative_3 | higher | 0.240 |
| volatility_10_percentile | higher | 0.188 |
| relative_7 | higher | 0.187 |
| early_vol_cv | higher | 0.175 |
| peer_momentum_7 | lower | 0.170 |
| relative_3 | higher | 0.169 |
| early_range | higher | 0.166 |
| relative_14 | higher | 0.112 |
| recent_volume_step | higher | 0.090 |
| peer_momentum_14 | lower | 0.043 |
| volatility_5 | higher | 0.036 |

## 研究边界
- 事件留一使用其他事件的训练标签；早期事件可能学到后期事件，属于回溯机制研究，不是当时可执行收益
- 模型复杂度也按这三个事件的平均AP选择，事件留一结果已参与开发，不能宣称最终独立测试
- 同一事件日共享市场变量，样本相关；案例数据有选择偏差
- known_case_apparent_fit是训练案例拟合效果，不代表泛化
- current_candidates只作新数据的前瞻研究记录；未完成独立事件验证

完整首次入榜见case_windows.csv；解释路径见case_feature_paths.csv.gz；所有同榜误报保留在逐日排名文件中。
