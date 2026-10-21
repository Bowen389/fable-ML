# 自动历史反弹形态记忆

按季度起点，只使用结果已完成22自然日的历史样本。人工指定案例只用于商品精确映射及事后检查，不用于训练标签。标签由过去已完成的后续行情自动产生。

正例：未来第7—21日最高收盘净涨幅前30且至少15%、固定7或14日净收益为正、信号前7日涨幅不超过20%。每件商品22日去重后最多1200个正例。负例：潜力低于10%、14日净收益非正、前7日涨幅不超过20%，最多1500个负例。抽样固定种子。

两个预先固定的记忆范围：全部历史、最近540日。都使用按自身波动及区间标准化的形态，缺失填补、缩放和近邻库仅从当时的训练原型拟合。不根据指定案例选一个范围当成事前最佳方案。

这比使用后期事件回放早期事件的模型更严格，但仍有研究者已经看过2026年结果的选型偏差、固定池存活偏差和历史修订问题。不是完全未见的独立验证。原型训练最晚标签日期逐季披露。

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python -m unittest -v test_rebound_memory.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python verify_rebound_memory_pipeline.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python -u rebound_historical_memory.py
```

输出output/rebound_memory包含报告、验证元数据、逐案例首次排名、历史原型及排名、当日研究榜、模型。仅卖出1%、零滑点。生产评分不改，研究榜不代表买入资格。
