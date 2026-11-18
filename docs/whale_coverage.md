# Whale 监控覆盖度与监控清单

## 背景：为什么"没动静"经常是"根本没扫"

2026-10-22 接入 Whale 模块时，监控商品清单（CSQAQ TOP30 快照）写进了
`state/whale_monitor/data/top30_latest.json`，之后 27 天没有被刷新过。

两个机制叠加，导致监控范围被永久冻结：

1. `integrations/whale/monitor_v7.py` 的 `top_goods()` 原本用**文件 mtime** 判断快照是否过期。
   Actions 每次 `checkout` + `git reset --hard` 都会把 mtime 重置成"刚刚"，
   `age_hours` 永远接近 0 → 浏览器抓取分支永远不触发。
   （现在改成读文件内 `generated_at`，没有该字段才退回 mtime。）
2. `rank_new_goods()` 只对"不在 `top30_seen_goods.json` 里的 good_id"做 rank。
   seen 集合也冻在那 30 个商品上 → 没有新商品进入 → 鲸鱼池永远 245 只。

结果：快照里出现过 **2819 个 good_id**，主动监控的只有 30 个（1.1%），
其中 **2002 个是非"崭新出厂"磨损**（略磨/久经沙场/战痕累累/破损不堪），零覆盖。
像 `AK-47 | 幻影破坏者`、`M4A1消音版 | 二号玩家`、`沙漠之鹰 | 蓝色层压板`、
`裹手 | 云杉 DDPAT`、`裹手 | 恶土`、`AWP | 冥界之河`、`沙漠之鹰 | 阴谋者`
这些标的**从来没有被主动监控过**，只能靠其它商品带出来的附带记录被动看到，
所以只能看到零星几条，看不到头部。

## 现在的做法

### 1. 显式白名单：`state/whale_monitor/data/extra_goods.json`

格式：`{"updated_at": "...", "goods": [{"good_id": "...", "name": "..."}]}`

- `extra_goods(cfg)` 会把它并进 `top_goods(cfg)` 的结果里，
  `rank_new_goods()` 对其中每个**尚未见过**的 good_id 调一次 `POST /monitor/rank`，
  取回该商品的大户排名，写进 `whales_monitor_pool.json`。
- 因此**每加一个 good_id，最多新增 10 只鲸鱼**（`WHALE_RANK_USERS` 默认 10）。
- 当前白名单 66 个 good_id：30 个在监控品的**全部磨损变体** + 重点标的
  （幻影破坏者 / 二号玩家 / DE 蓝色层压板 / 云杉 DDPAT / 恶土 / AWP 冥界之河 /
  DE 阴谋者 / 法玛斯 2A2F / AK 局外人 等）。

### 2. 每轮吞吐

`unified_system.py` 里：

| 环境变量 | 旧值 | 新值 | 说明 |
|---|---|---|---|
| `WHALE_MAX_WHALES_PER_ROUND` | 30 | 80 | 每轮最多扫多少只鲸鱼 |
| `WHALE_MAX_RUN_SECONDS` | 600 | 1500 | 每轮时间上限（秒） |

池子扩大后如果不同时抬吞吐，轮转周期会从 8.2 天拉到 20 天以上，
单只鲸鱼的"最近"就失去意义。`.github/workflows/unified-system.yml` 的
job `timeout-minutes` 同时从 75 抬到 150，给 20:07 那一档留出余量。

### 3. 覆盖度自检：`whale_coverage_audit.py`

```bash
python whale_coverage_audit.py            # 文字报告
python whale_coverage_audit.py --json     # 机器可读
```

只读本地状态文件，不请求任何接口，不改动任何数据。输出三件事：

1. **监控商品清单新鲜度**：TOP30 快照年龄、白名单年龄、合计监控 good_id 数
2. **鲸鱼池与轮转**：池规模、每轮上限、全池轮转天数、单只鲸鱼末次扫描的中位滞后
3. **标的级覆盖新鲜度**：每个标的被多少只鲸鱼记录、最近一次事件距今多少天

告警阈值：清单 > 3 天未更新、轮转 > 10 天、标的 > 7 天无新事件。

结果会写进 `output/whale_coverage.json`，并作为 `coverage` 模块出现在
`output/system_latest.md` 的「Whale 监控覆盖度」小节。
`coverage` 不参与总体 `status` 的判定（只作为告警展示），避免它掩盖其它模块的问题。

## 一次扩池会发生什么

1. 手动触发 Actions → **Unified CS2 system** → 勾选 `collect_whale`。
2. `rank_new_goods()` 对 66 个新 good_id 各调一次 rank → 池子从 245 涨到约 600-700 只。
3. 每轮扫 80 只，约 8 天轮转一圈；每只鲸鱼的 task 会带回它自己的完整交易流，
   所以物品覆盖面会显著变宽。
4. 跑完后用 `whale_coverage_audit.py` 核对池子规模与轮转天数。

## 口径提醒

- 所有 Whale 事件都是 `CD_RECOVER`（物品回库），**不是成交确认**。
- `whale_snapshots.json` 里的数值是"记录条数"，真实件数只在已发布事件里。
- 悠悠 user_id 与 Steam ID 不是同一身份，不能合并。
- 单只鲸鱼 8 天左右才被扫一次，"最近没有动作"要结合覆盖度报告一起看。
