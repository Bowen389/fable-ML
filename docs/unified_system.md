# 一体化系统

入口：`python unified_system.py report`，总报告：[output/system_latest.md](../output/system_latest.md)。

| 模块 | 集成方式 |
|---|---|
| 四类传统买点 | buy-cs 原规则移入 integrations/traditional.py，全量历史重算；当天未完成K线排除 |
| 悠悠价格/在售/求购 | 复用 up 现有采集结果；完整保留815监控行，求购每日采集口径 |
| 大户求购排行 | 只读求购库，有效挂单金额排行，非成交或持仓 |
| CSQAQ Whale V7 | 用户提供源码纳入 integrations/whale；增量状态保存在 state/whale_monitor |
| 原版ML与蓄势观察 | 合并展示现有输出，不修改评分公式和买入资格 |

报价由 up 每日09:17、15:17、21:17（北京时间）采集。总报告于10:47、16:07、22:07尝试刷新；蓄势评分成功发布后也触发。每轮最多等待30分钟，确认本时段报价发布、昨日完整日K蓄势评分就绪，然后重新读取主分支已发布评分并生成报告。未就绪时显示等待原因并关闭入场，不将旧报价伪装为本时段更新。20:07尝试Whale实采，其余刷新复用状态。GitHub调度可能延迟，实际依赖检查优先于时钟。

## 凭据与原生采集
现有悠悠采集继续运行在 up，避免重复请求；代码也已打包，可手动运行：
- `python unified_system.py collect-demand`
- `python unified_system.py collect-quotes`
- `python unified_system.py collect-traditional`

悠悠原生采集需要 YP_RAW_HEADERS 或原采集器支持的请求头配置，传统原生采集需要 STEAMDT_API_KEY；这些凭据不会自动从其他仓库迁移。
Whale实采需要本仓库 Actions Secret `CSQAQ_TOKEN`，可在统一任务手动勾选 collect_whale。首次采集建立基线，不回放历史；首次没有新增事件不等于没有大户活动。没有凭据会明确显示 not_configured，不使用演示数据。Playwright依赖只在真实Whale采集需要时安装。

## 数据口径
悠悠价格与全平台成交量分开；求购金额变化不是净买入，挂单阈值与采集覆盖变化也会影响变化额。
悠悠用户与Steam用户不能直接对应。会员建仓、成本差、洗盘只是量价代理。
Whale仅辅助。观察候选不是经过验证的买入系统，不自动交易。
新独立研究卖出费1%、无滑点；原版历史统计仍按原报告独立标注。

原始下载、数据库、凭据不提交；仅发布报告和无凭据Whale增量状态。数据缺失、过期、零事件分别展示。

## 时序与版本一致性
报价CSV、报价元数据与每日求购库固定读取同一个 up 提交，报告记录 upstream_sha、quote_run_id 与各模块日期。日K与求购分别采用各自日期口径，不要求每日求购重复刷新。首份上游已就绪且评分可用的决策冻结为 output/history/decision_ready_日期_decision-v1.json；之前的数据等待快照保留但不充当有效前瞻入场样本。
