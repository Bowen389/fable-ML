# 熊市反弹独立回测
截至2026-10-20；取数764/773；案例精确加载29/31。
现行评分公式未改。三规则×两环境×五退出，共30个固定方案，无收益最优自动选择。
价格为悠悠日K，成交量为全平台代理；次日收盘代理入场，手续费2.5%，双边各0.5%滑点。
最早第7日退出；动态退出按触发收盘成交，存在乐观执行假设。MAE按收盘价，不代表盘中最大回撤。
仅逐商品去重，不是资金组合净值；固定池有存活偏差。开发与2026事件诊断不冒充独立验证。
100根历史门槛为独立早期研究要求，不改生产300根门槛；缺日不补价，退出窗口要求真实报价和正成交量。
缺失历史求购、会员档位与Whale不倒填。组内未触发也保留；三个事件在±14日内诊断首次信号，不能当作自动事件发现。

| 规则 | 环境 | 退出 | 时段 | 信号/可评估 | 熊市n | 熊市净均值 | 熊市净中位 | 熊市胜率 | 熊市P10 |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| left_support | ungated | 7 | development_2025 | 1588/1081 | 229 | 4.01% | -2.20% | 42.79% | -11.60% |
| left_support | ungated | 7 | 2026_Q1 | 821/604 | 319 | 3.41% | -0.76% | 47.02% | -10.06% |
| left_support | ungated | 7 | 2026_Q2 | 1812/1525 | 1298 | -8.19% | -8.35% | 20.72% | -25.29% |
| left_support | ungated | 7 | 2026_Q3 | 1356/1075 | 1075 | -6.29% | -7.13% | 16.93% | -15.75% |
| left_support | ungated | 7 | recent90 | 1358/1050 | 1050 | -7.90% | -8.28% | 12.48% | -16.42% |
| left_support | ungated | 14 | development_2025 | 1441/667 | 74 | -2.09% | -6.96% | 24.32% | -16.80% |
| left_support | ungated | 14 | 2026_Q1 | 718/472 | 254 | 5.53% | 0.67% | 52.76% | -12.02% |
| left_support | ungated | 14 | 2026_Q2 | 1559/1039 | 901 | -12.39% | -13.74% | 11.43% | -26.96% |
| left_support | ungated | 14 | 2026_Q3 | 1119/776 | 776 | -9.00% | -9.36% | 13.40% | -20.43% |
| left_support | ungated | 14 | recent90 | 1125/787 | 787 | -10.28% | -10.47% | 11.05% | -21.25% |
| left_support | ungated | 30 | development_2025 | 1262/233 | 21 | -6.34% | -8.26% | 14.29% | -17.84% |
| left_support | ungated | 30 | 2026_Q1 | 571/303 | 191 | 23.27% | 11.54% | 70.16% | -10.37% |
| left_support | ungated | 30 | 2026_Q2 | 1265/728 | 596 | -11.67% | -16.93% | 17.28% | -36.67% |
| left_support | ungated | 30 | 2026_Q3 | 830/449 | 449 | -17.81% | -16.49% | 6.24% | -35.39% |
| left_support | ungated | 30 | recent90 | 916/466 | 466 | -18.64% | -17.07% | 5.15% | -36.26% |
| left_support | ungated | take15 | development_2025 | 1262/351 | 21 | -7.53% | -10.44% | 9.52% | -11.53% |
| left_support | ungated | take15 | 2026_Q1 | 571/337 | 191 | 10.62% | 15.34% | 66.49% | -11.44% |
| left_support | ungated | take15 | 2026_Q2 | 1265/840 | 677 | -13.25% | -13.77% | 11.37% | -32.24% |
| left_support | ungated | take15 | 2026_Q3 | 830/525 | 525 | -10.00% | -11.26% | 7.24% | -16.24% |
| left_support | ungated | take15 | recent90 | 916/466 | 466 | -10.47% | -11.30% | 5.79% | -16.17% |
| left_support | ungated | trail8 | development_2025 | 1262/378 | 21 | -6.03% | -10.14% | 14.29% | -11.41% |
| left_support | ungated | trail8 | 2026_Q1 | 571/339 | 191 | 8.60% | 1.61% | 57.07% | -10.56% |
| left_support | ungated | trail8 | 2026_Q2 | 1265/864 | 689 | -12.50% | -12.26% | 11.61% | -31.45% |
| left_support | ungated | trail8 | 2026_Q3 | 830/534 | 534 | -8.78% | -10.31% | 9.74% | -16.08% |
| left_support | ungated | trail8 | recent90 | 916/466 | 466 | -8.93% | -10.27% | 8.58% | -16.01% |
| left_support | local_repair | 7 | development_2025 | 1000/705 | 121 | 5.79% | 0.38% | 52.07% | -7.93% |
| left_support | local_repair | 7 | 2026_Q1 | 505/433 | 169 | 2.61% | -1.42% | 42.01% | -9.85% |
| left_support | local_repair | 7 | 2026_Q2 | 1481/1273 | 993 | -9.55% | -8.79% | 19.74% | -30.64% |
| left_support | local_repair | 7 | 2026_Q3 | 1002/762 | 762 | -6.66% | -7.14% | 17.85% | -16.16% |
| left_support | local_repair | 7 | recent90 | 1046/791 | 791 | -8.11% | -8.46% | 13.15% | -16.81% |
| left_support | local_repair | 14 | development_2025 | 949/414 | 20 | -9.81% | -8.52% | 5.00% | -19.26% |
| left_support | local_repair | 14 | 2026_Q1 | 448/343 | 131 | 1.74% | -2.07% | 43.51% | -14.17% |
| left_support | local_repair | 14 | 2026_Q2 | 1360/887 | 714 | -12.97% | -14.35% | 10.92% | -26.66% |
| left_support | local_repair | 14 | 2026_Q3 | 848/600 | 600 | -9.25% | -9.42% | 12.17% | -20.35% |
| left_support | local_repair | 14 | recent90 | 905/631 | 631 | -10.84% | -10.82% | 9.19% | -21.81% |
| left_support | local_repair | 30 | development_2025 | 862/171 | 9 | -8.21% | -7.25% | 22.22% | -18.10% |
| left_support | local_repair | 30 | 2026_Q1 | 369/224 | 107 | 23.52% | 5.80% | 60.75% | -16.96% |
| left_support | local_repair | 30 | 2026_Q2 | 1137/691 | 528 | -13.47% | -18.53% | 16.48% | -39.48% |
| left_support | local_repair | 30 | 2026_Q3 | 676/389 | 389 | -19.44% | -17.70% | 4.88% | -37.29% |
| left_support | local_repair | 30 | recent90 | 756/366 | 366 | -20.30% | -18.98% | 3.55% | -37.98% |
| left_support | local_repair | take15 | development_2025 | 862/259 | 9 | -11.08% | -11.38% | 11.11% | -14.73% |
| left_support | local_repair | take15 | 2026_Q1 | 369/264 | 107 | 6.55% | 7.62% | 56.07% | -13.04% |
| left_support | local_repair | take15 | 2026_Q2 | 1137/776 | 576 | -14.74% | -14.00% | 9.03% | -33.66% |
| left_support | local_repair | take15 | 2026_Q3 | 676/436 | 436 | -10.47% | -11.40% | 5.96% | -16.10% |
| left_support | local_repair | take15 | recent90 | 756/366 | 366 | -10.80% | -11.40% | 4.92% | -16.10% |
| left_support | local_repair | trail8 | development_2025 | 862/279 | 9 | -11.08% | -11.38% | 11.11% | -14.73% |
| left_support | local_repair | trail8 | 2026_Q1 | 369/266 | 107 | 5.12% | -2.10% | 45.79% | -11.25% |
| left_support | local_repair | trail8 | 2026_Q2 | 1137/799 | 590 | -13.71% | -12.26% | 9.49% | -33.30% |
| left_support | local_repair | trail8 | 2026_Q3 | 676/438 | 438 | -8.90% | -10.34% | 9.59% | -16.06% |
| left_support | local_repair | trail8 | recent90 | 756/366 | 366 | -8.91% | -10.32% | 9.02% | -16.01% |
| uniform_turn | ungated | 7 | development_2025 | 1688/1013 | 353 | -1.40% | -3.95% | 26.06% | -8.99% |
| uniform_turn | ungated | 7 | 2026_Q1 | 1166/1121 | 298 | -1.00% | -3.19% | 27.18% | -9.80% |
| uniform_turn | ungated | 7 | 2026_Q2 | 1053/926 | 897 | -3.21% | -5.01% | 34.23% | -20.98% |
| uniform_turn | ungated | 7 | 2026_Q3 | 1491/1279 | 1279 | -6.21% | -6.68% | 17.44% | -14.88% |
| uniform_turn | ungated | 7 | recent90 | 1528/1347 | 1347 | -7.03% | -7.67% | 14.85% | -15.40% |
| uniform_turn | ungated | 14 | development_2025 | 1487/550 | 161 | -2.42% | -5.72% | 23.60% | -11.85% |
| uniform_turn | ungated | 14 | 2026_Q1 | 970/880 | 248 | 0.56% | -2.52% | 38.31% | -10.97% |
| uniform_turn | ungated | 14 | 2026_Q2 | 899/755 | 736 | -6.10% | -10.12% | 23.78% | -21.13% |
| uniform_turn | ungated | 14 | 2026_Q3 | 1243/968 | 968 | -8.35% | -8.45% | 9.61% | -17.46% |
| uniform_turn | ungated | 14 | recent90 | 1276/970 | 970 | -9.51% | -9.59% | 9.07% | -20.00% |
| uniform_turn | ungated | 30 | development_2025 | 1318/258 | 48 | -7.33% | -7.08% | 14.58% | -19.29% |
| uniform_turn | ungated | 30 | 2026_Q1 | 686/410 | 184 | 8.77% | 2.42% | 58.15% | -12.72% |
| uniform_turn | ungated | 30 | 2026_Q2 | 733/574 | 564 | -14.07% | -15.18% | 22.87% | -42.98% |
| uniform_turn | ungated | 30 | 2026_Q3 | 976/644 | 644 | -14.06% | -13.74% | 6.21% | -26.18% |
| uniform_turn | ungated | 30 | recent90 | 977/574 | 574 | -14.54% | -13.60% | 6.27% | -28.07% |
| uniform_turn | ungated | take15 | development_2025 | 1318/305 | 48 | -5.93% | -10.20% | 14.58% | -12.59% |
| uniform_turn | ungated | take15 | 2026_Q1 | 686/558 | 184 | 4.07% | 0.24% | 51.09% | -11.52% |
| uniform_turn | ungated | take15 | 2026_Q2 | 733/597 | 585 | -6.12% | -11.29% | 23.59% | -22.08% |
| uniform_turn | ungated | take15 | 2026_Q3 | 976/744 | 744 | -10.17% | -10.97% | 4.97% | -14.55% |
| uniform_turn | ungated | take15 | recent90 | 977/574 | 574 | -10.18% | -10.91% | 5.05% | -14.74% |
| uniform_turn | ungated | trail8 | development_2025 | 1318/307 | 48 | -6.10% | -8.54% | 8.33% | -11.82% |
| uniform_turn | ungated | trail8 | 2026_Q1 | 686/581 | 184 | 1.88% | -0.74% | 45.65% | -11.29% |
| uniform_turn | ungated | trail8 | 2026_Q2 | 733/607 | 595 | -5.49% | -10.10% | 25.88% | -20.98% |
| uniform_turn | ungated | trail8 | 2026_Q3 | 976/749 | 749 | -8.69% | -10.25% | 7.88% | -14.42% |
| uniform_turn | ungated | trail8 | recent90 | 977/574 | 574 | -8.96% | -10.33% | 7.84% | -14.57% |
| uniform_turn | local_repair | 7 | development_2025 | 1194/693 | 214 | -1.06% | -3.33% | 29.91% | -8.00% |
| uniform_turn | local_repair | 7 | 2026_Q1 | 882/850 | 224 | -0.41% | -2.53% | 31.25% | -8.39% |
| uniform_turn | local_repair | 7 | 2026_Q2 | 845/777 | 762 | -2.92% | -4.54% | 35.56% | -21.57% |
| uniform_turn | local_repair | 7 | 2026_Q3 | 1113/954 | 954 | -6.61% | -7.01% | 18.45% | -15.75% |
| uniform_turn | local_repair | 7 | recent90 | 1211/1057 | 1057 | -7.36% | -7.90% | 14.85% | -16.06% |
| uniform_turn | local_repair | 14 | development_2025 | 1087/348 | 69 | -6.11% | -6.33% | 18.84% | -12.79% |
| uniform_turn | local_repair | 14 | 2026_Q1 | 756/713 | 187 | -0.36% | -2.68% | 34.76% | -10.42% |
| uniform_turn | local_repair | 14 | 2026_Q2 | 733/646 | 637 | -5.45% | -9.97% | 24.96% | -20.01% |
| uniform_turn | local_repair | 14 | 2026_Q3 | 950/770 | 770 | -8.34% | -8.09% | 10.13% | -18.08% |
| uniform_turn | local_repair | 14 | recent90 | 1032/763 | 763 | -9.38% | -9.42% | 10.09% | -20.48% |
| uniform_turn | local_repair | 30 | development_2025 | 1034/197 | 29 | -9.72% | -7.99% | 10.34% | -20.49% |
| uniform_turn | local_repair | 30 | 2026_Q1 | 562/357 | 141 | 7.69% | 1.77% | 56.03% | -12.39% |
| uniform_turn | local_repair | 30 | 2026_Q2 | 619/533 | 524 | -14.27% | -14.20% | 23.28% | -43.61% |
| uniform_turn | local_repair | 30 | 2026_Q3 | 779/558 | 558 | -14.39% | -13.77% | 5.20% | -26.79% |
| uniform_turn | local_repair | 30 | recent90 | 831/481 | 481 | -14.82% | -13.86% | 5.82% | -28.51% |
| uniform_turn | local_repair | take15 | development_2025 | 1034/238 | 29 | -7.71% | -10.34% | 13.79% | -13.58% |
| uniform_turn | local_repair | take15 | 2026_Q1 | 562/469 | 141 | 3.48% | -0.42% | 48.94% | -11.59% |
| uniform_turn | local_repair | take15 | 2026_Q2 | 619/542 | 533 | -5.51% | -11.27% | 25.14% | -21.52% |
| uniform_turn | local_repair | take15 | 2026_Q3 | 779/630 | 630 | -10.59% | -10.99% | 4.60% | -15.07% |
| uniform_turn | local_repair | take15 | recent90 | 831/481 | 481 | -10.55% | -10.98% | 5.41% | -15.60% |
| uniform_turn | local_repair | trail8 | development_2025 | 1034/239 | 29 | -7.82% | -10.34% | 6.90% | -13.58% |
| uniform_turn | local_repair | trail8 | 2026_Q1 | 562/484 | 141 | 0.96% | -3.28% | 41.13% | -11.07% |
| uniform_turn | local_repair | trail8 | 2026_Q2 | 619/546 | 537 | -4.74% | -10.06% | 27.56% | -20.17% |
| uniform_turn | local_repair | trail8 | 2026_Q3 | 779/631 | 631 | -9.14% | -10.28% | 7.92% | -15.05% |
| uniform_turn | local_repair | trail8 | recent90 | 831/481 | 481 | -9.25% | -10.35% | 8.94% | -15.48% |
| first_pullback | ungated | 7 | development_2025 | 200/115 | 59 | -3.53% | -4.90% | 18.64% | -8.62% |
| first_pullback | ungated | 7 | 2026_Q1 | 238/189 | 122 | -0.08% | -2.91% | 27.05% | -8.64% |
| first_pullback | ungated | 7 | 2026_Q2 | 234/219 | 214 | -4.93% | -6.09% | 20.09% | -15.67% |
| first_pullback | ungated | 7 | 2026_Q3 | 389/359 | 359 | -6.23% | -6.04% | 8.64% | -12.24% |
| first_pullback | ungated | 7 | recent90 | 387/325 | 325 | -6.62% | -6.52% | 8.62% | -12.75% |
| first_pullback | ungated | 14 | development_2025 | 199/74 | 40 | -3.04% | -4.69% | 25.00% | -11.93% |
| first_pullback | ungated | 14 | 2026_Q1 | 228/167 | 111 | 3.17% | -1.19% | 43.24% | -9.76% |
| first_pullback | ungated | 14 | 2026_Q2 | 230/182 | 178 | -8.77% | -8.62% | 17.98% | -26.55% |
| first_pullback | ungated | 14 | 2026_Q3 | 373/311 | 311 | -8.93% | -8.21% | 6.75% | -17.49% |
| first_pullback | ungated | 14 | recent90 | 371/291 | 291 | -9.36% | -8.55% | 6.53% | -17.95% |
| first_pullback | ungated | 30 | development_2025 | 199/14 | 0 | — | — | — | — |
| first_pullback | ungated | 30 | 2026_Q1 | 204/127 | 83 | 13.18% | 4.38% | 72.29% | -10.94% |
| first_pullback | ungated | 30 | 2026_Q2 | 219/105 | 103 | -8.17% | -15.19% | 22.33% | -39.11% |
| first_pullback | ungated | 30 | 2026_Q3 | 334/162 | 162 | -14.16% | -12.07% | 6.17% | -28.24% |
| first_pullback | ungated | 30 | recent90 | 336/233 | 233 | -16.22% | -15.79% | 4.72% | -29.30% |
| first_pullback | ungated | take15 | development_2025 | 199/14 | 0 | — | — | — | — |
| first_pullback | ungated | take15 | 2026_Q1 | 204/136 | 83 | 5.48% | 2.92% | 65.06% | -11.69% |
| first_pullback | ungated | take15 | 2026_Q2 | 219/137 | 135 | -8.79% | -12.36% | 14.07% | -20.87% |
| first_pullback | ungated | take15 | 2026_Q3 | 334/245 | 245 | -10.35% | -10.82% | 3.27% | -13.66% |
| first_pullback | ungated | take15 | recent90 | 336/233 | 233 | -10.27% | -10.80% | 3.86% | -13.38% |
| first_pullback | ungated | trail8 | development_2025 | 199/14 | 0 | — | — | — | — |
| first_pullback | ungated | trail8 | 2026_Q1 | 204/134 | 83 | 4.67% | 1.14% | 57.83% | -11.13% |
| first_pullback | ungated | trail8 | 2026_Q2 | 219/140 | 138 | -7.70% | -10.86% | 13.04% | -19.24% |
| first_pullback | ungated | trail8 | 2026_Q3 | 334/251 | 251 | -9.59% | -10.46% | 4.38% | -13.25% |
| first_pullback | ungated | trail8 | recent90 | 336/233 | 233 | -9.71% | -10.46% | 4.72% | -13.15% |
| first_pullback | local_repair | 7 | development_2025 | 46/20 | 11 | -3.63% | -5.02% | 18.18% | -7.61% |
| first_pullback | local_repair | 7 | 2026_Q1 | 51/49 | 19 | 1.95% | -0.50% | 36.84% | -5.29% |
| first_pullback | local_repair | 7 | 2026_Q2 | 53/50 | 47 | -0.77% | -3.36% | 34.04% | -19.81% |
| first_pullback | local_repair | 7 | 2026_Q3 | 115/103 | 103 | -6.67% | -5.97% | 11.65% | -13.35% |
| first_pullback | local_repair | 7 | recent90 | 142/102 | 102 | -7.17% | -6.96% | 10.78% | -13.66% |
| first_pullback | local_repair | 14 | development_2025 | 46/13 | 7 | -4.28% | -6.45% | 28.57% | -8.01% |
| first_pullback | local_repair | 14 | 2026_Q1 | 50/46 | 17 | 3.34% | -0.15% | 47.06% | -8.09% |
| first_pullback | local_repair | 14 | 2026_Q2 | 52/24 | 22 | -7.63% | -10.56% | 22.73% | -27.69% |
| first_pullback | local_repair | 14 | 2026_Q3 | 114/99 | 99 | -8.78% | -7.40% | 7.07% | -17.59% |
| first_pullback | local_repair | 14 | recent90 | 140/93 | 93 | -9.61% | -8.21% | 7.53% | -21.23% |
| first_pullback | local_repair | 30 | development_2025 | 46/2 | 0 | — | — | — | — |
| first_pullback | local_repair | 30 | 2026_Q1 | 50/36 | 17 | 18.27% | 8.21% | 70.59% | -3.74% |
| first_pullback | local_repair | 30 | 2026_Q2 | 51/22 | 20 | -13.90% | -20.95% | 25.00% | -44.94% |
| first_pullback | local_repair | 30 | 2026_Q3 | 110/81 | 81 | -14.70% | -13.34% | 6.17% | -26.23% |
| first_pullback | local_repair | 30 | recent90 | 136/69 | 69 | -16.22% | -15.28% | 5.80% | -31.84% |
| first_pullback | local_repair | take15 | development_2025 | 46/2 | 0 | — | — | — | — |
| first_pullback | local_repair | take15 | 2026_Q1 | 50/44 | 17 | 8.53% | 15.46% | 64.71% | -11.35% |
| first_pullback | local_repair | take15 | 2026_Q2 | 51/35 | 33 | -5.39% | -12.23% | 21.21% | -20.98% |
| first_pullback | local_repair | take15 | 2026_Q3 | 110/89 | 89 | -10.72% | -10.89% | 3.37% | -14.00% |
| first_pullback | local_repair | take15 | recent90 | 136/69 | 69 | -10.76% | -10.90% | 4.35% | -14.40% |
| first_pullback | local_repair | trail8 | development_2025 | 46/2 | 0 | — | — | — | — |
| first_pullback | local_repair | trail8 | 2026_Q1 | 50/44 | 17 | 10.57% | 0.43% | 52.94% | -9.04% |
| first_pullback | local_repair | trail8 | 2026_Q2 | 51/34 | 32 | -9.60% | -11.87% | 15.62% | -21.04% |
| first_pullback | local_repair | trail8 | 2026_Q3 | 110/89 | 89 | -9.28% | -10.45% | 7.87% | -13.73% |
| first_pullback | local_repair | trail8 | recent90 | 136/69 | 69 | -9.21% | -10.47% | 10.14% | -13.94% |

## 案例覆盖缺口
- ★ Sport Gloves | Hedge Maze (Minimal Wear)：mapped=False, loaded=False, event_close=False
- ★ Sport Gloves | Pandora's Box (Minimal Wear)：mapped=False, loaded=False, event_close=False

完整逐笔、案例触发及覆盖见同目录文件；未通过系统验证，不输出正式买入资格。
