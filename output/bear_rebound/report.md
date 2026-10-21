# 熊市反弹独立回测
截至2026-10-20；取数764/773；案例精确加载29/31。
现行评分公式未改。三规则×两环境×五退出，共30个固定方案，无收益最优自动选择。
价格为悠悠日K，成交量为全平台代理；次日收盘代理入场，仅卖出手续费1%，买入不收费，不考虑滑点。
最早第7日退出；动态退出按触发收盘成交，存在乐观执行假设。MAE按收盘价，不代表盘中最大回撤。
仅逐商品去重，不是资金组合净值；固定池有存活偏差。开发与2026事件诊断不冒充独立验证。
100根历史门槛为独立早期研究要求，不改生产300根门槛；缺日不补价，退出窗口要求真实报价和正成交量。
缺失历史求购、会员档位与Whale不倒填。组内未触发也保留；三个事件在±14日内诊断首次信号，不能当作自动事件发现。

| 规则 | 环境 | 退出 | 时段 | 信号/可评估 | 熊市n | 熊市净均值 | 熊市净中位 | 熊市胜率 | 熊市P10 |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| left_support | ungated | 7 | development_2025 | 1588/1081 | 229 | 6.67% | 0.30% | 50.66% | -9.34% |
| left_support | ungated | 7 | 2026_Q1 | 821/604 | 319 | 6.06% | 1.78% | 57.37% | -7.76% |
| left_support | ungated | 7 | 2026_Q2 | 1812/1525 | 1298 | -5.84% | -6.00% | 28.04% | -23.38% |
| left_support | ungated | 7 | 2026_Q3 | 1356/1075 | 1075 | -3.90% | -4.75% | 26.14% | -13.59% |
| left_support | ungated | 7 | recent90 | 1358/1050 | 1050 | -5.54% | -5.93% | 20.67% | -14.28% |
| left_support | ungated | 14 | development_2025 | 1441/667 | 74 | 0.41% | -4.58% | 29.73% | -14.68% |
| left_support | ungated | 14 | 2026_Q1 | 718/472 | 254 | 8.23% | 3.24% | 63.78% | -9.77% |
| left_support | ungated | 14 | 2026_Q2 | 1559/1039 | 901 | -10.14% | -11.53% | 15.09% | -25.10% |
| left_support | ungated | 14 | 2026_Q3 | 1119/776 | 776 | -6.68% | -7.04% | 20.10% | -18.40% |
| left_support | ungated | 14 | recent90 | 1125/787 | 787 | -7.98% | -8.18% | 16.77% | -19.24% |
| left_support | ungated | 30 | development_2025 | 1262/233 | 21 | -3.95% | -5.91% | 28.57% | -15.74% |
| left_support | ungated | 30 | 2026_Q1 | 571/303 | 191 | 26.42% | 14.39% | 79.06% | -8.07% |
| left_support | ungated | 30 | 2026_Q2 | 1265/728 | 596 | -9.41% | -14.80% | 20.97% | -35.05% |
| left_support | ungated | 30 | 2026_Q3 | 830/449 | 449 | -15.71% | -14.35% | 8.91% | -33.73% |
| left_support | ungated | 30 | recent90 | 916/466 | 466 | -16.56% | -14.94% | 7.73% | -34.63% |
| left_support | ungated | take15 | development_2025 | 1262/337 | 21 | -5.54% | -8.45% | 19.05% | -12.68% |
| left_support | ungated | take15 | 2026_Q1 | 571/338 | 191 | 12.62% | 16.27% | 76.96% | -11.13% |
| left_support | ungated | take15 | 2026_Q2 | 1265/816 | 661 | -11.48% | -13.06% | 13.92% | -31.51% |
| left_support | ungated | take15 | 2026_Q3 | 830/516 | 516 | -8.64% | -10.99% | 9.88% | -15.02% |
| left_support | ungated | take15 | recent90 | 916/466 | 466 | -9.17% | -10.97% | 8.37% | -14.80% |
| left_support | ungated | trail8 | development_2025 | 1262/372 | 21 | -3.41% | -7.59% | 23.81% | -9.48% |
| left_support | ungated | trail8 | 2026_Q1 | 571/339 | 191 | 11.40% | 4.21% | 67.54% | -9.05% |
| left_support | ungated | trail8 | 2026_Q2 | 1265/859 | 685 | -10.55% | -10.55% | 14.45% | -30.58% |
| left_support | ungated | trail8 | 2026_Q3 | 830/529 | 529 | -6.54% | -8.51% | 14.93% | -13.95% |
| left_support | ungated | trail8 | recent90 | 916/466 | 466 | -6.78% | -8.55% | 13.95% | -13.86% |
| left_support | local_repair | 7 | development_2025 | 1000/705 | 121 | 8.50% | 2.94% | 61.98% | -5.57% |
| left_support | local_repair | 7 | 2026_Q1 | 505/433 | 169 | 5.24% | 1.10% | 55.03% | -7.54% |
| left_support | local_repair | 7 | 2026_Q2 | 1481/1273 | 993 | -7.24% | -6.46% | 26.59% | -28.87% |
| left_support | local_repair | 7 | 2026_Q3 | 1002/762 | 762 | -4.27% | -4.77% | 25.85% | -14.02% |
| left_support | local_repair | 7 | recent90 | 1046/791 | 791 | -5.76% | -6.11% | 20.10% | -14.68% |
| left_support | local_repair | 14 | development_2025 | 949/414 | 20 | -7.50% | -6.18% | 10.00% | -17.19% |
| left_support | local_repair | 14 | 2026_Q1 | 448/343 | 131 | 4.35% | 0.43% | 51.91% | -11.97% |
| left_support | local_repair | 14 | 2026_Q2 | 1360/887 | 714 | -10.74% | -12.16% | 13.87% | -24.78% |
| left_support | local_repair | 14 | 2026_Q3 | 848/600 | 600 | -6.92% | -7.11% | 19.33% | -18.31% |
| left_support | local_repair | 14 | recent90 | 905/631 | 631 | -8.56% | -8.54% | 15.06% | -19.81% |
| left_support | local_repair | 30 | development_2025 | 862/171 | 9 | -5.86% | -4.87% | 33.33% | -16.01% |
| left_support | local_repair | 30 | 2026_Q1 | 369/224 | 107 | 26.68% | 8.51% | 66.36% | -14.84% |
| left_support | local_repair | 30 | 2026_Q2 | 1137/691 | 528 | -11.26% | -16.44% | 20.08% | -37.93% |
| left_support | local_repair | 30 | 2026_Q3 | 676/389 | 389 | -17.38% | -15.59% | 7.46% | -35.69% |
| left_support | local_repair | 30 | recent90 | 756/366 | 366 | -18.26% | -16.91% | 6.01% | -36.39% |
| left_support | local_repair | take15 | development_2025 | 862/246 | 9 | -6.49% | -8.45% | 22.22% | -12.55% |
| left_support | local_repair | take15 | 2026_Q1 | 369/265 | 107 | 7.88% | 11.00% | 63.55% | -12.86% |
| left_support | local_repair | take15 | 2026_Q2 | 1137/758 | 565 | -12.93% | -13.12% | 11.68% | -32.34% |
| left_support | local_repair | take15 | 2026_Q3 | 676/429 | 429 | -9.40% | -11.19% | 8.16% | -14.94% |
| left_support | local_repair | take15 | recent90 | 756/366 | 366 | -9.60% | -11.17% | 7.38% | -14.74% |
| left_support | local_repair | trail8 | development_2025 | 862/273 | 9 | -7.66% | -9.15% | 22.22% | -12.55% |
| left_support | local_repair | trail8 | 2026_Q1 | 369/266 | 107 | 7.84% | 0.47% | 51.40% | -9.52% |
| left_support | local_repair | trail8 | 2026_Q2 | 1137/794 | 586 | -11.77% | -10.76% | 12.46% | -31.82% |
| left_support | local_repair | trail8 | 2026_Q3 | 676/436 | 436 | -6.66% | -8.66% | 14.45% | -13.91% |
| left_support | local_repair | trail8 | recent90 | 756/366 | 366 | -6.77% | -8.67% | 14.48% | -13.86% |
| uniform_turn | ungated | 7 | development_2025 | 1688/1013 | 353 | 1.13% | -1.50% | 38.53% | -6.66% |
| uniform_turn | ungated | 7 | 2026_Q1 | 1166/1121 | 298 | 1.53% | -0.72% | 45.30% | -7.49% |
| uniform_turn | ungated | 7 | 2026_Q2 | 1053/926 | 897 | -0.74% | -2.57% | 40.58% | -18.96% |
| uniform_turn | ungated | 7 | 2026_Q3 | 1491/1279 | 1279 | -3.81% | -4.29% | 24.24% | -12.70% |
| uniform_turn | ungated | 7 | recent90 | 1528/1347 | 1347 | -4.65% | -5.31% | 20.94% | -13.24% |
| uniform_turn | ungated | 14 | development_2025 | 1487/550 | 161 | 0.08% | -3.30% | 34.16% | -9.60% |
| uniform_turn | ungated | 14 | 2026_Q1 | 970/880 | 248 | 3.13% | -0.03% | 49.60% | -8.70% |
| uniform_turn | ungated | 14 | 2026_Q2 | 899/755 | 736 | -3.70% | -7.82% | 28.26% | -19.11% |
| uniform_turn | ungated | 14 | 2026_Q3 | 1243/968 | 968 | -6.00% | -6.11% | 16.94% | -15.35% |
| uniform_turn | ungated | 14 | recent90 | 1276/970 | 970 | -7.19% | -7.28% | 14.64% | -17.95% |
| uniform_turn | ungated | 30 | development_2025 | 1318/258 | 48 | -4.96% | -4.70% | 25.00% | -17.23% |
| uniform_turn | ungated | 30 | 2026_Q1 | 686/410 | 184 | 11.55% | 5.04% | 71.20% | -10.48% |
| uniform_turn | ungated | 30 | 2026_Q2 | 733/574 | 564 | -11.87% | -13.01% | 27.13% | -41.52% |
| uniform_turn | ungated | 30 | 2026_Q3 | 976/644 | 644 | -11.86% | -11.53% | 8.54% | -24.29% |
| uniform_turn | ungated | 30 | recent90 | 977/574 | 574 | -12.35% | -11.39% | 8.19% | -26.23% |
| uniform_turn | ungated | take15 | development_2025 | 1318/290 | 48 | -3.30% | -6.45% | 25.00% | -12.06% |
| uniform_turn | ungated | take15 | 2026_Q1 | 686/550 | 184 | 7.35% | 4.45% | 65.22% | -10.87% |
| uniform_turn | ungated | take15 | 2026_Q2 | 733/595 | 584 | -4.26% | -11.10% | 27.91% | -20.13% |
| uniform_turn | ungated | take15 | 2026_Q3 | 976/730 | 730 | -8.64% | -10.66% | 8.08% | -13.68% |
| uniform_turn | ungated | take15 | recent90 | 977/574 | 574 | -8.66% | -10.63% | 7.67% | -13.67% |
| uniform_turn | ungated | trail8 | development_2025 | 1318/301 | 48 | -3.77% | -5.86% | 14.58% | -9.91% |
| uniform_turn | ungated | trail8 | 2026_Q1 | 686/581 | 184 | 4.54% | 1.96% | 55.98% | -9.74% |
| uniform_turn | ungated | trail8 | 2026_Q2 | 733/606 | 595 | -3.20% | -7.96% | 30.42% | -18.95% |
| uniform_turn | ungated | trail8 | 2026_Q3 | 976/748 | 748 | -6.70% | -8.97% | 14.30% | -12.37% |
| uniform_turn | ungated | trail8 | recent90 | 977/574 | 574 | -6.96% | -9.00% | 13.94% | -12.54% |
| uniform_turn | local_repair | 7 | development_2025 | 1194/693 | 214 | 1.47% | -0.86% | 43.93% | -5.65% |
| uniform_turn | local_repair | 7 | 2026_Q1 | 882/850 | 224 | 2.14% | -0.04% | 49.55% | -6.05% |
| uniform_turn | local_repair | 7 | 2026_Q2 | 845/777 | 762 | -0.43% | -2.10% | 42.52% | -19.56% |
| uniform_turn | local_repair | 7 | 2026_Q3 | 1113/954 | 954 | -4.22% | -4.63% | 25.05% | -13.59% |
| uniform_turn | local_repair | 7 | recent90 | 1211/1057 | 1057 | -4.99% | -5.55% | 20.91% | -13.91% |
| uniform_turn | local_repair | 14 | development_2025 | 1087/348 | 69 | -3.70% | -3.93% | 27.54% | -10.56% |
| uniform_turn | local_repair | 14 | 2026_Q1 | 756/713 | 187 | 2.19% | -0.19% | 48.66% | -8.13% |
| uniform_turn | local_repair | 14 | 2026_Q2 | 733/646 | 637 | -3.03% | -7.66% | 29.36% | -17.97% |
| uniform_turn | local_repair | 14 | 2026_Q3 | 950/770 | 770 | -6.00% | -5.74% | 18.18% | -15.98% |
| uniform_turn | local_repair | 14 | recent90 | 1032/763 | 763 | -7.07% | -7.10% | 16.12% | -18.45% |
| uniform_turn | local_repair | 30 | development_2025 | 1034/197 | 29 | -7.41% | -5.63% | 17.24% | -18.45% |
| uniform_turn | local_repair | 30 | 2026_Q1 | 562/357 | 141 | 10.45% | 4.37% | 66.67% | -10.14% |
| uniform_turn | local_repair | 30 | 2026_Q2 | 619/533 | 524 | -12.08% | -12.01% | 28.44% | -42.17% |
| uniform_turn | local_repair | 30 | 2026_Q3 | 779/558 | 558 | -12.20% | -11.57% | 7.53% | -24.92% |
| uniform_turn | local_repair | 30 | recent90 | 831/481 | 481 | -12.64% | -11.66% | 8.11% | -26.68% |
| uniform_turn | local_repair | take15 | development_2025 | 1034/222 | 29 | -5.92% | -10.13% | 17.24% | -13.08% |
| uniform_turn | local_repair | take15 | 2026_Q1 | 562/459 | 141 | 6.79% | 3.49% | 59.57% | -11.08% |
| uniform_turn | local_repair | take15 | 2026_Q2 | 619/541 | 532 | -3.68% | -11.08% | 29.32% | -19.66% |
| uniform_turn | local_repair | take15 | 2026_Q3 | 779/624 | 624 | -9.20% | -10.73% | 7.37% | -13.99% |
| uniform_turn | local_repair | take15 | recent90 | 831/481 | 481 | -9.06% | -10.79% | 8.32% | -14.57% |
| uniform_turn | local_repair | trail8 | development_2025 | 1034/233 | 29 | -5.47% | -8.93% | 10.34% | -11.36% |
| uniform_turn | local_repair | trail8 | 2026_Q1 | 562/482 | 141 | 3.58% | -0.44% | 48.94% | -9.78% |
| uniform_turn | local_repair | trail8 | 2026_Q2 | 619/546 | 537 | -2.48% | -7.97% | 32.40% | -18.13% |
| uniform_turn | local_repair | trail8 | 2026_Q3 | 779/630 | 630 | -7.14% | -8.99% | 13.97% | -12.93% |
| uniform_turn | local_repair | trail8 | recent90 | 831/481 | 481 | -7.24% | -9.01% | 14.76% | -13.44% |
| first_pullback | ungated | 7 | development_2025 | 200/115 | 59 | -1.06% | -2.47% | 28.81% | -6.28% |
| first_pullback | ungated | 7 | 2026_Q1 | 238/189 | 122 | 2.48% | -0.43% | 42.62% | -6.30% |
| first_pullback | ungated | 7 | 2026_Q2 | 234/219 | 214 | -2.50% | -3.69% | 28.97% | -13.51% |
| first_pullback | ungated | 7 | 2026_Q3 | 389/359 | 359 | -3.83% | -3.64% | 14.21% | -10.00% |
| first_pullback | ungated | 7 | recent90 | 387/325 | 325 | -4.23% | -4.13% | 13.54% | -10.52% |
| first_pullback | ungated | 14 | development_2025 | 199/74 | 40 | -0.56% | -2.25% | 30.00% | -9.68% |
| first_pullback | ungated | 14 | 2026_Q1 | 228/167 | 111 | 5.81% | 1.34% | 58.56% | -7.45% |
| first_pullback | ungated | 14 | 2026_Q2 | 230/182 | 178 | -6.43% | -6.28% | 25.84% | -24.67% |
| first_pullback | ungated | 14 | 2026_Q3 | 373/311 | 311 | -6.60% | -5.86% | 11.25% | -15.38% |
| first_pullback | ungated | 14 | recent90 | 371/291 | 291 | -7.04% | -6.21% | 10.31% | -15.85% |
| first_pullback | ungated | 30 | development_2025 | 199/14 | 0 | — | — | — | — |
| first_pullback | ungated | 30 | 2026_Q1 | 204/127 | 83 | 16.08% | 7.05% | 79.52% | -8.66% |
| first_pullback | ungated | 30 | 2026_Q2 | 219/105 | 103 | -5.82% | -13.02% | 24.27% | -37.55% |
| first_pullback | ungated | 30 | 2026_Q3 | 334/162 | 162 | -11.97% | -9.82% | 8.02% | -26.40% |
| first_pullback | ungated | 30 | recent90 | 336/233 | 233 | -14.07% | -13.63% | 6.01% | -27.49% |
| first_pullback | ungated | take15 | development_2025 | 199/14 | 0 | — | — | — | — |
| first_pullback | ungated | take15 | 2026_Q1 | 204/136 | 83 | 8.21% | 7.13% | 73.49% | -10.72% |
| first_pullback | ungated | take15 | 2026_Q2 | 219/132 | 130 | -8.20% | -11.65% | 15.38% | -20.45% |
| first_pullback | ungated | take15 | 2026_Q3 | 334/216 | 216 | -9.00% | -10.48% | 5.56% | -13.11% |
| first_pullback | ungated | take15 | recent90 | 336/233 | 233 | -9.14% | -10.60% | 6.01% | -13.21% |
| first_pullback | ungated | trail8 | development_2025 | 199/14 | 0 | — | — | — | — |
| first_pullback | ungated | trail8 | 2026_Q1 | 204/134 | 83 | 7.17% | 3.72% | 61.45% | -9.53% |
| first_pullback | ungated | trail8 | 2026_Q2 | 219/136 | 134 | -5.64% | -9.93% | 16.42% | -17.92% |
| first_pullback | ungated | trail8 | 2026_Q3 | 334/237 | 237 | -7.53% | -8.98% | 7.59% | -11.58% |
| first_pullback | ungated | trail8 | recent90 | 336/233 | 233 | -7.87% | -9.14% | 7.30% | -11.50% |
| first_pullback | local_repair | 7 | development_2025 | 46/20 | 11 | -1.17% | -2.59% | 36.36% | -5.24% |
| first_pullback | local_repair | 7 | 2026_Q1 | 51/49 | 19 | 4.56% | 2.05% | 68.42% | -2.87% |
| first_pullback | local_repair | 7 | 2026_Q2 | 53/50 | 47 | 1.77% | -0.89% | 46.81% | -17.76% |
| first_pullback | local_repair | 7 | 2026_Q3 | 115/103 | 103 | -4.28% | -3.56% | 15.53% | -11.13% |
| first_pullback | local_repair | 7 | recent90 | 142/102 | 102 | -4.80% | -4.58% | 14.71% | -11.45% |
| first_pullback | local_repair | 14 | development_2025 | 46/13 | 7 | -1.83% | -4.05% | 42.86% | -5.66% |
| first_pullback | local_repair | 14 | 2026_Q1 | 50/46 | 17 | 5.98% | 2.41% | 64.71% | -5.74% |
| first_pullback | local_repair | 14 | 2026_Q2 | 52/24 | 22 | -5.27% | -8.27% | 31.82% | -25.83% |
| first_pullback | local_repair | 14 | 2026_Q3 | 114/99 | 99 | -6.44% | -5.03% | 12.12% | -15.48% |
| first_pullback | local_repair | 14 | recent90 | 140/93 | 93 | -7.30% | -5.86% | 11.83% | -19.22% |
| first_pullback | local_repair | 30 | development_2025 | 46/2 | 0 | — | — | — | — |
| first_pullback | local_repair | 30 | 2026_Q1 | 50/36 | 17 | 21.29% | 10.98% | 82.35% | -1.28% |
| first_pullback | local_repair | 30 | 2026_Q2 | 51/22 | 20 | -11.69% | -18.93% | 25.00% | -43.53% |
| first_pullback | local_repair | 30 | 2026_Q3 | 110/81 | 81 | -12.52% | -11.13% | 7.41% | -24.34% |
| first_pullback | local_repair | 30 | recent90 | 136/69 | 69 | -14.08% | -13.11% | 7.25% | -30.10% |
| first_pullback | local_repair | take15 | development_2025 | 46/2 | 0 | — | — | — | — |
| first_pullback | local_repair | take15 | 2026_Q1 | 50/44 | 17 | 10.35% | 15.89% | 76.47% | -4.97% |
| first_pullback | local_repair | take15 | 2026_Q2 | 51/33 | 31 | -3.40% | -11.13% | 22.58% | -19.08% |
| first_pullback | local_repair | take15 | 2026_Q3 | 110/87 | 87 | -9.80% | -10.62% | 4.60% | -13.51% |
| first_pullback | local_repair | take15 | recent90 | 136/69 | 69 | -10.10% | -10.90% | 5.80% | -14.20% |
| first_pullback | local_repair | trail8 | development_2025 | 46/2 | 0 | — | — | — | — |
| first_pullback | local_repair | trail8 | 2026_Q1 | 50/44 | 17 | 13.40% | 3.00% | 64.71% | -6.72% |
| first_pullback | local_repair | trail8 | 2026_Q2 | 51/33 | 31 | -7.63% | -10.18% | 19.35% | -19.08% |
| first_pullback | local_repair | trail8 | 2026_Q3 | 110/87 | 87 | -7.30% | -8.96% | 11.49% | -11.68% |
| first_pullback | local_repair | trail8 | recent90 | 136/69 | 69 | -7.45% | -9.25% | 14.49% | -12.24% |

## 案例覆盖缺口
- ★ Sport Gloves | Hedge Maze (Minimal Wear)：mapped=False, loaded=False, event_close=False
- ★ Sport Gloves | Pandora's Box (Minimal Wear)：mapped=False, loaded=False, event_close=False

完整逐笔、案例触发及覆盖见同目录文件；未通过系统验证，不输出正式买入资格。
