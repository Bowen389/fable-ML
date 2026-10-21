# 时序阶段反弹研究 v3

独立于生产评分，按用户要求在事件前后各7日逐日回放。不能通过商品名称、ID或人工指定身份加分。研究员已见这些历史行情，因此本轮为开发诊断，不是全新独立验证。

输入增加此前21—60日蓄势、此前7—21日量价台阶、此前2—7日洗盘及当前放量等分段特征、波动率、价格量级、品类相对强弱；品类仅粗分手套/探员，不编码具体商品身份。均为截至当时可见的代理。

三个固定模型：stage7_global预测7日领涨前30，stage21_global预测第7至21日最高收盘净涨幅至少15%且前30，stage21_recent使用同潜力标签且训练数据限定此前540日。后者是峰值潜力标签，不表示可以在最高价卖出。实际收益另按固定7/14日计算。

按季度扩展训练，120日校准，所有模型统一22日成熟标签隔离。仅使用校准AP相对基准率的提升选择当季模型。人工案例名单不参与选模，历史商品本身的已成熟公开收益可以正常进入训练。重新查看各季结果仍有多重研究偏差，需要冻结后的新事件验证。

14项单元检查及合成数据端到端检查。合成检查不是实际市场收益。

```bash
python -m unittest -v test_bear_rebound.py test_rebound_rank.py test_rebound_stage.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python verify_rebound_stage_pipeline.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python -u rebound_stage_research.py
```

输出output/rebound_stage/：report.md、validation.json、case_daily.csv、case_windows.csv、historical_rankings.csv.gz、current_candidates.csv、models.joblib。case_windows保留最佳排名与首次入榜的区别，并列入榜价对锚点价偏离、首次入榜后7/14日净收益；最佳日只作事后诊断。

买入0、卖出1%、零滑点；悠悠价格与全平台量分开。没有历史求购时不倒填，会员身份与真实成本不能据此确认。两款缺失略磨手套尝试严格名称/磨损搜索，只接受唯一且符合Firepulse长ID结构的匹配，否则明确缺失。补采不改生产商品池。

无自动替换评分、真实买入或自动资格晋级。