# 每日自适应龙头观察部署

默认分支的 adaptive-rank.yml 每日北京时间10:45启动；GitHub定时可能延迟。首次部署会因该工作流文件的push立即运行，也可手动workflow_dispatch。

工作流分别检出main最新数据和research/peer-reversal-leaders研究代码，复制main的data及universe.csv给研究程序。代码版本会打印到日志；主扫描仍负责取数，本任务不使用API、不调用推送、不写买点日志。它重建因果特征，执行固定对照与月度滚动回放，生成每日最多30个观察排名。最新月度模型、训练审计和报告保存回研究分支；运行产生的文件也作为Actions artifact保留30天。分支更新采用正常fast-forward，冲突会失败，不强推覆盖。

报告：output/adaptive_rank_latest.md；结构化排名：output/adaptive_rank_latest.json；模型：state/adaptive_rank/。数据陈旧时报告会注明历史观察。预测使用当月月初前已完整到期的训练样本，最晚训练标签日严格早于预测月起点。未来标签仅用于回放评价。统计是每日入选样本收益，不是实际持仓组合收益。

预设五组实验：固定基础、固定行情分层、固定品类特征、滚动基础、滚动综合。固定参数，T1/T0分别训练，报告对比Top5/10/30及近期涨幅、随机基准。线上固定输出滚动综合T1 Top30，T0评分附在同一名单；不会根据当次回放成绩临时选择最佳模型。

发布状态为research_only，自动买点放行0。已有买点扫描工作流不被替换；研究结果不能自动提升规则健康状态。是否改成自动买点须另行建立并通过独立盈利验证。

本地：pip install -r requirements-research.txt；python tools/research_adaptive_rank.py。开发时可用 --cache /path/features.pkl；部署不使用开发机缓存。
