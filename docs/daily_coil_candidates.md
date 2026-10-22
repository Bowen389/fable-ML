# 每日蓄势观察候选与报告合并

每日评分任务 Daily leader process scores（原定北京时间10:15，GitHub可能延迟）成功完成后，Daily accumulation watch candidates 自动接力。没有新增定时采集；只复用刚刷新的 research_cache，不请求行情接口、不拟合模型、不重复历史回测。

沿用独立对齐蓄势研究的固定权重与计算方式。每天输出完整链条Top5、提前蓄势Top5，字段含日K日期、生成时间、分数、形态、数据覆盖率、扣分和主要理由。覆盖率仅表示可计算字段；局部形态可以有分，但不等于链条完整。模型与生产买点资格均不改变。

栏目自动合并到 output/latest.md、process_score_report.md、multifactor_report.md、guide_latest.md；guide_latest.json附加coil_candidates。扫描或指导报告再次生成时也保留该栏目。原报告内容保留，标记块幂等替换。发布时读取当前远端head的报告，不用旧工作区覆盖并行更新。

产物：output/daily_coil_candidates.json、daily_coil_scores.csv、daily_coil_report.md。每个完整日与算法版本的首次评分保存到 output/history/coil_scores_<日期>_daily-coil-v1.csv；不改写已有快照。公式变更时应更新版本。

旧日期显式标注，异常日期不展示名单；失败写error并清除旧候选，不能当成零买点。失败状态先发布到报告，再将任务标红。候选只作观察，未通过买入系统验证，不自动开仓；全平台量与悠悠价格分别理解，不能认定会员身份或真实成本。研究费用卖出1%、买入0、无滑点。
