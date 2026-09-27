# CS2 饰品买点扫描器 · GitHub Actions 版

每天自动：**从 SteamDT 拉日 K → 算特征 → 按规则扫描买点 → 结算历史信号、更新规则健康度 → 生成报告 / 推送**，
所有数据和状态直接提交回仓库，不需要任何服务器。每月自动跑一次"学习任务"（重新调参、重新挖掘、训练 LightGBM）。

与 Colab 版（`cs2_scanner.ipynb`）同一套规则和代码逻辑，区别只是：无人值守、结果存在 git 里。

---

## 一、5 分钟部署

1. **新建一个 GitHub 仓库（建议 Private）**，把本目录全部内容推上去：
   ```bash
   cd cs2_actions
   git init -b main && git add -A && git commit -m "init"
   git remote add origin git@github.com:<你>/<仓库名>.git
   git push -u origin main
   ```
   目录里已经包含 2025-09-24 → 2026-09-22 的历史 K 线（`data/bars/`），以及规则库、已训练的模型。

2. **添加 Secrets**：仓库 → Settings → Secrets and variables → Actions → *New repository secret*

   | 名称 | 必填 | 说明 |
   |---|---|---|
   | `STEAMDT_API_KEY` | ✅ | SteamDT 个人中心 → API 管理 |
   | `TG_BOT_TOKEN` + `TG_CHAT_ID` | 可选 | Telegram 推送 |
   | `SERVERCHAN_KEY` | 可选 | Server酱（微信推送，https://sct.ftqq.com） |
   | `WEBHOOK_URL` | 可选 | 企业微信 / 飞书 / 钉钉 自定义机器人 webhook，或任意接收 JSON 的地址 |

   不配推送也行，报告会写在仓库 `output/latest.md` 里，并显示在每次运行的 Summary 页。

3. **启用 Actions 并手动跑第一次**：仓库 → Actions → 如提示 "enable workflows" 点启用 → 左侧选 **daily-scan** → *Run workflow*。
   第一次会把 1571 个饰品全部更新一遍（约 15 分钟，受 API 120 次/分钟限制），之后每天只补缺的日期。

4. 之后每天 **北京时间 09:30 左右**自动运行（GitHub 的定时任务高峰期可能延迟 10~40 分钟）。

> 如果 "Commit results" 步骤报 403：Settings → Actions → General → Workflow permissions 选 **Read and write permissions**。

---

## 二、每天看什么

| 位置 | 内容 |
|---|---|
| `output/latest.md` | 当日完整报告：市场状态、买点列表、接近满足、信号日志战绩、规则健康度（GitHub 上直接渲染） |
| `output/screen_latest.csv` | 买点表格（Excel 可开） |
| Actions → 某次运行 → Summary | 同一份报告 |
| 推送消息 | 精简版：市场状态 + 各规则命中数 + 前 5 个饰品 |
| `output/history/` | 每天的报告和买点存档 |
| `state/signals.csv` | 每条历史信号的真实结果（次日收盘入场，H 天后收盘出场，扣 2.5% 手续费） |
| `state/rules.json` | 规则库（可手工编辑：改阈值、把 `status` 改成 `disabled` 等） |

### 规则（默认 5 条）

| ID | 周期 | 条件 | 全样本 胜率 / 中位净收益 | 熊市外测 |
|---|---|---|---|---|
| S1 | 10 天 | 60日回撤分位≤0.20 且 距30日低点≥25天 且 短/长波动比≤0.30 | 59% / +4.1% | 39% |
| M4 | 14 天 | 60日回撤分位≤0.10 且 距30日低点≥25天 且 7日波动≤7.4% 且 枪械 5~100 元 | 61% / +7.1% | 49% |
| M3 | 14 天 | 偏离MA90≤−37.9% 且 60日区间位置≥0.03 且 距14日低反弹≤9.2% | 57% / +3.6% | **57%** |
| L1 | 30 天 | 60日回撤分位≤0.10 且 MA7/MA30≥+2.4% 且 距7日低反弹≤33.5% | 60% / +9.7% | 35%（需择时） |
| L3 | 30 天 | 60日回撤分位≤0.10 且 距30日低点≥21天 且 价格≤20 元 | 58% / +8.5% | 45% |

规则健康度按"跑赢当日全市场中位"的比例判定：90 日 ≥55% 正常，50~55% `watch`，<50% `probation`，180 日 <45% 自动 `disabled`。
当前（2026-09）市场处于深跌区，L 系列长线规则的择时开关为 ✗，报告里会标出来。

---

## 三、每月学习任务（monthly-learn）

每月 1 日自动运行，**只给建议、不自动改规则**（结果写到 `output/learn_<日期>.md` 和 `state/`）：

1. **重新调参**：在每个规则当前阈值附近（±2 档）搜索，要求 ≥9 个月有样本、单月占比 ≤35%、新阈值在 ≥60% 的月份里优于旧阈值才"建议采纳"。
2. **重新挖掘**：beam search 找新规则组合，必须通过最近 150 天的时序外测试（跑赢中位 ≥55%）才算"通过"。
3. **LightGBM 排序模型**：目标是"跑赢当日中位"，最近 90 天验证 RankIC ≥0.05 的模型才会在日常扫描中启用（表现为买点表里的 `ML分位` 列，只用于同一规则内排序）。

手动运行时可以勾选 **apply_retune**（自动应用通过检验的调参）和 **add_mined**（把通过外测的新规则以 `probation` 状态加入）。
也可以直接改 `state/rules.json` 后提交。

---

## 四、本地运行 / 调试

```bash
pip install -r requirements.txt
export STEAMDT_API_KEY=xxx            # 没有 key 时：export DATA_SOURCE=offline
python run.py scan --no-notify        # 日常扫描
python run.py learn --retune --mine --ml
python run.py init-seed seed/*.csv    # 导入 SteamDT 导出的历史 CSV（饰品名称,品类,日期,更新时间,开盘指数,收盘指数,最高指数,最低指数）
python tests/mock_api.py              # 用假 API 验证增量取数逻辑
```

环境变量（全部可选）：`DATA_SOURCE`(api/offline) · `REFRESH_MODE`(auto/full/none) · `PLATFORM`(ALL/BUFF/YOUPIN/C5/STEAM/HALOSKINS，也可在仓库 Variables 里设) ·
`MAX_FETCH_MINUTES` · `RATE_PER_MINUTE`(默认 110) · `FEE`(0.025) · `DROP_TODAY_BAR`(1) · `AUTO_UPDATE_STATUS`(1) · `ML_MIN_IC`(0.05)

---

## 五、数据是怎么存的

```
data/bars/2025-09.csv.gz   ← 已过去的月份：压缩、不再改动
data/bars/2026-09.csv      ← 当前月：明文，每天只追加新行（git diff 很小）
data/broad_kline.csv       ← SteamDT 官方大盘指数（仅对照）
data/fetch_errors.csv      ← 当天取数失败的饰品（有才生成）
```

- 列：`name,date,open,close,high,low,fetched`。`fetched` 是抓取日期；`date < fetched` 才算完整 K 线，当天抓到的当日 K 线只是临时值，第二天重抓覆盖。
- 每次只请求"完整 K 线没到昨天"的饰品；API 返回的历史里已经有的完整行不会被改写。
- 换月时上个月的 csv 自动压成 gz。
- 修改 `universe.csv`（`name,cat`，cat ∈ gun_FN / gloves_MW_FT / agent）即可增删饰品，新饰品第二天自动开始取数。

## 六、注意

- **数据时效**：SteamDT 日 K 以北京时间自然日为界，09:30 跑的时候昨天的 K 线已经完整；如果发现报告日期比昨天还早，说明 API 那边尚未生成前一天的 K 线，可把 cron 往后挪。
- **免费额度**：私有仓库每月 2000 分钟 Actions 时长，本项目每天约 18 分钟 + 每月学习任务约 10 分钟，够用；公开仓库不限时长但会暴露你的数据（key 不会暴露，在 Secrets 里）。
- **公开仓库** 60 天没有人为提交会被 GitHub 自动停掉定时任务，私有仓库没有这个限制——这是建议 Private 的另一个原因。
- 报告里的胜率是历史统计，当前是一年来最差的熊市，规则命中数很少是正常的；真实前瞻战绩以 `state/signals.csv` 为准。
