# 共同特征的透明权重研究

从三个已知案例事件与失败对照的描述差异，提炼六项当日全池分位：相对领先、相对转强、近期扩量、波动活跃、弱同类背景、前期量能活跃。六因子已经看过三个事件后确定，因此后续事件留一也只是开发诊断。

用20%步长穷举252个非负且合计100%的权重。统一公式，不给具体商品名称或ID加分。优先提高三事件最差的有效前30覆盖，其次平均事件覆盖，最后平均有效最佳排名。有效开发目标要求未来第7—21日仍有>=15%潜力且固定7或14日净收益为正；未来标签仅用于选择开发公式，绝不用于当日评分或过滤。

报告同时列原始覆盖与未来结果合格覆盖，保留未经未来筛选的首次入榜日期及其后收益，避免把事后挑到的赚钱日期当作可执行入场。复杂比较带来多重研究与已知赢家选择偏差，不能称为样本外盈利验证。

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python -m unittest -v test_rebound_shared.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python verify_rebound_shared_pipeline.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python -u rebound_shared_factors.py
```

输出output/rebound_shared/：report.md、validation.json、case_windows.csv、outcome_qualified_windows.csv、all_profiles.csv、development_rows.csv.gz、event_holdout_rows.csv.gz、current_candidates.csv。费用仅卖出1%，零滑点。生产评分保持不变，无自动买入资格。
