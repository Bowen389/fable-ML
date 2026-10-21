# 时序阶段反弹龙头研究 v3
截至2026-10-20，加载766/775件，输入78项。现行评分未改。
成本：买入0、卖出1%、滑点0。次日收盘代理入场，真实日K不保证可成交。
新增蓄势（此前21至60日）、中段量价台阶（此前7至21日）、洗盘（此前2至7日）、当前放量的相对顺序；全平台量与悠悠价格分别使用。承接及会员建仓仍为代理。
比较未来7日涨幅前30目标，以及未来第7至21日收盘最大净涨幅至少15%且前30的潜力目标；后者是事后标签，绝非保证可在峰值卖出。实际收益仍列固定7/14日结果。
三个固定模型按季度训练，120日校准，22日标签隔离；近期模型只训练校准日前540日。跨目标按校准AP相对基准率的提升选择，不查看点名案例或预测季度结果选模。
人工案例只用于回放诊断，不输入身份、不加商品奖金。经过多轮已看历史结果，不能把2026年称为完全未见事件。
±7日最优名次仅是事后窗口诊断；首次入榜日期、与锚点价格差、入榜后固定收益同时保留，避免只展示涨后好看的日期。
每日商品日信号重叠，不是独立交易或组合收益。退出收益缺失按缺失保留。还没有通过完整买入验证的系统。

| 时段 | 环境 | 模型 | 前K | 结果n | 14日净均值 | 胜率 | 潜力龙头召回 |
|---|---|---|---:|---:|---:|---:|
| Q1 | all | stage7_global | 10 | 706 | 22.01% | 69.69% | 4.74% |
| Q1 | all | stage7_global | 30 | 2175 | 21.84% | 69.52% | 15.41% |
| Q1 | all | stage21_global | 10 | 765 | 23.62% | 68.50% | 7.22% |
| Q1 | all | stage21_global | 30 | 2320 | 21.71% | 67.28% | 18.15% |
| Q1 | all | stage21_recent | 10 | 769 | 17.63% | 67.49% | 5.04% |
| Q1 | all | stage21_recent | 30 | 2289 | 19.82% | 68.81% | 15.26% |
| Q1 | all | selected | 10 | 769 | 17.63% | 67.49% | 5.04% |
| Q1 | all | selected | 30 | 2289 | 19.82% | 68.81% | 15.26% |
| Q1 | bear | stage7_global | 10 | 237 | 18.61% | 68.78% | 4.33% |
| Q1 | bear | stage7_global | 30 | 708 | 21.39% | 70.06% | 16.44% |
| Q1 | bear | stage21_global | 10 | 239 | 15.15% | 59.83% | 5.00% |
| Q1 | bear | stage21_global | 30 | 742 | 18.68% | 64.82% | 16.89% |
| Q1 | bear | stage21_recent | 10 | 254 | 20.13% | 71.65% | 6.33% |
| Q1 | bear | stage21_recent | 30 | 767 | 22.11% | 72.75% | 18.78% |
| Q1 | bear | selected | 10 | 254 | 20.13% | 71.65% | 6.33% |
| Q1 | bear | selected | 30 | 767 | 22.11% | 72.75% | 18.78% |
| Q1 | repair | stage7_global | 10 | 315 | 23.53% | 71.43% | 5.20% |
| Q1 | repair | stage7_global | 30 | 971 | 22.93% | 70.75% | 15.45% |
| Q1 | repair | stage21_global | 10 | 338 | 25.90% | 70.41% | 7.24% |
| Q1 | repair | stage21_global | 30 | 1045 | 23.43% | 69.95% | 19.11% |
| Q1 | repair | stage21_recent | 10 | 331 | 18.99% | 68.88% | 4.96% |
| Q1 | repair | stage21_recent | 30 | 997 | 20.86% | 70.21% | 15.69% |
| Q1 | repair | selected | 10 | 331 | 18.99% | 68.88% | 4.96% |
| Q1 | repair | selected | 30 | 997 | 20.86% | 70.21% | 15.69% |
| Q2 | all | stage7_global | 10 | 745 | 0.67% | 44.56% | 4.14% |
| Q2 | all | stage7_global | 30 | 2215 | 1.85% | 45.42% | 13.49% |
| Q2 | all | stage21_global | 10 | 730 | 0.01% | 42.74% | 4.03% |
| Q2 | all | stage21_global | 30 | 2204 | 0.37% | 42.83% | 12.56% |
| Q2 | all | stage21_recent | 10 | 685 | 6.12% | 50.80% | 5.44% |
| Q2 | all | stage21_recent | 30 | 2142 | 4.22% | 48.09% | 14.01% |
| Q2 | all | selected | 10 | 730 | 0.01% | 42.74% | 4.03% |
| Q2 | all | selected | 30 | 2204 | 0.37% | 42.83% | 12.56% |
| Q2 | bear | stage7_global | 10 | 667 | -0.21% | 42.13% | 4.05% |
| Q2 | bear | stage7_global | 30 | 1955 | 1.11% | 43.02% | 13.56% |
| Q2 | bear | stage21_global | 10 | 644 | -0.61% | 40.37% | 4.09% |
| Q2 | bear | stage21_global | 30 | 1934 | -0.59% | 40.74% | 12.10% |
| Q2 | bear | stage21_recent | 10 | 586 | 5.49% | 49.83% | 5.29% |
| Q2 | bear | stage21_recent | 30 | 1834 | 3.06% | 45.69% | 13.39% |
| Q2 | bear | selected | 10 | 644 | -0.61% | 40.37% | 4.09% |
| Q2 | bear | selected | 30 | 1934 | -0.59% | 40.74% | 12.10% |
| Q2 | repair | stage7_global | 10 | 277 | -3.72% | 39.71% | 3.53% |
| Q2 | repair | stage7_global | 30 | 846 | -2.36% | 41.02% | 12.16% |
| Q2 | repair | stage21_global | 10 | 264 | -3.70% | 37.50% | 3.24% |
| Q2 | repair | stage21_global | 30 | 832 | -4.94% | 35.46% | 9.71% |
| Q2 | repair | stage21_recent | 10 | 257 | -0.19% | 40.47% | 3.92% |
| Q2 | repair | stage21_recent | 30 | 829 | -0.66% | 39.45% | 11.27% |
| Q2 | repair | selected | 10 | 264 | -3.70% | 37.50% | 3.24% |
| Q2 | repair | selected | 30 | 832 | -4.94% | 35.46% | 9.71% |
| Q3 | all | stage7_global | 10 | 577 | -7.43% | 23.92% | 3.37% |
| Q3 | all | stage7_global | 30 | 1715 | -8.28% | 22.16% | 9.62% |
| Q3 | all | stage21_global | 10 | 474 | -6.13% | 27.64% | 4.68% |
| Q3 | all | stage21_global | 30 | 1601 | -8.02% | 23.92% | 12.79% |
| Q3 | all | stage21_recent | 10 | 512 | -5.76% | 29.30% | 5.49% |
| Q3 | all | stage21_recent | 30 | 1635 | -6.22% | 27.40% | 15.76% |
| Q3 | all | selected | 10 | 474 | -6.13% | 27.64% | 4.68% |
| Q3 | all | selected | 30 | 1601 | -8.02% | 23.92% | 12.79% |
| Q3 | bear | stage7_global | 10 | 577 | -7.43% | 23.92% | 3.37% |
| Q3 | bear | stage7_global | 30 | 1715 | -8.28% | 22.16% | 9.62% |
| Q3 | bear | stage21_global | 10 | 474 | -6.13% | 27.64% | 4.68% |
| Q3 | bear | stage21_global | 30 | 1601 | -8.02% | 23.92% | 12.79% |
| Q3 | bear | stage21_recent | 10 | 512 | -5.76% | 29.30% | 5.49% |
| Q3 | bear | stage21_recent | 30 | 1635 | -6.22% | 27.40% | 15.76% |
| Q3 | bear | selected | 10 | 474 | -6.13% | 27.64% | 4.68% |
| Q3 | bear | selected | 30 | 1601 | -8.02% | 23.92% | 12.79% |
| Q3 | repair | stage7_global | 10 | 180 | -7.74% | 20.56% | 4.58% |
| Q3 | repair | stage7_global | 30 | 548 | -8.24% | 19.53% | 11.69% |
| Q3 | repair | stage21_global | 10 | 144 | -7.49% | 27.08% | 4.74% |
| Q3 | repair | stage21_global | 30 | 514 | -9.71% | 20.82% | 11.69% |
| Q3 | repair | stage21_recent | 10 | 181 | -8.42% | 25.97% | 5.53% |
| Q3 | repair | stage21_recent | 30 | 565 | -7.60% | 24.07% | 16.59% |
| Q3 | repair | selected | 10 | 144 | -7.49% | 27.08% | 4.74% |
| Q3 | repair | selected | 30 | 514 | -9.71% | 20.82% | 11.69% |
| Q4_partial | all | stage7_global | 10 | 32 | -12.29% | 12.50% | — |
| Q4_partial | all | stage7_global | 30 | 98 | -12.21% | 12.24% | — |
| Q4_partial | all | stage21_global | 10 | 31 | -11.95% | 16.13% | — |
| Q4_partial | all | stage21_global | 30 | 87 | -12.22% | 12.64% | — |
| Q4_partial | all | stage21_recent | 10 | 30 | -0.08% | 30.00% | — |
| Q4_partial | all | stage21_recent | 30 | 87 | -3.01% | 28.74% | — |
| Q4_partial | all | selected | 10 | 30 | -0.08% | 30.00% | — |
| Q4_partial | all | selected | 30 | 87 | -3.01% | 28.74% | — |
| Q4_partial | bear | stage7_global | 10 | 32 | -12.29% | 12.50% | — |
| Q4_partial | bear | stage7_global | 30 | 98 | -12.21% | 12.24% | — |
| Q4_partial | bear | stage21_global | 10 | 31 | -11.95% | 16.13% | — |
| Q4_partial | bear | stage21_global | 30 | 87 | -12.22% | 12.64% | — |
| Q4_partial | bear | stage21_recent | 10 | 30 | -0.08% | 30.00% | — |
| Q4_partial | bear | stage21_recent | 30 | 87 | -3.01% | 28.74% | — |
| Q4_partial | bear | selected | 10 | 30 | -0.08% | 30.00% | — |
| Q4_partial | bear | selected | 30 | 87 | -3.01% | 28.74% | — |
| Q4_partial | repair | stage7_global | 10 | 21 | -9.41% | 14.29% | — |
| Q4_partial | repair | stage7_global | 30 | 58 | -9.54% | 17.24% | — |
| Q4_partial | repair | stage21_global | 10 | 18 | -9.33% | 27.78% | — |
| Q4_partial | repair | stage21_global | 30 | 52 | -9.65% | 17.31% | — |
| Q4_partial | repair | stage21_recent | 10 | 18 | 1.47% | 38.89% | — |
| Q4_partial | repair | stage21_recent | 30 | 50 | 2.48% | 40.00% | — |
| Q4_partial | repair | selected | 10 | 18 | 1.47% | 38.89% | — |
| Q4_partial | repair | selected | 30 | 50 | 2.48% | 40.00% | — |

## 指定案例±7日覆盖
| 日期 | 模型 | 可评估/该事件案例数 | 前30覆盖 |
|---|---|---:|---:|
| 2026-02-09 | stage7_global | 24/24 | 0 |
| 2026-02-09 | stage21_global | 24/24 | 0 |
| 2026-02-09 | stage21_recent | 24/24 | 0 |
| 2026-02-09 | selected | 24/24 | 0 |
| 2026-05-27 | stage7_global | 4/4 | 1 |
| 2026-05-27 | stage21_global | 4/4 | 0 |
| 2026-05-27 | stage21_recent | 4/4 | 0 |
| 2026-05-27 | selected | 4/4 | 0 |
| 2026-08-22 | stage7_global | 3/3 | 0 |
| 2026-08-22 | stage21_global | 3/3 | 0 |
| 2026-08-22 | stage21_recent | 3/3 | 0 |
| 2026-08-22 | selected | 3/3 | 0 |

逐日名次见case_daily.csv，首次入榜及最佳日期见case_windows.csv；当前研究候选不等于买入推荐。
精确磨损补采：[{"name": "★ Sport Gloves | Hedge Maze (Minimal Wear)", "resolved_id": "640174305739308770", "status": "exact_match"}, {"name": "★ Sport Gloves | Pandora's Box (Minimal Wear)", "resolved_id": "8244171592052627335", "status": "exact_match"}]
