# 固定公式的完整时段与入场验证

冻结开发公式：相对领先40%、相对转强20%、近期扩量40%。本轮不再改权重，完整列出5类入场×7/10/14日持有共15个方案。

入场对照：每日前30；此前7天均不在前30且报价完整后的再次入榜；7日涨幅不超过15%；首次入榜并限制涨幅；首次入榜、限制涨幅且局部修复。首次只表示7日窗口代理，不是生命周期首次，局部修复不要求市场7日涨幅为正。

信号后次日收盘代理入场，持有期按自然日，卖出1%无滑点。退出可跨季度，按信号季度分组，但必须有截至研究日的完整真实结果。每商品计划持有期+2日去重，先决定信号，再检查未来结果是否缺失；缺失与未成熟分开保留。

2025、2026各季度、2026累计及最近90日分别列示；同时排除三段已知事件各前后30天作诊断。这仍不等于全新未见验证，因为公式来自已看过的2026案例，多轮历史研究已经有选择偏差。

输出output/rebound_entries/report.md、validation.json、trades.csv.gz、current_candidates.csv。当前研究榜不代表买入资格，生产评分未改。

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python -m unittest -v test_rebound_entries.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python verify_rebound_entry_pipeline.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python -u rebound_entry_validation.py
```
