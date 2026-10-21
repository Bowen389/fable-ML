# 标准化形态迁移实验

针对完整背景模型在已知案例上31/31拟合、事件留一0/31覆盖的问题，增加删除价格/品类/行情背景的消融对照。不能从这一失败直接证明是哪个特征导致，须以对照结果判断。

四个固定方案：完整背景控制；删去绝对价格、绝对量、手套/探员标记、大盘变量和品类整体动量；用自身此前波动/前期震荡区间标准化涨跌及回踩的形态；相同标准化空间内的成功/失败近邻模板。模板的缺失填补与缩放只用训练事件，负例超过1500时采用固定随机子样本。

逐次拿掉整段事件回放。选模依次最大化三事件最差前30覆盖率、平均事件覆盖率、平均AP；不为每件商品单独挑模型。此选择已经使用三个开发事件，早期事件可能训练于晚期标签，所有结果仍为回溯机制研究，绝不冒充历史可执行成绩。

所有算法使用同样的±7日窗口和全池排名，首次入榜/最佳日期/入榜收益都保留。已知案例拟合与事件留一分列。当前模型只供独立研究，不修改生产评分。

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python -m unittest -v test_rebound_shapes.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python verify_rebound_shape_pipeline.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python -u rebound_shape_transfer.py
```

实际输出位于output/rebound_shapes：report.md、validation.json、case_windows.csv、event_holdout_rows.csv.gz、apparent_fit_rows.csv.gz、current_candidates.csv、shape_models.joblib。合成流水线只验证工程，不用于报告市场收益。
