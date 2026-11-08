# 当前研究算法：2月以来逐日假设回放

范围：2026-02-01至2026-10-09。使用归档数据和固定当前规则；不是当时实盘运行结果。
连续口径：2月1日假设全部规则初始active，此后承接状态；新信号扣除同饰品持仓占用。规则实际建立较晚，前瞻恢复起点保留其真实创建日期，因此早期probation可能长期不恢复。
独立口径：每天重新从active评估，对应此前“当前代码放行数”，仅作对照。它不能等同连续运行结果。
早期龙头只观察，未计入买点。无真实订单，无仓位资金约束。当天信号次日真实日K收盘模拟入场，固定H天退出。

| 日期 | 连续扫描去重放行 | 新增模拟信号 | 独立扫描去重放行 |
|---|---:|---:|---:|
| 2026-02-01 | 15 | 15 | 15 |
| 2026-02-02 | 16 | 7 | 16 |
| 2026-02-03 | 18 | 5 | 18 |
| 2026-02-04 | 19 | 3 | 19 |
| 2026-02-05 | 19 | 2 | 19 |
| 2026-02-06 | 17 | 4 | 17 |
| 2026-02-07 | 24 | 8 | 24 |
| 2026-02-08 | 23 | 4 | 23 |
| 2026-02-09 | 48 | 25 | 48 |
| 2026-02-10 | 35 | 5 | 35 |
| 2026-02-11 | 37 | 5 | 37 |
| 2026-02-12 | 43 | 11 | 43 |
| 2026-02-13 | 47 | 6 | 47 |
| 2026-02-14 | 47 | 7 | 47 |
| 2026-02-15 | 47 | 1 | 47 |
| 2026-02-16 | 70 | 21 | 70 |
| 2026-02-17 | 53 | 3 | 53 |
| 2026-02-18 | 54 | 2 | 54 |
| 2026-02-19 | 52 | 2 | 52 |
| 2026-02-20 | 48 | 4 | 48 |
| 2026-02-21 | 39 | 3 | 39 |
| 2026-02-22 | 35 | 3 | 35 |
| 2026-02-23 | 27 | 2 | 27 |
| 2026-02-24 | 25 | 1 | 25 |
| 2026-02-25 | 21 | 2 | 21 |
| 2026-02-26 | 22 | 3 | 22 |
| 2026-02-27 | 21 | 5 | 21 |
| 2026-02-28 | 20 | 4 | 20 |
| 2026-03-01 | 26 | 5 | 26 |
| 2026-03-02 | 34 | 4 | 34 |
| 2026-03-03 | 32 | 4 | 32 |
| 2026-03-04 | 35 | 7 | 35 |
| 2026-03-05 | 32 | 7 | 32 |
| 2026-03-06 | 29 | 5 | 29 |
| 2026-03-07 | 37 | 8 | 37 |
| 2026-03-08 | 56 | 10 | 56 |
| 2026-03-09 | 66 | 9 | 66 |
| 2026-03-10 | 70 | 10 | 70 |
| 2026-03-11 | 81 | 11 | 81 |
| 2026-03-12 | 77 | 14 | 77 |
| 2026-03-13 | 74 | 9 | 74 |
| 2026-03-14 | 69 | 13 | 69 |
| 2026-03-15 | 55 | 7 | 55 |
| 2026-03-16 | 44 | 6 | 44 |
| 2026-03-17 | 38 | 6 | 38 |
| 2026-03-18 | 43 | 9 | 43 |
| 2026-03-19 | 55 | 15 | 55 |
| 2026-03-20 | 67 | 18 | 67 |
| 2026-03-21 | 66 | 15 | 66 |
| 2026-03-22 | 65 | 12 | 65 |
| 2026-03-23 | 72 | 15 | 72 |
| 2026-03-24 | 70 | 9 | 70 |
| 2026-03-25 | 45 | 10 | 45 |
| 2026-03-26 | 56 | 12 | 57 |
| 2026-03-27 | 69 | 10 | 69 |
| 2026-03-28 | 78 | 4 | 78 |
| 2026-03-29 | 86 | 12 | 87 |
| 2026-03-30 | 94 | 7 | 94 |
| 2026-03-31 | 92 | 7 | 93 |
| 2026-04-01 | 93 | 5 | 94 |
| 2026-04-02 | 89 | 5 | 90 |
| 2026-04-03 | 93 | 7 | 94 |
| 2026-04-04 | 87 | 3 | 88 |
| 2026-04-05 | 82 | 3 | 86 |
| 2026-04-06 | 90 | 5 | 96 |
| 2026-04-07 | 95 | 4 | 114 |
| 2026-04-08 | 84 | 5 | 113 |
| 2026-04-09 | 95 | 4 | 125 |
| 2026-04-10 | 93 | 5 | 116 |
| 2026-04-11 | 89 | 3 | 106 |
| 2026-04-12 | 81 | 3 | 97 |
| 2026-04-13 | 73 | 1 | 86 |
| 2026-04-14 | 61 | 2 | 69 |
| 2026-04-15 | 38 | 5 | 40 |
| 2026-04-16 | 32 | 3 | 35 |
| 2026-04-17 | 28 | 1 | 30 |
| 2026-04-18 | 25 | 1 | 26 |
| 2026-04-19 | 24 | 1 | 25 |
| 2026-04-20 | 14 | 0 | 15 |
| 2026-04-21 | 4 | 0 | 6 |
| 2026-04-22 | 9 | 2 | 10 |
| 2026-04-23 | 8 | 1 | 9 |
| 2026-04-24 | 5 | 1 | 6 |
| 2026-04-25 | 10 | 3 | 10 |
| 2026-04-26 | 9 | 1 | 9 |
| 2026-04-27 | 9 | 3 | 9 |
| 2026-04-28 | 12 | 4 | 12 |
| 2026-04-29 | 16 | 2 | 16 |
| 2026-04-30 | 18 | 4 | 18 |
| 2026-05-01 | 21 | 3 | 21 |
| 2026-05-02 | 17 | 0 | 19 |
| 2026-05-03 | 21 | 3 | 22 |
| 2026-05-04 | 25 | 6 | 27 |
| 2026-05-05 | 24 | 4 | 26 |
| 2026-05-06 | 21 | 2 | 23 |
| 2026-05-07 | 19 | 1 | 20 |
| 2026-05-08 | 14 | 0 | 17 |
| 2026-05-09 | 12 | 0 | 15 |
| 2026-05-10 | 12 | 2 | 14 |
| 2026-05-11 | 15 | 7 | 17 |
| 2026-05-12 | 16 | 7 | 17 |
| 2026-05-13 | 12 | 2 | 13 |
| 2026-05-14 | 15 | 3 | 15 |
| 2026-05-15 | 6 | 0 | 6 |
| 2026-05-16 | 15 | 4 | 15 |
| 2026-05-17 | 3 | 1 | 3 |
| 2026-05-18 | 5 | 3 | 5 |
| 2026-05-19 | 7 | 3 | 7 |
| 2026-05-20 | 7 | 1 | 7 |
| 2026-05-21 | 18 | 11 | 18 |
| 2026-05-22 | 52 | 43 | 52 |
| 2026-05-23 | 50 | 24 | 50 |
| 2026-05-24 | 52 | 27 | 52 |
| 2026-05-25 | 78 | 54 | 78 |
| 2026-05-26 | 91 | 45 | 91 |
| 2026-05-27 | 39 | 23 | 39 |
| 2026-05-28 | 0 | 0 | 0 |
| 2026-05-29 | 0 | 0 | 0 |
| 2026-05-30 | 0 | 0 | 0 |
| 2026-05-31 | 0 | 0 | 0 |
| 2026-06-01 | 0 | 0 | 0 |
| 2026-06-02 | 0 | 0 | 0 |
| 2026-06-03 | 0 | 0 | 0 |
| 2026-06-04 | 0 | 0 | 0 |
| 2026-06-05 | 0 | 0 | 0 |
| 2026-06-06 | 0 | 0 | 3 |
| 2026-06-07 | 0 | 0 | 2 |
| 2026-06-08 | 0 | 0 | 1 |
| 2026-06-09 | 0 | 0 | 1 |
| 2026-06-10 | 0 | 0 | 5 |
| 2026-06-11 | 0 | 0 | 21 |
| 2026-06-12 | 0 | 0 | 30 |
| 2026-06-13 | 0 | 0 | 44 |
| 2026-06-14 | 0 | 0 | 59 |
| 2026-06-15 | 0 | 0 | 67 |
| 2026-06-16 | 0 | 0 | 59 |
| 2026-06-17 | 0 | 0 | 79 |
| 2026-06-18 | 0 | 0 | 102 |
| 2026-06-19 | 0 | 0 | 110 |
| 2026-06-20 | 0 | 0 | 108 |
| 2026-06-21 | 0 | 0 | 124 |
| 2026-06-22 | 0 | 0 | 96 |
| 2026-06-23 | 0 | 0 | 82 |
| 2026-06-24 | 0 | 0 | 63 |
| 2026-06-25 | 0 | 0 | 54 |
| 2026-06-26 | 0 | 0 | 52 |
| 2026-06-27 | 0 | 0 | 47 |
| 2026-06-28 | 0 | 0 | 45 |
| 2026-06-29 | 0 | 0 | 49 |
| 2026-06-30 | 0 | 0 | 38 |
| 2026-07-01 | 0 | 0 | 49 |
| 2026-07-02 | 0 | 0 | 32 |
| 2026-07-03 | 0 | 0 | 22 |
| 2026-07-04 | 0 | 0 | 20 |
| 2026-07-05 | 0 | 0 | 25 |
| 2026-07-06 | 0 | 0 | 19 |
| 2026-07-07 | 0 | 0 | 21 |
| 2026-07-08 | 0 | 0 | 20 |
| 2026-07-09 | 0 | 0 | 16 |
| 2026-07-10 | 0 | 0 | 17 |
| 2026-07-11 | 0 | 0 | 14 |
| 2026-07-12 | 0 | 0 | 9 |
| 2026-07-13 | 0 | 0 | 1 |
| 2026-07-14 | 0 | 0 | 14 |
| 2026-07-15 | 0 | 0 | 4 |
| 2026-07-16 | 0 | 0 | 6 |
| 2026-07-17 | 0 | 0 | 9 |
| 2026-07-18 | 0 | 0 | 14 |
| 2026-07-19 | 0 | 0 | 9 |
| 2026-07-20 | 0 | 0 | 7 |
| 2026-07-21 | 0 | 0 | 8 |
| 2026-07-22 | 0 | 0 | 6 |
| 2026-07-23 | 0 | 0 | 6 |
| 2026-07-24 | 0 | 0 | 6 |
| 2026-07-25 | 0 | 0 | 7 |
| 2026-07-26 | 0 | 0 | 0 |
| 2026-07-27 | 0 | 0 | 0 |
| 2026-07-28 | 0 | 0 | 0 |
| 2026-07-29 | 0 | 0 | 0 |
| 2026-07-30 | 0 | 0 | 0 |
| 2026-07-31 | 0 | 0 | 0 |
| 2026-08-01 | 0 | 0 | 9 |
| 2026-08-02 | 0 | 0 | 6 |
| 2026-08-03 | 0 | 0 | 8 |
| 2026-08-04 | 0 | 0 | 12 |
| 2026-08-05 | 0 | 0 | 16 |
| 2026-08-06 | 0 | 0 | 10 |
| 2026-08-07 | 0 | 0 | 8 |
| 2026-08-08 | 0 | 0 | 11 |
| 2026-08-09 | 0 | 0 | 12 |
| 2026-08-10 | 0 | 0 | 11 |
| 2026-08-11 | 0 | 0 | 9 |
| 2026-08-12 | 0 | 0 | 7 |
| 2026-08-13 | 0 | 0 | 10 |
| 2026-08-14 | 0 | 0 | 7 |
| 2026-08-15 | 0 | 0 | 10 |
| 2026-08-16 | 0 | 0 | 0 |
| 2026-08-17 | 0 | 0 | 0 |
| 2026-08-18 | 0 | 0 | 0 |
| 2026-08-19 | 0 | 0 | 0 |
| 2026-08-20 | 0 | 0 | 0 |
| 2026-08-21 | 0 | 0 | 0 |
| 2026-08-22 | 0 | 0 | 0 |
| 2026-08-23 | 0 | 0 | 0 |
| 2026-08-24 | 0 | 0 | 0 |
| 2026-08-25 | 0 | 0 | 0 |
| 2026-08-26 | 0 | 0 | 0 |
| 2026-08-27 | 0 | 0 | 0 |
| 2026-08-28 | 0 | 0 | 0 |
| 2026-08-29 | 0 | 0 | 0 |
| 2026-08-30 | 0 | 0 | 0 |
| 2026-08-31 | 0 | 0 | 0 |
| 2026-09-01 | 0 | 0 | 0 |
| 2026-09-02 | 0 | 0 | 0 |
| 2026-09-03 | 0 | 0 | 0 |
| 2026-09-04 | 0 | 0 | 0 |
| 2026-09-05 | 0 | 0 | 13 |
| 2026-09-06 | 0 | 0 | 11 |
| 2026-09-07 | 0 | 0 | 0 |
| 2026-09-08 | 0 | 0 | 11 |
| 2026-09-09 | 0 | 0 | 0 |
| 2026-09-10 | 0 | 0 | 5 |
| 2026-09-11 | 0 | 0 | 7 |
| 2026-09-12 | 0 | 0 | 7 |
| 2026-09-13 | 0 | 0 | 6 |
| 2026-09-14 | 0 | 0 | 2 |
| 2026-09-15 | 0 | 0 | 2 |
| 2026-09-16 | 0 | 0 | 1 |
| 2026-09-17 | 0 | 0 | 0 |
| 2026-09-18 | 0 | 0 | 0 |
| 2026-09-19 | 0 | 0 | 0 |
| 2026-09-20 | 0 | 0 | 0 |
| 2026-09-21 | 0 | 0 | 0 |
| 2026-09-22 | 0 | 0 | 0 |
| 2026-09-23 | 0 | 0 | 0 |
| 2026-09-24 | 0 | 0 | 0 |
| 2026-09-25 | 0 | 0 | 0 |
| 2026-09-26 | 0 | 0 | 0 |
| 2026-09-27 | 0 | 0 | 0 |
| 2026-09-28 | 0 | 0 | 0 |
| 2026-09-29 | 0 | 0 | 0 |
| 2026-09-30 | 0 | 0 | 0 |
| 2026-10-01 | 0 | 0 | 0 |
| 2026-10-02 | 0 | 0 | 0 |
| 2026-10-03 | 0 | 0 | 0 |
| 2026-10-04 | 0 | 0 | 0 |
| 2026-10-05 | 0 | 0 | 0 |
| 2026-10-06 | 0 | 0 | 0 |
| 2026-10-07 | 0 | 0 | 0 |
| 2026-10-08 | 0 | 0 | 0 |
| 2026-10-09 | 0 | 0 | 0 |

新增模拟信号合计：819条。

## 每日新增具体单品

### 2026-02-01

- SG 553 | Waves Perforated (Factory New)
- MP5-SD | Agent (Field-Tested)
- MAC-10 | Whitefish (Factory New)
- MAG-7 | Popdog (Factory New)
- Desert Eagle | Trigger Discipline (Factory New)
- P250 | Constructivist (Factory New)
- MP9 | Bioleak (Factory New)
- MAC-10 | Classic Crate (Factory New)
- CZ75-Auto | Yellow Jacket (Factory New)
- AWP | Ice Coaled (Factory New)
- PP-Bizon | Harvester (Factory New)
- CZ75-Auto | Copper Fiber (Factory New)
- ★ Bloodhound Gloves | Bronzed (Minimal Wear)
- Galil AR | Cold Fusion (Factory New)
- P250 | Boreal Forest (Factory New)

### 2026-02-02

- MP5-SD | Agent (Minimal Wear)
- P250 | Exchanger (Factory New)
- MAG-7 | Resupply (Factory New)
- R8 Revolver | Nitro (Factory New)
- Glock-18 | Oxide Blaze (Factory New)
- PP-Bizon | Photic Zone (Factory New)
- P2000 | Granite Marbleized (Factory New)

### 2026-02-03

- R8 Revolver | Desert Brush (Factory New)
- ★ Driver Gloves | Diamondback (Field-Tested)
- FAMAS | Teardown (Factory New)
- MAC-10 | Strats (Factory New)
- MAC-10 | Echoing Sands (Factory New)

### 2026-02-04

- FAMAS | Colony (Factory New)
- ★ Driver Gloves | Diamondback (Minimal Wear)
- AWP | Acheron (Factory New)

### 2026-02-05

- ★ Hand Wraps | Spruce DDPAT (Field-Tested)
- UMP-45 | Gunsmoke (Factory New)

### 2026-02-06

- Sawed-Off | Snake Camo (Factory New)
- MP9 | Capillary (Factory New)
- ★ Hand Wraps | Spruce DDPAT (Minimal Wear)
- SSG 08 | Azure Glyph (Factory New)

### 2026-02-07

- AUG | Random Access (Factory New)
- ★ Driver Gloves | Convoy (Field-Tested)
- ★ Bloodhound Gloves | Bronzed (Field-Tested)
- ★ Hand Wraps | Badlands (Minimal Wear)
- P2000 | Red FragCam (Factory New)
- USP-S | Forest Leaves (Factory New)
- Glock-18 | Catacombs (Factory New)
- ★ Bloodhound Gloves | Guerrilla (Field-Tested)

### 2026-02-08

- Tec-9 | Groundwater (Factory New)
- ★ Bloodhound Gloves | Snakebite (Minimal Wear)
- ★ Driver Gloves | Convoy (Minimal Wear)
- SG 553 | Damascus Steel (Factory New)

### 2026-02-09

- CZ75-Auto | Silver (Factory New)
- FAMAS | Decommissioned (Factory New)
- MP7 | Tall Grass (Factory New)
- Dual Berettas | Anodized Navy (Factory New)
- USP-S | Royal Blue (Factory New)
- MP5-SD | Co-Processor (Factory New)
- FAMAS | Styx (Factory New)
- MP5-SD | Liquidation (Factory New)
- P90 | Facility Negative (Factory New)
- Dual Berettas | Twin Turbo (Factory New)
- UMP-45 | Scaffold (Factory New)
- FAMAS | Commemoration (Factory New)
- Dual Berettas | Panther (Factory New)
- R8 Revolver | Desert Brush (Factory New)
- Desert Eagle | The Bronze (Factory New)
- P2000 | Scorpion (Factory New)
- USP-S | Desert Tactical (Factory New)
- Tec-9 | Flash Out (Factory New)
- ★ Hand Wraps | Badlands (Field-Tested)
- Sawed-Off | Brake Light (Factory New)
- ★ Specialist Gloves | Forest DDPAT (Field-Tested)
- ★ Driver Gloves | Lunar Weave (Field-Tested)
- Glock-18 | Sacrifice (Factory New)
- ★ Hand Wraps | Leather (Field-Tested)
- FAMAS | Faulty Wiring (Factory New)

### 2026-02-10

- MP9 | Ruby Poison Dart (Factory New)
- XM1014 | Urban Perforated (Factory New)
- MP9 | Orange Peel (Factory New)
- MAC-10 | Palm (Factory New)
- USP-S | Lead Conduit (Factory New)

### 2026-02-11

- SG 553 | Anodized Navy (Factory New)
- P90 | Cocoa Rampage (Factory New)
- Tec-9 | Urban DDPAT (Factory New)
- AUG | Tom Cat (Factory New)
- MP7 | Urban Hazard (Factory New)

### 2026-02-12

- PP-Bizon | Embargo (Factory New)
- SG 553 | Waves Perforated (Factory New)
- Glock-18 | Wraiths (Factory New)
- SSG 08 | Necropos (Factory New)
- FAMAS | Survivor Z (Factory New)
- MP7 | Akoben (Factory New)
- FAMAS | Crypsis (Factory New)
- MAC-10 | Pipe Down (Factory New)
- Glock-18 | Off World (Factory New)
- AUG | Contractor (Factory New)
- Tec-9 | Titanium Bit (Factory New)

### 2026-02-13

- Five-SeveN | Silver Quartz (Factory New)
- MAC-10 | Rangeen (Factory New)
- P2000 | Urban Hazard (Factory New)
- Five-SeveN | Forest Night (Factory New)
- PP-Bizon | Photic Zone (Factory New)
- MAC-10 | Oceanic (Factory New)

### 2026-02-14

- CZ75-Auto | Tread Plate (Factory New)
- USP-S | 27 (Factory New)
- USP-S | Blood Tiger (Factory New)
- FAMAS | Cyanospatter (Factory New)
- PP-Bizon | Water Sigil (Factory New)
- MAC-10 | Carnivore (Factory New)
- MP9 | Deadly Poison (Factory New)

### 2026-02-15

- Glock-18 | Ironwork (Factory New)

### 2026-02-16

- ★ Sport Gloves | Superconductor (Field-Tested)
- ★ Sport Gloves | Superconductor (Minimal Wear)
- ★ Moto Gloves | Spearmint (Minimal Wear)
- ★ Moto Gloves | Spearmint (Field-Tested)
- MP9 | Dart (Factory New)
- ★ Driver Gloves | King Snake (Minimal Wear)
- ★ Driver Gloves | Racing Green (Field-Tested)
- ★ Specialist Gloves | Crimson Web (Minimal Wear)
- ★ Driver Gloves | Imperial Plaid (Minimal Wear)
- ★ Hand Wraps | Arboreal (Field-Tested)
- ★ Sport Gloves | Pandora's Box (Minimal Wear)
- ★ Specialist Gloves | Mogul (Minimal Wear)
- ★ Hydra Gloves | Rattler (Field-Tested)
- ★ Sport Gloves | Omega (Minimal Wear)
- ★ Driver Gloves | Queen Jaguar (Field-Tested)
- ★ Moto Gloves | Finish Line (Minimal Wear)
- MP9 | Bioleak (Factory New)
- ★ Hand Wraps | Duct Tape (Minimal Wear)
- Tec-9 | Cracked Opal (Factory New)
- MP7 | Forest DDPAT (Factory New)
- R8 Revolver | Survivalist (Factory New)

### 2026-02-17

- MAG-7 | Core Breach (Factory New)
- ★ Hand Wraps | Slaughter (Field-Tested)
- ★ Moto Gloves | Eclipse (Field-Tested)

### 2026-02-18

- M4A4 | Etch Lord (Factory New)
- P2000 | Oceanic (Factory New)

### 2026-02-19

- AWP | Acheron (Factory New)
- Five-SeveN | Orange Peel (Factory New)

### 2026-02-20

- MAG-7 | Silver (Factory New)
- ★ Driver Gloves | Racing Green (Minimal Wear)
- UMP-45 | Gunsmoke (Factory New)
- Galil AR | Dusk Ruins (Factory New)

### 2026-02-21

- CZ75-Auto | Hexane (Factory New)
- PP-Bizon | Brass (Factory New)
- P90 | Elite Build (Factory New)

### 2026-02-22

- AUG | Random Access (Factory New)
- P2000 | Panther Camo (Factory New)
- AK-47 | Rat Rod (Factory New)

### 2026-02-23

- M4A1-S | Boreal Forest (Factory New)
- FAMAS | Afterimage (Factory New)

### 2026-02-24

- MP7 | Astrolabe (Factory New)

### 2026-02-25

- SG 553 | Cyrex (Factory New)
- P2000 | Granite Marbleized (Factory New)

### 2026-02-26

- P90 | Off World (Factory New)
- USP-S | Forest Leaves (Factory New)
- Dual Berettas | Heist (Factory New)

### 2026-02-27

- Glock-18 | Wraiths (Factory New)
- MP7 | Sunbaked (Factory New)
- P250 | Sand Dune (Factory New)
- Dual Berettas | Panther (Factory New)
- P2000 | Red FragCam (Factory New)

### 2026-02-28

- PP-Bizon | Cobalt Halftone (Factory New)
- PP-Bizon | Photic Zone (Factory New)
- XM1014 | Oxide Blaze (Factory New)
- FAMAS | CaliCamo (Factory New)

### 2026-03-01

- Five-SeveN | Buddy (Factory New)
- R8 Revolver | Amber Fade (Factory New)
- MAG-7 | Popdog (Factory New)
- MAC-10 | Pipe Down (Factory New)
- CZ75-Auto | Tread Plate (Factory New)

### 2026-03-02

- M4A1-S | Guardian (Factory New)
- P250 | Inferno (Factory New)
- P2000 | Pulse (Factory New)
- SG 553 | Dragon Tech (Factory New)

### 2026-03-03

- XM1014 | Hieroglyph (Factory New)
- MP9 | Capillary (Factory New)
- MP9 | Modest Threat (Factory New)
- AK-47 | Safari Mesh (Factory New)

### 2026-03-04

- Dragomir | Sabre Footsoldier
- Dual Berettas | Oil Change (Factory New)
- P250 | Boreal Forest (Factory New)
- M4A4 | Daybreak (Factory New)
- SSG 08 | Acid Fade (Factory New)
- PP-Bizon | Runic (Factory New)
- SG 553 | Heavy Metal (Factory New)

### 2026-03-05

- MAG-7 | Heat (Factory New)
- SG 553 | Candy Apple (Factory New)
- SCAR-20 | Trail Blazer (Factory New)
- MAG-7 | Resupply (Factory New)
- CZ75-Auto | Yellow Jacket (Factory New)
- USP-S | Check Engine (Factory New)
- P250 | Exchanger (Factory New)

### 2026-03-06

- AWP | Acheron (Factory New)
- AK-47 | Steel Delta (Factory New)
- MP5-SD | Statics (Factory New)
- Desert Eagle | Trigger Discipline (Factory New)
- R8 Revolver | Bone Mask (Factory New)

### 2026-03-07

- USP-S | Night Ops (Factory New)
- P90 | Module (Factory New)
- Galil AR | Cold Fusion (Factory New)
- P250 | Red Tide (Factory New)
- UMP-45 | Moonrise (Factory New)
- MAC-10 | Echoing Sands (Factory New)
- SG 553 | Integrale (Factory New)
- MP7 | Neon Ply (Factory New)

### 2026-03-08

- M4A4 | Converter (Factory New)
- FAMAS | Crypsis (Factory New)
- FAMAS | Teardown (Factory New)
- P90 | Blind Spot (Factory New)
- SCAR-20 | Assault (Factory New)
- FAMAS | Colony (Factory New)
- MAC-10 | Sienna Damask (Factory New)
- Galil AR | Sage Spray (Factory New)
- Glock-18 | Coral Bloom (Factory New)
- SG 553 | Cyberforce (Factory New)

### 2026-03-09

- MAC-10 | Button Masher (Factory New)
- UMP-45 | Plastique (Factory New)
- MP9 | Ruby Poison Dart (Factory New)
- G3SG1 | Ventilator (Factory New)
- Glock-18 | Ironwork (Factory New)
- CZ75-Auto | Hexane (Factory New)
- AUG | Random Access (Factory New)
- P2000 | Royal Baroque (Factory New)
- Galil AR | Akoben (Factory New)

### 2026-03-10

- AK-47 | Aquamarine Revenge (Factory New)
- MP5-SD | Agent (Factory New)
- P250 | Verdigris (Factory New)
- MAC-10 | Lapis Gator (Factory New)
- MP7 | Just Smile (Factory New)
- SSG 08 | Hand Brake (Factory New)
- MAC-10 | Classic Crate (Factory New)
- P90 | Mustard Gas (Factory New)
- MP5-SD | Gauss (Factory New)
- MAC-10 | Whitefish (Factory New)

### 2026-03-11

- Sawed-Off | Clay Ambush (Factory New)
- MP9 | Dark Age (Factory New)
- Dual Berettas | Rose Nacre (Factory New)
- R8 Revolver | Nitro (Factory New)
- Sawed-Off | Snake Camo (Factory New)
- SG 553 | Damascus Steel (Factory New)
- P90 | Elite Build (Factory New)
- SG 553 | Fallout Warning (Factory New)
- P250 | Iron Clad (Factory New)
- Five-SeveN | Violent Daimyo (Factory New)
- MAG-7 | Foresight (Factory New)

### 2026-03-12

- MP7 | Tall Grass (Factory New)
- P90 | Facility Negative (Factory New)
- MP5-SD | Co-Processor (Factory New)
- Glock-18 | Sacrifice (Factory New)
- FAMAS | Commemoration (Factory New)
- Sawed-Off | Full Stop (Factory New)
- Tec-9 | Garter-9 (Factory New)
- UMP-45 | Scaffold (Factory New)
- USP-S | Desert Tactical (Factory New)
- AUG | Condemned (Factory New)
- AUG | Amber Slipstream (Factory New)
- AUG | Amber Fade (Factory New)
- Tec-9 | Slag (Factory New)
- Tec-9 | Brother (Factory New)

### 2026-03-13

- UMP-45 | Riot (Factory New)
- MP7 | Forest DDPAT (Factory New)
- Sawed-Off | Brake Light (Factory New)
- AUG | Radiation Hazard (Factory New)
- PP-Bizon | Urban Dashed (Factory New)
- AUG | Luxe Trim (Factory New)
- MP9 | Sand Scale (Factory New)
- MP9 | Black Sand (Factory New)
- MP5-SD | Phosphor (Factory New)

### 2026-03-14

- 'Two Times' McCoy | USAF TACP
- FAMAS | Meow 36 (Factory New)
- MP7 | Urban Hazard (Factory New)
- M4A1-S | Atomic Alloy (Factory New)
- MP5-SD | Liquidation (Factory New)
- Dual Berettas | Anodized Navy (Factory New)
- P90 | Teardown (Factory New)
- CZ75-Auto | Silver (Factory New)
- SG 553 | Anodized Navy (Factory New)
- G3SG1 | Orange Crash (Factory New)
- SSG 08 | Tiger Tear (Factory New)
- P250 | Sand Dune (Factory New)
- UMP-45 | Gunsmoke (Factory New)

### 2026-03-15

- M4A4 | Poly Mag (Factory New)
- MP5-SD | Bamboo Garden (Factory New)
- SG 553 | Waves Perforated (Factory New)
- Tec-9 | Red Quartz (Factory New)
- SCAR-20 | Torn (Factory New)
- P90 | Wash me (Factory New)
- P250 | Cassette (Factory New)

### 2026-03-16

- R8 Revolver | Junk Yard (Factory New)
- MP9 | Army Sheen (Factory New)
- XM1014 | Quicksilver (Factory New)
- XM1014 | Blue Steel (Factory New)
- G3SG1 | Polar Camo (Factory New)
- SG 553 | Bleached (Factory New)

### 2026-03-17

- Five-SeveN | Silver Quartz (Factory New)
- MP9 | Deadly Poison (Factory New)
- PP-Bizon | Night Ops (Factory New)
- Glock-18 | Ramese's Reach (Factory New)
- PP-Bizon | Water Sigil (Factory New)
- SG 553 | Danger Close (Factory New)

### 2026-03-18

- MAG-7 | Heaven Guard (Factory New)
- MP7 | Armor Core (Factory New)
- UMP-45 | Urban DDPAT (Factory New)
- M4A1-S | VariCamo (Factory New)
- P90 | Vent Rush (Factory New)
- MP5-SD | Agent (Field-Tested)
- P90 | Death Grip (Factory New)
- Galil AR | Amber Fade (Factory New)
- Five-SeveN | Hybrid (Factory New)

### 2026-03-19

- Chem-Haz Specialist | SWAT
- P2000 | Gnarled (Factory New)
- Five-SeveN | Flame Test (Factory New)
- PP-Bizon | Night Riot (Factory New)
- AK-47 | Uncharted (Factory New)
- SCAR-20 | Blueprint (Factory New)
- MP9 | Setting Sun (Factory New)
- Dual Berettas | Twin Turbo (Factory New)
- AWP | Exoskeleton (Factory New)
- P2000 | Lifted Spirits (Factory New)
- USP-S | Lead Conduit (Factory New)
- AWP | Elite Build (Factory New)
- Five-SeveN | Boost Protocol (Factory New)
- Desert Eagle | Blue Ply (Factory New)
- Desert Eagle | Cobalt Disruption (Factory New)

### 2026-03-20

- R8 Revolver | Bone Forged (Factory New)
- Glock-18 | Catacombs (Factory New)
- CZ75-Auto | Circaetus (Factory New)
- XM1014 | Black Tie (Factory New)
- P250 | X-Ray (Factory New)
- MAC-10 | Acid Hex (Factory New)
- MAG-7 | Core Breach (Factory New)
- XM1014 | Slipstream (Factory New)
- Dual Berettas | Briar (Factory New)
- P2000 | Red Wing (Factory New)
- MP9 | Goo (Factory New)
- MAC-10 | Oceanic (Factory New)
- P90 | Cocoa Rampage (Factory New)
- FAMAS | Decommissioned (Factory New)
- Desert Eagle | The Bronze (Factory New)
- CZ75-Auto | Copper Fiber (Factory New)
- FAMAS | Yeti Camo (Factory New)
- MP7 | Vault Heist (Factory New)

### 2026-03-21

- MP9 | Sand Dashed (Factory New)
- Zeus x27 | Electric Blue (Factory New)
- P90 | Ancient Earth (Factory New)
- SSG 08 | Mainframe 001 (Factory New)
- Tec-9 | Blast From the Past (Factory New)
- Five-SeveN | Capillary (Factory New)
- MP9 | Stained Glass (Factory New)
- AWP | Acheron (Factory New)
- MP9 | Shredded (Factory New)
- UMP-45 | Full Stop (Factory New)
- ★ Bloodhound Gloves | Bronzed (Field-Tested)
- Glock-18 | Royal Legion (Factory New)
- Desert Eagle | Corinthian (Factory New)
- Dual Berettas | Cobra Strike (Factory New)
- SSG 08 | Necropos (Factory New)

### 2026-03-22

- PP-Bizon | Anolis (Factory New)
- SG 553 | Ol' Rusty (Factory New)
- Glock-18 | Clear Polymer (Factory New)
- Glock-18 | Off World (Factory New)
- Dual Berettas | Balance (Factory New)
- MP5-SD | Desert Strike (Factory New)
- P2000 | Acid Etched (Factory New)
- Dual Berettas | Tread (Factory New)
- P2000 | Marsh (Factory New)
- FAMAS | Rapid Eye Movement (Factory New)
- Desert Eagle | Urban DDPAT (Factory New)
- AK-47 | Orbit Mk01 (Factory New)

### 2026-03-23

- SSG 08 | Blue Spruce (Factory New)
- MP7 | Sunbaked (Factory New)
- AUG | Storm (Factory New)
- P2000 | Urban Hazard (Factory New)
- R8 Revolver | Grip (Factory New)
- MP7 | Prey (Factory New)
- MP7 | Akoben (Factory New)
- AUG | Tom Cat (Factory New)
- MAC-10 | Palm (Factory New)
- CZ75-Auto | Syndicate (Factory New)
- Galil AR | Tornado (Factory New)
- Galil AR | Destroyer (Factory New)
- P2000 | Coral Halftone (Factory New)
- Sawed-Off | Forest DDPAT (Factory New)
- Dual Berettas | Royal Consorts (Factory New)

### 2026-03-24

- PP-Bizon | Jungle Slipstream (Factory New)
- P90 | Verdant Growth (Factory New)
- SSG 08 | Prey (Factory New)
- Sawed-Off | Origami (Factory New)
- MP5-SD | Agent (Minimal Wear)
- R8 Revolver | Survivalist (Factory New)
- XM1014 | Gum Wall Camo (Factory New)
- P2000 | Pathfinder (Factory New)
- SCAR-20 | Green Marine (Factory New)

### 2026-03-25

- M4A4 | Etch Lord (Factory New)
- AK-47 | Rat Rod (Factory New)
- ★ Broken Fang Gloves | Yellow-banded (Field-Tested)
- ★ Broken Fang Gloves | Needle Point (Minimal Wear)
- G3SG1 | Murky (Factory New)
- CZ75-Auto | The Fuschia Is Now (Factory New)
- UMP-45 | Gold Bismuth (Factory New)
- USP-S | Orange Anolis (Factory New)
- ★ Moto Gloves | Finish Line (Minimal Wear)
- ★ Hand Wraps | Desert Shamagh (Minimal Wear)

### 2026-03-26

- Dual Berettas | Stained (Factory New)
- PP-Bizon | Jungle Slipstream (Factory New)
- G3SG1 | Jungle Dashed (Factory New)
- MAG-7 | Cobalt Core (Factory New)
- UMP-45 | Motorized (Factory New)
- MAC-10 | Calf Skin (Factory New)
- Dual Berettas | Cobalt Quartz (Factory New)
- P250 | Ripple (Factory New)
- P2000 | Ivory (Factory New)
- M4A1-S | Boreal Forest (Factory New)
- USP-S | Overgrowth (Factory New)
- ★ Moto Gloves | 3rd Commando Company (Minimal Wear)

### 2026-03-27

- FAMAS | Half Sleeve (Factory New)
- MAG-7 | Navy Sheen (Factory New)
- Dual Berettas | Shred (Factory New)
- Tec-9 | Rebel (Factory New)
- Sawed-Off | Parched (Factory New)
- Sawed-Off | Morris (Factory New)
- SCAR-20 | Jungle Slipstream (Factory New)
- XM1014 | Charter (Factory New)
- Dual Berettas | Ventilators (Factory New)
- UMP-45 | Labyrinth (Factory New)

### 2026-03-28

- MP7 | Anodized Navy (Factory New)
- AUG | Contractor (Factory New)
- Five-SeveN | Scrawl (Factory New)
- USP-S | Purple DDPAT (Factory New)

### 2026-03-29

- P250 | Drought (Factory New)
- MAC-10 | Rangeen (Factory New)
- SG 553 | Aerial (Factory New)
- AUG | Ricochet (Factory New)
- FAMAS | Survivor Z (Factory New)
- Tec-9 | Flash Out (Factory New)
- Galil AR | Signal (Factory New)
- SSG 08 | Azure Glyph (Factory New)
- Dual Berettas | Elite 1.6 (Factory New)
- P90 | Off World (Factory New)
- PP-Bizon | Sand Dashed (Factory New)
- AUG | Surveillance (Factory New)

### 2026-03-30

- P90 | Desert DDPAT (Factory New)
- P2000 | Imperial (Factory New)
- Tec-9 | Groundwater (Factory New)
- Five-SeveN | Scumbria (Factory New)
- SG 553 | Triarch (Factory New)
- UMP-45 | Briefing (Factory New)
- Dual Berettas | Colony (Factory New)

### 2026-03-31

- XM1014 | Oxide Blaze (Factory New)
- MP5-SD | Acid Wash (Factory New)
- P90 | Grim (Factory New)
- Dual Berettas | Hideout (Factory New)
- SCAR-20 | Outbreak (Factory New)
- P250 | Re.built (Factory New)
- XM1014 | Blue Spruce (Factory New)

### 2026-04-01

- SG 553 | Atlas (Factory New)
- Galil AR | Robin's Egg (Factory New)
- UMP-45 | Oscillator (Factory New)
- SG 553 | Aloha (Factory New)
- Galil AR | Acid Dart (Factory New)

### 2026-04-02

- MAG-7 | Justice (Factory New)
- R8 Revolver | Desert Brush (Factory New)
- Sawed-Off | Apocalypto (Factory New)
- MP9 | Bioleak (Factory New)
- USP-S | Flashback (Factory New)

### 2026-04-03

- SG 553 | Dragon Tech (Factory New)
- G3SG1 | Hunter (Factory New)
- MP9 | Modest Threat (Factory New)
- XM1014 | Hieroglyph (Factory New)
- Dual Berettas | Polished Malachite (Factory New)
- SSG 08 | Dezastre (Factory New)
- AWP | Capillary (Factory New)

### 2026-04-04

- Tec-9 | Ice Cap (Factory New)
- Tec-9 | Re-Entry (Factory New)
- Five-SeveN | Silver Quartz (Factory New)

### 2026-04-05

- G3SG1 | Desert Storm (Factory New)
- MAG-7 | Heat (Factory New)
- G3SG1 | Orange Crash (Factory New)

### 2026-04-06

- SCAR-20 | Sand Mesh (Factory New)
- MP5-SD | Agent (Field-Tested)
- SG 553 | Candy Apple (Factory New)
- P90 | Sand Spray (Factory New)
- FAMAS | Djinn (Factory New)

### 2026-04-07

- Glock-18 | Wraiths (Factory New)
- P250 | Bengal Tiger (Factory New)
- Galil AR | Cold Fusion (Factory New)
- MAG-7 | Insomnia (Factory New)

### 2026-04-08

- SCAR-20 | Assault (Factory New)
- FAMAS | Crypsis (Factory New)
- SG 553 | Cyberforce (Factory New)
- FAMAS | Colony (Factory New)
- FAMAS | Teardown (Factory New)

### 2026-04-09

- P90 | Verdant Growth (Factory New)
- FAMAS | Halftone Wash (Factory New)
- P2000 | Sure Grip (Factory New)
- MP9 | Cobalt Paisley (Factory New)

### 2026-04-10

- SSG 08 | Hand Brake (Factory New)
- SCAR-20 | Grotto (Factory New)
- MAG-7 | Popdog (Factory New)
- P90 | Module (Factory New)
- Desert Eagle | Urban Rubble (Factory New)

### 2026-04-11

- P90 | Freight (Factory New)
- Sawed-Off | Snake Camo (Factory New)
- Dual Berettas | Rose Nacre (Factory New)

### 2026-04-12

- Tec-9 | Garter-9 (Factory New)
- AUG | Amber Slipstream (Factory New)
- Desert Eagle | Mint Fan (Factory New)

### 2026-04-13

- XM1014 | Urban Perforated (Factory New)

### 2026-04-14

- FAMAS | Meow 36 (Factory New)
- SCAR-20 | Trail Blazer (Factory New)

### 2026-04-15

- ★ Driver Gloves | Lunar Weave (Field-Tested)
- Tec-9 | Red Quartz (Factory New)
- Galil AR | Dusk Ruins (Factory New)
- MP9 | Setting Sun (Factory New)
- SSG 08 | Fever Dream (Factory New)

### 2026-04-16

- Chem-Haz Capitaine | Gendarmerie Nationale
- XM1014 | Blue Steel (Factory New)
- P2000 | Imperial Dragon (Factory New)

### 2026-04-17

- P250 | Red Tide (Factory New)

### 2026-04-18

- MP7 | Armor Core (Factory New)

### 2026-04-19

- P250 | Contamination (Factory New)

### 2026-04-22

- SG 553 | Dragon Tech (Factory New)
- MP9 | Sand Dashed (Factory New)

### 2026-04-23

- Sawed-Off | Forest DDPAT (Factory New)

### 2026-04-24

- Sawed-Off | Black Sand (Factory New)

### 2026-04-25

- SG 553 | Ol' Rusty (Factory New)
- MP9 | Stained Glass (Factory New)
- SG 553 | Anodized Navy (Factory New)

### 2026-04-26

- MAG-7 | Heaven Guard (Factory New)

### 2026-04-27

- MAG-7 | Navy Sheen (Factory New)
- R8 Revolver | Bone Forged (Factory New)
- Dual Berettas | Ventilators (Factory New)

### 2026-04-28

- UMP-45 | Mechanism (Factory New)
- Sawed-Off | Full Stop (Factory New)
- SCAR-20 | Assault (Factory New)
- AUG | Storm (Factory New)

### 2026-04-29

- SG 553 | Danger Close (Factory New)
- G3SG1 | Jungle Dashed (Factory New)

### 2026-04-30

- P90 | Verdant Growth (Factory New)
- SCAR-20 | Jungle Slipstream (Factory New)
- Sawed-Off | Origami (Factory New)
- SCAR-20 | Blueprint (Factory New)

### 2026-05-01

- MP5-SD | Acid Wash (Factory New)
- SCAR-20 | Trail Blazer (Factory New)
- UMP-45 | Riot (Factory New)

### 2026-05-03

- PP-Bizon | Jungle Slipstream (Factory New)
- Glock-18 | Off World (Factory New)
- MP9 | Bioleak (Factory New)

### 2026-05-04

- Dual Berettas | Shred (Factory New)
- PP-Bizon | Night Riot (Factory New)
- G3SG1 | Hunter (Factory New)
- Five-SeveN | Capillary (Factory New)
- XM1014 | Copperflage (Factory New)
- P90 | Off World (Factory New)

### 2026-05-05

- Sawed-Off | Morris (Factory New)
- P2000 | Lifted Spirits (Factory New)
- SG 553 | Aerial (Factory New)
- Dual Berettas | Stained (Factory New)

### 2026-05-06

- XM1014 | Oxide Blaze (Factory New)
- G3SG1 | Desert Storm (Factory New)

### 2026-05-07

- P90 | Sand Spray (Factory New)

### 2026-05-10

- ★ Hand Wraps | Badlands (Minimal Wear)
- USP-S | Purple DDPAT (Factory New)

### 2026-05-11

- Lt. Commander Ricksaw | NSWC SEAL
- Galil AR | Dusk Ruins (Factory New)
- AK-47 | Searing Rage (Factory New)
- M4A4 | Hellfire (Factory New)
- ★ Hand Wraps | Spruce DDPAT (Minimal Wear)
- AWP | Crakow! (Factory New)
- ★ Hand Wraps | Leather (Minimal Wear)

### 2026-05-12

- Zeus x27 | Dragon Snore (Factory New)
- XM1014 | Monster Melt (Factory New)
- AK-47 | B the Monster (Factory New)
- MAC-10 | Stalker (Factory New)
- P90 | Reef Grief (Factory New)
- FAMAS | Pulse (Factory New)
- P2000 | Imperial (Factory New)

### 2026-05-13

- Cmdr. Mae 'Dead Cold' Jamison | SWAT
- AWP | Green Energy (Factory New)

### 2026-05-14

- MAC-10 | Poplar Thicket (Factory New)
- ★ Sport Gloves | Arid (Minimal Wear)
- ★ Specialist Gloves | Emerald Web (Field-Tested)

### 2026-05-16

- MP9 | Shredded (Factory New)
- AUG | Eye of Zapems (Factory New)
- M4A1-S | Stratosphere (Factory New)
- ★ Hand Wraps | Slaughter (Field-Tested)

### 2026-05-17

- Glock-18 | Glockingbird (Factory New)

### 2026-05-18

- Glock-18 | Sacrifice (Factory New)
- XM1014 | Gum Wall Camo (Factory New)
- ★ Specialist Gloves | Emerald Web (Minimal Wear)

### 2026-05-19

- MP5-SD | Gold Leaf (Factory New)
- ★ Hand Wraps | Slaughter (Minimal Wear)
- ★ Specialist Gloves | Foundation (Minimal Wear)

### 2026-05-20

- Tec-9 | Citric Acid (Factory New)

### 2026-05-21

- AUG | Creep (Factory New)
- USP-S | Royal Guard (Factory New)
- UMP-45 | Warm Blooded (Factory New)
- AWP | Exothermic (Factory New)
- AWP | The End (Factory New)
- ★ Moto Gloves | Eclipse (Minimal Wear)
- ★ Hand Wraps | Badlands (Field-Tested)
- ★ Hand Wraps | Spruce DDPAT (Field-Tested)
- ★ Driver Gloves | Crimson Weave (Minimal Wear)
- ★ Driver Gloves | Diamondback (Minimal Wear)
- CZ75-Auto | Distressed (Factory New)

### 2026-05-22

- Galil AR | Sky Mandala (Factory New)
- P2000 | Royal Baroque (Factory New)
- USP-S | Bleeding Edge (Factory New)
- AK-47 | Breakthrough (Factory New)
- SSG 08 | Calligrafaux (Factory New)
- Zeus x27 | Earth Mandala (Factory New)
- Five-SeveN | Fraise Crane (Factory New)
- M4A1-S | Glitched Paint (Factory New)
- M4A4 | In Living Color (Factory New)
- Glock-18 | Gamma Doppler (Factory New)
- M4A4 | Royal Paladin (Factory New)
- USP-S | Tropical Breeze (Factory New)
- FAMAS | Commemoration (Factory New)
- USP-S | Orion (Factory New)
- M4A4 | The Emperor (Factory New)
- AK-47 | Cartel (Factory New)
- ★ Specialist Gloves | Foundation (Field-Tested)
- Dual Berettas | Sweet Little Angels (Factory New)
- P250 | Muertos (Factory New)
- M4A1-S | Golden Coil (Factory New)
- ★ Sport Gloves | Arid (Field-Tested)
- MP9 | Rose Iron (Factory New)
- Glock-18 | Bullet Queen (Factory New)
- Desert Eagle | Kumicho Dragon (Factory New)
- ★ Moto Gloves | Boom! (Minimal Wear)
- ★ Driver Gloves | Crimson Weave (Field-Tested)
- MP9 | Deadly Poison (Factory New)
- M4A4 | The Battlestar (Factory New)
- Glock-18 | Winterized (Factory New)
- ★ Driver Gloves | Lunar Weave (Field-Tested)
- MAC-10 | Pipsqueak (Factory New)
- M4A1-S | Decimator (Factory New)
- Dual Berettas | Hemoglobin (Factory New)
- CZ75-Auto | Imprint (Factory New)
- P2000 | Fire Elemental (Factory New)
- M4A4 | Desert-Strike (Factory New)
- Galil AR | Cerberus (Factory New)
- ★ Hand Wraps | Leather (Field-Tested)
- M4A4 | Cyber Security (Factory New)
- ★ Driver Gloves | Diamondback (Field-Tested)
- AUG | Carved Jade (Factory New)
- USP-S | Orange Anolis (Factory New)
- AK-47 | Panthera onca (Factory New)

### 2026-05-23

- Rezan The Ready | Sabre
- SSG 08 | Blush Pour (Factory New)
- Zeus x27 | Tosai (Factory New)
- Five-SeveN | Angry Mob (Factory New)
- Desert Eagle | Tilted (Factory New)
- Desert Eagle | The Daily Deagle (Factory New)
- ★ Driver Gloves | Lunar Weave (Minimal Wear)
- CZ75-Auto | Tacticat (Factory New)
- Galil AR | Sugar Rush (Factory New)
- P2000 | Handgun (Factory New)
- AUG | Death by Puppy (Factory New)
- AK-47 | Frontside Misty (Factory New)
- FAMAS | Valence (Factory New)
- UMP-45 | Plastique (Factory New)
- M4A4 | Desolate Space (Factory New)
- AK-47 | The Outsiders (Factory New)
- Sawed-Off | Serenity (Factory New)
- PP-Bizon | Brass (Factory New)
- ★ Moto Gloves | Finish Line (Minimal Wear)
- MP7 | Impire (Factory New)
- Desert Eagle | Starcade (Factory New)
- Dual Berettas | Anodized Navy (Factory New)
- M4A1-S | Hyper Beast (Factory New)
- Glock-18 | Weasel (Factory New)

### 2026-05-24

- Charm | Lil' SAS
- Galil AR | Stone Cold (Factory New)
- Glock-18 | Coral Bloom (Factory New)
- MP9 | Food Chain (Factory New)
- PP-Bizon | Photic Zone (Factory New)
- Galil AR | Rocket Pop (Factory New)
- Desert Eagle | Serpent Strike (Factory New)
- Glock-18 | Neo-Noir (Factory New)
- Desert Eagle | Golden Koi (Factory New)
- Desert Eagle | Calligraffiti (Factory New)
- P2000 | Imperial Dragon (Factory New)
- USP-S | Monster Mashup (Factory New)
- ★ Bloodhound Gloves | Bronzed (Field-Tested)
- PP-Bizon | Carbon Fiber (Factory New)
- Five-SeveN | Copper Galaxy (Factory New)
- Galil AR | Black Sand (Factory New)
- M4A1-S | Master Piece (Factory New)
- AK-47 | Asiimov (Factory New)
- Glock-18 | Franklin (Factory New)
- Tec-9 | Bamboozle (Factory New)
- Five-SeveN | Forest Night (Factory New)
- Tec-9 | Remote Control (Factory New)
- M4A1-S | Control Panel (Factory New)
- Desert Eagle | Naga (Factory New)
- SSG 08 | Azure Glyph (Factory New)
- Sawed-Off | Parched (Factory New)
- ★ Hand Wraps | CAUTION! (Minimal Wear)

### 2026-05-25

- Col. Mangos Dabisi | Guerrilla Warfare
- Lieutenant 'Tree Hugger' Farlow | SWAT
- M4A4 | Bullet Rain (Factory New)
- FAMAS | Meow 36 (Factory New)
- XM1014 | Copperflage (Factory New)
- M4A1-S | Player Two (Factory New)
- Desert Eagle | Ocean Drive (Factory New)
- Desert Eagle | Heat Treated (Factory New)
- AWP | Printstream (Factory New)
- Dual Berettas | Flora Carnivora (Factory New)
- P250 | Epicenter (Factory New)
- SG 553 | Darkwing (Factory New)
- MP9 | Hypnotic (Factory New)
- M4A1-S | Chantico's Fire (Factory New)
- FAMAS | Decommissioned (Factory New)
- Tec-9 | Decimator (Factory New)
- Five-SeveN | Fairy Tale (Factory New)
- M4A1-S | Moss Quartz (Factory New)
- ★ Moto Gloves | Boom! (Field-Tested)
- Tec-9 | Avalanche (Factory New)
- M4A4 | Tooth Fairy (Factory New)
- P250 | Black & Tan (Factory New)
- P250 | Valence (Factory New)
- MP9 | Arctic Tri-Tone (Factory New)
- P90 | Blind Spot (Factory New)
- MP7 | Cirrus (Factory New)
- AK-47 | Phantom Disruptor (Factory New)
- AUG | Tom Cat (Factory New)
- M4A1-S | VariCamo (Factory New)
- SSG 08 | Rapid Transit (Factory New)
- M4A1-S | Leaded Glass (Factory New)
- SSG 08 | Ghost Crusader (Factory New)
- P2000 | Urban Hazard (Factory New)
- MAC-10 | Fade (Factory New)
- P2000 | Pulse (Factory New)
- AK-47 | X-Ray (Factory New)
- MAG-7 | Copper Coated (Factory New)
- MP9 | Black Sand (Factory New)
- ★ Moto Gloves | Spearmint (Minimal Wear)
- AK-47 | Elite Build (Factory New)
- USP-S | Road Rash (Factory New)
- MAC-10 | Malachite (Factory New)
- Desert Eagle | Fennec Fox (Factory New)
- Tec-9 | Mummy's Rot (Factory New)
- M4A4 | Polysoup (Factory New)
- AWP | Desert Hydra (Factory New)
- AWP | Hyper Beast (Factory New)
- Dual Berettas | Twin Turbo (Factory New)
- ★ Bloodhound Gloves | Snakebite (Field-Tested)
- M4A4 | Global Offensive (Factory New)
- ★ Broken Fang Gloves | Needle Point (Minimal Wear)
- MAG-7 | Sonar (Factory New)
- AK-47 | Baroque Purple (Factory New)
- M4A1-S | Boreal Forest (Factory New)

### 2026-05-26

- 'Two Times' McCoy | USAF TACP
- Arno The Overgrown | Guerrilla Warfare
- Dragomir | Sabre
- Rezan the Redshirt | Sabre
- MAC-10 | Snow Splash (Factory New)
- Glock-18 | Trace Lock (Factory New)
- Tec-9 | Brother (Factory New)
- R8 Revolver | Banana Cannon (Factory New)
- AUG | Syd Mead (Factory New)
- USP-S | Kill Confirmed (Factory New)
- MAC-10 | Disco Tech (Factory New)
- M4A1-S | Vaporwave (Factory New)
- ★ Moto Gloves | Cool Mint (Minimal Wear)
- MP9 | Hot Rod (Factory New)
- Galil AR | Urban Rubble (Factory New)
- USP-S | The Traitor (Factory New)
- FAMAS | Meltdown (Factory New)
- M4A1-S | Atomic Alloy (Factory New)
- M4A4 | Hellish (Factory New)
- MAG-7 | Praetorian (Factory New)
- MAG-7 | Hard Water (Factory New)
- USP-S | Guardian (Factory New)
- UMP-45 | Blaze (Factory New)
- AK-47 | Rat Rod (Factory New)
- Desert Eagle | Corinthian (Factory New)
- MAC-10 | Propaganda (Factory New)
- AK-47 | Orbit Mk01 (Factory New)
- ★ Moto Gloves | Spearmint (Field-Tested)
- Zeus x27 | Charged Up (Factory New)
- P90 | Attack Vector (Factory New)
- AWP | Capillary (Factory New)
- Five-SeveN | Kami (Factory New)
- AUG | Contractor (Factory New)
- SSG 08 | Blood in the Water (Factory New)
- CZ75-Auto | Red Astor (Factory New)
- M4A4 | Evil Daimyo (Factory New)
- SG 553 | Heavy Metal (Factory New)
- XM1014 | Black Tie (Factory New)
- Tec-9 | Cracked Opal (Factory New)
- P250 | Visions (Factory New)
- Tec-9 | Flash Out (Factory New)
- AUG | Amber Fade (Factory New)
- M4A1-S | Party Animal (Factory New)
- ★ Bloodhound Gloves | Charred (Field-Tested)
- CZ75-Auto | Polymer (Factory New)

### 2026-05-27

- P2000 | Sure Grip (Factory New)
- MP5-SD | Phosphor (Factory New)
- PP-Bizon | High Roller (Factory New)
- FAMAS | Bad Trip (Factory New)
- Dual Berettas | Hydro Strike (Factory New)
- MP7 | Coral Paisley (Factory New)
- Sawed-Off | Kiss♥Love (Factory New)
- XM1014 | XOXO (Factory New)
- SSG 08 | Mainframe 001 (Factory New)
- MP7 | Abyssal Apparition (Factory New)
- MAC-10 | Pipe Down (Factory New)
- SG 553 | Dragon Tech (Factory New)
- USP-S | Torque (Factory New)
- MP7 | Special Delivery (Factory New)
- Five-SeveN | Violent Daimyo (Factory New)
- P90 | Neoqueen (Factory New)
- P250 | Dark Filigree (Factory New)
- ★ Driver Gloves | Racing Green (Minimal Wear)
- Tec-9 | Urban DDPAT (Factory New)
- AWP | Arsenic Spill (Factory New)
- MAC-10 | Whitefish (Factory New)
- M4A1-S | Rose Hex (Factory New)
- M4A4 | Poly Mag (Factory New)

## 逐笔信号参数

| 信号日 | 规则 | 饰品 | 信号价 | H天 | 同类强度分 | 龙头候选 |
|---|---|---|---:|---:|---:|---|
| 2026-02-01 | S1 | SG 553 \| Waves Perforated (Factory New) | 3.41 | 10 | 71.9 | 否 |
| 2026-02-01 | L3 | MP5-SD \| Agent (Field-Tested) | 8.96 | 30 | 64.1 | 否 |
| 2026-02-01 | L3 | MAC-10 \| Whitefish (Factory New) | 20.00 | 30 | 58.7 | 否 |
| 2026-02-01 | S1 | MAG-7 \| Popdog (Factory New) | 7.82 | 10 | 54.4 | 否 |
| 2026-02-01 | M4 | Desert Eagle \| Trigger Discipline (Factory New) | 45.80 | 14 | 49.5 | 否 |
| 2026-02-01 | L3 | P250 \| Constructivist (Factory New) | 1.63 | 30 | 42.8 | 否 |
| 2026-02-01 | M4 | MP9 \| Bioleak (Factory New) | 6.36 | 14 | 37.9 | 否 |
| 2026-02-01 | L3 | MAC-10 \| Classic Crate (Factory New) | 18.99 | 30 | 35.1 | 否 |
| 2026-02-01 | S1 | CZ75-Auto \| Yellow Jacket (Factory New) | 274.36 | 10 | 34.3 | 否 |
| 2026-02-01 | S1 | AWP \| Ice Coaled (Factory New) | 426.40 | 10 | 23.5 | 否 |
| 2026-02-01 | L3 | PP-Bizon \| Harvester (Factory New) | 18.59 | 30 | 16.7 | 否 |
| 2026-02-01 | L3 | CZ75-Auto \| Copper Fiber (Factory New) | 1.69 | 30 | 14.8 | 否 |
| 2026-02-01 | M3 | ★ Bloodhound Gloves \| Bronzed (Minimal Wear) | 1450.00 | 14 | 5.0 | 否 |
| 2026-02-01 | L3 | Galil AR \| Cold Fusion (Factory New) | 2.80 | 30 | 3.8 | 否 |
| 2026-02-01 | L3 | P250 \| Boreal Forest (Factory New) | 5.00 | 30 | 2.5 | 否 |
| 2026-02-02 | S1 | MP5-SD \| Agent (Minimal Wear) | 28.00 | 10 | 60.0 | 否 |
| 2026-02-02 | L3 | P250 \| Exchanger (Factory New) | 7.34 | 30 | 58.2 | 否 |
| 2026-02-02 | L3 | MAG-7 \| Resupply (Factory New) | 7.10 | 30 | 49.6 | 否 |
| 2026-02-02 | L3 | R8 Revolver \| Nitro (Factory New) | 20.00 | 30 | 37.8 | 否 |
| 2026-02-02 | L3 | Glock-18 \| Oxide Blaze (Factory New) | 19.00 | 30 | 35.2 | 否 |
| 2026-02-02 | S1 | PP-Bizon \| Photic Zone (Factory New) | 29.00 | 10 | 34.1 | 否 |
| 2026-02-02 | S1 | P2000 \| Granite Marbleized (Factory New) | 15.50 | 10 | 20.5 | 否 |
| 2026-02-03 | L3 | R8 Revolver \| Desert Brush (Factory New) | 9.00 | 30 | 43.3 | 否 |
| 2026-02-03 | M3 | ★ Driver Gloves \| Diamondback (Field-Tested) | 5486.50 | 14 | 33.4 | 否 |
| 2026-02-03 | L3 | FAMAS \| Teardown (Factory New) | 5.85 | 30 | 17.3 | 否 |
| 2026-02-03 | L3 | MAC-10 \| Strats (Factory New) | 14.89 | 30 | 12.8 | 否 |
| 2026-02-03 | L3 | MAC-10 \| Echoing Sands (Factory New) | 20.00 | 30 | 3.9 | 否 |
| 2026-02-04 | L3 | FAMAS \| Colony (Factory New) | 4.70 | 30 | 10.0 | 否 |
| 2026-02-04 | M3 | ★ Driver Gloves \| Diamondback (Minimal Wear) | 5399.00 | 14 | 6.9 | 否 |
| 2026-02-04 | M4 | AWP \| Acheron (Factory New) | 33.57 | 14 | 5.2 | 否 |
| 2026-02-05 | M3 | ★ Hand Wraps \| Spruce DDPAT (Field-Tested) | 3299.99 | 14 | 10.1 | 否 |
| 2026-02-05 | M4 | UMP-45 \| Gunsmoke (Factory New) | 10.20 | 14 | 4.7 | 否 |
| 2026-02-06 | L3 | Sawed-Off \| Snake Camo (Factory New) | 9.63 | 30 | 49.4 | 否 |
| 2026-02-06 | M4 | MP9 \| Capillary (Factory New) | 8.30 | 14 | 35.0 | 否 |
| 2026-02-06 | M3 | ★ Hand Wraps \| Spruce DDPAT (Minimal Wear) | 3448.50 | 14 | 23.9 | 否 |
| 2026-02-06 | L3 | SSG 08 \| Azure Glyph (Factory New) | 18.90 | 30 | 5.8 | 否 |
| 2026-02-07 | M4 | AUG \| Random Access (Factory New) | 66.20 | 14 | 41.3 | 否 |
| 2026-02-07 | M3 | ★ Driver Gloves \| Convoy (Field-Tested) | 2275.40 | 14 | 40.4 | 否 |
| 2026-02-07 | M3 | ★ Bloodhound Gloves \| Bronzed (Field-Tested) | 1277.00 | 14 | 37.5 | 否 |
| 2026-02-07 | M3 | ★ Hand Wraps \| Badlands (Minimal Wear) | 4190.00 | 14 | 33.8 | 否 |
| 2026-02-07 | M4 | P2000 \| Red FragCam (Factory New) | 45.00 | 14 | 33.4 | 否 |
| 2026-02-07 | M4 | USP-S \| Forest Leaves (Factory New) | 42.79 | 14 | 9.2 | 否 |
| 2026-02-07 | L3 | Glock-18 \| Catacombs (Factory New) | 19.70 | 30 | 8.0 | 否 |
| 2026-02-07 | M3 | ★ Bloodhound Gloves \| Guerrilla (Field-Tested) | 1240.00 | 14 | 5.7 | 否 |
| 2026-02-08 | L3 | Tec-9 \| Groundwater (Factory New) | 7.10 | 30 | 56.4 | 否 |
| 2026-02-08 | M3 | ★ Bloodhound Gloves \| Snakebite (Minimal Wear) | 1398.99 | 14 | 48.0 | 否 |
| 2026-02-08 | M3 | ★ Driver Gloves \| Convoy (Minimal Wear) | 2288.00 | 14 | 36.9 | 否 |
| 2026-02-08 | L3 | SG 553 \| Damascus Steel (Factory New) | 10.00 | 30 | 4.5 | 否 |
| 2026-02-09 | L1 | CZ75-Auto \| Silver (Factory New) | 39.40 | 30 | 81.4 | 否 |
| 2026-02-09 | L1 | FAMAS \| Decommissioned (Factory New) | 24.96 | 30 | 79.7 | 是 |
| 2026-02-09 | L1 | MP7 \| Tall Grass (Factory New) | 72.88 | 30 | 76.3 | 是 |
| 2026-02-09 | L1 | Dual Berettas \| Anodized Navy (Factory New) | 119.50 | 30 | 56.5 | 否 |
| 2026-02-09 | L1 | USP-S \| Royal Blue (Factory New) | 721.91 | 30 | 53.4 | 否 |
| 2026-02-09 | L1 | MP5-SD \| Co-Processor (Factory New) | 6.24 | 30 | 50.3 | 否 |
| 2026-02-09 | L1 | FAMAS \| Styx (Factory New) | 770.00 | 30 | 45.3 | 否 |
| 2026-02-09 | L3 | MP5-SD \| Liquidation (Factory New) | 6.89 | 30 | 37.8 | 否 |
| 2026-02-09 | L1 | P90 \| Facility Negative (Factory New) | 6.22 | 30 | 32.1 | 否 |
| 2026-02-09 | L1 | Dual Berettas \| Twin Turbo (Factory New) | 200.00 | 30 | 31.1 | 否 |
| 2026-02-09 | L1 | UMP-45 \| Scaffold (Factory New) | 75.00 | 30 | 30.5 | 否 |
| 2026-02-09 | L1 | FAMAS \| Commemoration (Factory New) | 484.00 | 30 | 28.7 | 否 |
| 2026-02-09 | M4 | Dual Berettas \| Panther (Factory New) | 32.80 | 14 | 22.1 | 否 |
| 2026-02-09 | L1 | R8 Revolver \| Desert Brush (Factory New) | 11.39 | 30 | 18.9 | 否 |
| 2026-02-09 | L1 | Desert Eagle \| The Bronze (Factory New) | 37.30 | 30 | 13.1 | 否 |
| 2026-02-09 | L1 | P2000 \| Scorpion (Factory New) | 359.50 | 30 | 13.1 | 否 |
| 2026-02-09 | L1 | USP-S \| Desert Tactical (Factory New) | 37.79 | 30 | 12.2 | 否 |
| 2026-02-09 | L1 | Tec-9 \| Flash Out (Factory New) | 12.59 | 30 | 11.7 | 否 |
| 2026-02-09 | M3 | ★ Hand Wraps \| Badlands (Field-Tested) | 3787.50 | 14 | 11.2 | 否 |
| 2026-02-09 | L1 | Sawed-Off \| Brake Light (Factory New) | 5.20 | 30 | 9.5 | 否 |
| 2026-02-09 | M3 | ★ Specialist Gloves \| Forest DDPAT (Field-Tested) | 2169.50 | 14 | 5.1 | 否 |
| 2026-02-09 | M3 | ★ Driver Gloves \| Lunar Weave (Field-Tested) | 6645.00 | 14 | 4.4 | 否 |
| 2026-02-09 | L1 | Glock-18 \| Sacrifice (Factory New) | 44.92 | 30 | 3.7 | 否 |
| 2026-02-09 | M3 | ★ Hand Wraps \| Leather (Field-Tested) | 5500.00 | 14 | 3.4 | 否 |
| 2026-02-09 | L1 | FAMAS \| Faulty Wiring (Factory New) | 18.98 | 30 | 3.1 | 否 |
| 2026-02-10 | M4 | MP9 \| Ruby Poison Dart (Factory New) | 50.00 | 14 | 24.2 | 否 |
| 2026-02-10 | L1 | XM1014 \| Urban Perforated (Factory New) | 233.22 | 30 | 16.2 | 否 |
| 2026-02-10 | L3 | MP9 \| Orange Peel (Factory New) | 16.50 | 30 | 14.1 | 否 |
| 2026-02-10 | L3 | MAC-10 \| Palm (Factory New) | 12.10 | 30 | 11.2 | 否 |
| 2026-02-10 | L1 | USP-S \| Lead Conduit (Factory New) | 175.00 | 30 | 2.5 | 否 |
| 2026-02-11 | L1 | SG 553 \| Anodized Navy (Factory New) | 4.60 | 30 | 49.8 | 否 |
| 2026-02-11 | L3 | P90 \| Cocoa Rampage (Factory New) | 18.00 | 30 | 29.6 | 否 |
| 2026-02-11 | L1 | Tec-9 \| Urban DDPAT (Factory New) | 7.50 | 30 | 15.2 | 否 |
| 2026-02-11 | L1 | AUG \| Tom Cat (Factory New) | 5.21 | 30 | 15.0 | 否 |
| 2026-02-11 | L1 | MP7 \| Urban Hazard (Factory New) | 10.14 | 30 | 5.4 | 否 |
| 2026-02-12 | L1 | PP-Bizon \| Embargo (Factory New) | 208.88 | 30 | 60.5 | 否 |
| 2026-02-12 | L3 | SG 553 \| Waves Perforated (Factory New) | 3.17 | 30 | 45.2 | 否 |
| 2026-02-12 | M4 | Glock-18 \| Wraiths (Factory New) | 42.94 | 14 | 40.1 | 否 |
| 2026-02-12 | L1 | SSG 08 \| Necropos (Factory New) | 44.00 | 30 | 37.7 | 否 |
| 2026-02-12 | L3 | FAMAS \| Survivor Z (Factory New) | 9.90 | 30 | 26.6 | 否 |
| 2026-02-12 | L1 | MP7 \| Akoben (Factory New) | 10.30 | 30 | 24.3 | 否 |
| 2026-02-12 | M4 | FAMAS \| Crypsis (Factory New) | 5.73 | 14 | 16.2 | 否 |
| 2026-02-12 | M4 | MAC-10 \| Pipe Down (Factory New) | 46.00 | 14 | 12.5 | 否 |
| 2026-02-12 | L1 | Glock-18 \| Off World (Factory New) | 23.90 | 30 | 8.2 | 否 |
| 2026-02-12 | L1 | AUG \| Contractor (Factory New) | 3.65 | 30 | 4.1 | 否 |
| 2026-02-12 | M4 | Tec-9 \| Titanium Bit (Factory New) | 95.00 | 14 | 3.8 | 否 |
| 2026-02-13 | L3 | Five-SeveN \| Silver Quartz (Factory New) | 4.96 | 30 | 67.4 | 否 |
| 2026-02-13 | L3 | MAC-10 \| Rangeen (Factory New) | 6.47 | 30 | 38.0 | 否 |
| 2026-02-13 | L1 | P2000 \| Urban Hazard (Factory New) | 26.38 | 30 | 29.0 | 否 |
| 2026-02-13 | L3 | Five-SeveN \| Forest Night (Factory New) | 6.19 | 30 | 27.1 | 否 |
| 2026-02-13 | M4 | PP-Bizon \| Photic Zone (Factory New) | 22.74 | 14 | 13.9 | 否 |
| 2026-02-13 | L3 | MAC-10 \| Oceanic (Factory New) | 4.27 | 30 | 3.8 | 否 |
| 2026-02-14 | M4 | CZ75-Auto \| Tread Plate (Factory New) | 53.40 | 14 | 48.4 | 否 |
| 2026-02-14 | M4 | USP-S \| 27 (Factory New) | 31.39 | 14 | 29.1 | 否 |
| 2026-02-14 | M4 | USP-S \| Blood Tiger (Factory New) | 91.30 | 14 | 18.8 | 否 |
| 2026-02-14 | M4 | FAMAS \| Cyanospatter (Factory New) | 15.70 | 14 | 15.8 | 否 |
| 2026-02-14 | L1 | PP-Bizon \| Water Sigil (Factory New) | 33.90 | 30 | 11.4 | 否 |
| 2026-02-14 | L3 | MAC-10 \| Carnivore (Factory New) | 17.47 | 30 | 8.9 | 否 |
| 2026-02-14 | L1 | MP9 \| Deadly Poison (Factory New) | 63.00 | 30 | 6.7 | 否 |
| 2026-02-15 | M3 | Glock-18 \| Ironwork (Factory New) | 56.80 | 14 | 3.0 | 否 |
| 2026-02-16 | RB1 | ★ Sport Gloves \| Superconductor (Field-Tested) | 26287.00 | 14 | 71.5 | 是 |
| 2026-02-16 | RB1 | ★ Sport Gloves \| Superconductor (Minimal Wear) | 35887.50 | 14 | 70.5 | 是 |
| 2026-02-16 | RB1 | ★ Moto Gloves \| Spearmint (Minimal Wear) | 34750.00 | 14 | 69.5 | 否 |
| 2026-02-16 | RB1 | ★ Moto Gloves \| Spearmint (Field-Tested) | 24650.00 | 14 | 62.7 | 否 |
| 2026-02-16 | L3 | MP9 \| Dart (Factory New) | 18.80 | 30 | 57.3 | 否 |
| 2026-02-16 | RB1 | ★ Driver Gloves \| King Snake (Minimal Wear) | 4650.00 | 14 | 56.7 | 否 |
| 2026-02-16 | RB1 | ★ Driver Gloves \| Racing Green (Field-Tested) | 276.44 | 14 | 56.0 | 否 |
| 2026-02-16 | RB1 | ★ Specialist Gloves \| Crimson Web (Minimal Wear) | 2954.00 | 14 | 52.2 | 否 |
| 2026-02-16 | RB1 | ★ Driver Gloves \| Imperial Plaid (Minimal Wear) | 3944.50 | 14 | 49.2 | 否 |
| 2026-02-16 | RB1 | ★ Hand Wraps \| Arboreal (Field-Tested) | 390.00 | 14 | 48.8 | 否 |
| 2026-02-16 | RB1 | ★ Sport Gloves \| Pandora's Box (Minimal Wear) | 59200.00 | 14 | 47.7 | 否 |
| 2026-02-16 | RB1 | ★ Specialist Gloves \| Mogul (Minimal Wear) | 1506.50 | 14 | 46.7 | 否 |
| 2026-02-16 | RB1 | ★ Hydra Gloves \| Rattler (Field-Tested) | 271.98 | 14 | 41.5 | 否 |
| 2026-02-16 | RB1 | ★ Sport Gloves \| Omega (Minimal Wear) | 5141.50 | 14 | 38.8 | 否 |
| 2026-02-16 | RB1 | ★ Driver Gloves \| Queen Jaguar (Field-Tested) | 487.00 | 14 | 36.4 | 否 |
| 2026-02-16 | RB1 | ★ Moto Gloves \| Finish Line (Minimal Wear) | 1757.00 | 14 | 32.0 | 否 |
| 2026-02-16 | L3 | MP9 \| Bioleak (Factory New) | 4.76 | 30 | 26.7 | 否 |
| 2026-02-16 | RB1 | ★ Hand Wraps \| Duct Tape (Minimal Wear) | 735.50 | 14 | 25.7 | 否 |
| 2026-02-16 | L3 | Tec-9 \| Cracked Opal (Factory New) | 14.04 | 30 | 17.3 | 否 |
| 2026-02-16 | M4 | MP7 \| Forest DDPAT (Factory New) | 5.29 | 14 | 16.1 | 否 |
| 2026-02-16 | L1 | R8 Revolver \| Survivalist (Factory New) | 14.89 | 30 | 9.2 | 否 |
| 2026-02-17 | L1 | MAG-7 \| Core Breach (Factory New) | 164.00 | 30 | 74.8 | 是 |
| 2026-02-17 | L1 | ★ Hand Wraps \| Slaughter (Field-Tested) | 8700.00 | 30 | 67.2 | 否 |
| 2026-02-17 | L1 | ★ Moto Gloves \| Eclipse (Field-Tested) | 3697.00 | 30 | 61.2 | 否 |
| 2026-02-18 | M4 | M4A4 \| Etch Lord (Factory New) | 45.00 | 14 | 47.4 | 否 |
| 2026-02-18 | L3 | P2000 \| Oceanic (Factory New) | 5.94 | 30 | 25.3 | 否 |
| 2026-02-19 | M4 | AWP \| Acheron (Factory New) | 31.18 | 14 | 14.6 | 否 |
| 2026-02-19 | L1 | Five-SeveN \| Orange Peel (Factory New) | 20.80 | 30 | 3.3 | 否 |
| 2026-02-20 | L1 | MAG-7 \| Silver (Factory New) | 120.00 | 30 | 60.4 | 否 |
| 2026-02-20 | L1 | ★ Driver Gloves \| Racing Green (Minimal Wear) | 627.00 | 30 | 8.7 | 否 |
| 2026-02-20 | M4 | UMP-45 \| Gunsmoke (Factory New) | 10.20 | 14 | 8.6 | 否 |
| 2026-02-20 | L1 | Galil AR \| Dusk Ruins (Factory New) | 1700.00 | 30 | 3.0 | 否 |
| 2026-02-21 | M4 | CZ75-Auto \| Hexane (Factory New) | 40.80 | 14 | 32.0 | 否 |
| 2026-02-21 | M4 | PP-Bizon \| Brass (Factory New) | 22.18 | 14 | 31.1 | 否 |
| 2026-02-21 | M4 | P90 \| Elite Build (Factory New) | 28.97 | 14 | 7.4 | 否 |
| 2026-02-22 | M4 | AUG \| Random Access (Factory New) | 72.40 | 14 | 46.7 | 否 |
| 2026-02-22 | M4 | P2000 \| Panther Camo (Factory New) | 57.78 | 14 | 15.2 | 否 |
| 2026-02-22 | L1 | AK-47 \| Rat Rod (Factory New) | 974.00 | 30 | 2.0 | 否 |
| 2026-02-23 | L1 | M4A1-S \| Boreal Forest (Factory New) | 129.00 | 30 | 4.4 | 否 |
| 2026-02-23 | L1 | FAMAS \| Afterimage (Factory New) | 789.50 | 30 | 3.1 | 否 |
| 2026-02-24 | M4 | MP7 \| Astrolabe (Factory New) | 16.58 | 14 | 10.4 | 否 |
| 2026-02-25 | L1 | SG 553 \| Cyrex (Factory New) | 273.26 | 30 | 80.6 | 是 |
| 2026-02-25 | L1 | P2000 \| Granite Marbleized (Factory New) | 14.09 | 30 | 10.0 | 否 |
| 2026-02-26 | M4 | P90 \| Off World (Factory New) | 7.00 | 14 | 46.8 | 否 |
| 2026-02-26 | L1 | USP-S \| Forest Leaves (Factory New) | 51.00 | 30 | 42.1 | 否 |
| 2026-02-26 | L1 | Dual Berettas \| Heist (Factory New) | 16.20 | 30 | 33.8 | 否 |
| 2026-02-27 | L1 | Glock-18 \| Wraiths (Factory New) | 49.90 | 30 | 43.2 | 否 |
| 2026-02-27 | M4 | MP7 \| Sunbaked (Factory New) | 7.17 | 14 | 22.0 | 否 |
| 2026-02-27 | M4 | P250 \| Sand Dune (Factory New) | 7.00 | 14 | 21.0 | 否 |
| 2026-02-27 | L1 | Dual Berettas \| Panther (Factory New) | 37.90 | 30 | 15.2 | 否 |
| 2026-02-27 | L1 | P2000 \| Red FragCam (Factory New) | 70.90 | 30 | 4.8 | 否 |
| 2026-02-28 | L1 | PP-Bizon \| Cobalt Halftone (Factory New) | 39.00 | 30 | 96.6 | 是 |
| 2026-02-28 | L1 | PP-Bizon \| Photic Zone (Factory New) | 28.80 | 30 | 73.0 | 是 |
| 2026-02-28 | L1 | XM1014 \| Oxide Blaze (Factory New) | 3.38 | 30 | 68.3 | 否 |
| 2026-02-28 | L1 | FAMAS \| CaliCamo (Factory New) | 44.66 | 30 | 6.2 | 否 |
| 2026-03-01 | L1 | Five-SeveN \| Buddy (Factory New) | 55.70 | 30 | 42.1 | 否 |
| 2026-03-01 | L3 | R8 Revolver \| Amber Fade (Factory New) | 12.35 | 30 | 40.0 | 否 |
| 2026-03-01 | L1 | MAG-7 \| Popdog (Factory New) | 7.69 | 30 | 26.2 | 否 |
| 2026-03-01 | L1 | MAC-10 \| Pipe Down (Factory New) | 53.00 | 30 | 8.7 | 否 |
| 2026-03-01 | L1 | CZ75-Auto \| Tread Plate (Factory New) | 61.70 | 30 | 8.0 | 否 |
| 2026-03-02 | L1 | M4A1-S \| Guardian (Factory New) | 755.00 | 30 | 96.4 | 是 |
| 2026-03-02 | L1 | P250 \| Inferno (Factory New) | 52.90 | 30 | 83.5 | 是 |
| 2026-03-02 | L1 | P2000 \| Pulse (Factory New) | 32.00 | 30 | 55.3 | 否 |
| 2026-03-02 | L3 | SG 553 \| Dragon Tech (Factory New) | 16.90 | 30 | 12.4 | 否 |
| 2026-03-03 | L1 | XM1014 \| Hieroglyph (Factory New) | 4.02 | 30 | 70.4 | 是 |
| 2026-03-03 | L1 | MP9 \| Capillary (Factory New) | 8.54 | 30 | 54.5 | 否 |
| 2026-03-03 | L1 | MP9 \| Modest Threat (Factory New) | 5.00 | 30 | 33.6 | 否 |
| 2026-03-03 | M4 | AK-47 \| Safari Mesh (Factory New) | 78.40 | 14 | 24.9 | 否 |
| 2026-03-04 | L1 | Dragomir \| Sabre Footsoldier | 90.00 | 30 | 100.0 | 是 |
| 2026-03-04 | L3 | Dual Berettas \| Oil Change (Factory New) | 14.90 | 30 | 83.6 | 是 |
| 2026-03-04 | L1 | P250 \| Boreal Forest (Factory New) | 5.87 | 30 | 55.8 | 否 |
| 2026-03-04 | L1 | M4A4 \| Daybreak (Factory New) | 9277.00 | 30 | 48.6 | 否 |
| 2026-03-04 | M4 | SSG 08 \| Acid Fade (Factory New) | 5.13 | 14 | 36.3 | 否 |
| 2026-03-04 | L3 | PP-Bizon \| Runic (Factory New) | 6.87 | 30 | 30.7 | 否 |
| 2026-03-04 | L3 | SG 553 \| Heavy Metal (Factory New) | 8.10 | 30 | 20.4 | 否 |
| 2026-03-05 | L1 | MAG-7 \| Heat (Factory New) | 96.34 | 30 | 98.9 | 是 |
| 2026-03-05 | L1 | SG 553 \| Candy Apple (Factory New) | 107.00 | 30 | 91.1 | 是 |
| 2026-03-05 | L1 | SCAR-20 \| Trail Blazer (Factory New) | 7.57 | 30 | 75.3 | 是 |
| 2026-03-05 | L1 | MAG-7 \| Resupply (Factory New) | 7.93 | 30 | 74.3 | 否 |
| 2026-03-05 | L1 | CZ75-Auto \| Yellow Jacket (Factory New) | 273.35 | 30 | 72.0 | 是 |
| 2026-03-05 | M4 | USP-S \| Check Engine (Factory New) | 12.29 | 14 | 44.2 | 否 |
| 2026-03-05 | L3 | P250 \| Exchanger (Factory New) | 6.42 | 30 | 40.1 | 否 |
| 2026-03-06 | M4 | AWP \| Acheron (Factory New) | 36.66 | 14 | 87.9 | 是 |
| 2026-03-06 | L1 | AK-47 \| Steel Delta (Factory New) | 189.00 | 30 | 76.8 | 是 |
| 2026-03-06 | L1 | MP5-SD \| Statics (Factory New) | 15.17 | 30 | 47.1 | 否 |
| 2026-03-06 | M4 | Desert Eagle \| Trigger Discipline (Factory New) | 46.36 | 14 | 37.0 | 否 |
| 2026-03-06 | L3 | R8 Revolver \| Bone Mask (Factory New) | 5.50 | 30 | 18.9 | 否 |
| 2026-03-07 | L3 | USP-S \| Night Ops (Factory New) | 18.79 | 30 | 78.1 | 是 |
| 2026-03-07 | L1 | P90 \| Module (Factory New) | 16.69 | 30 | 69.4 | 否 |
| 2026-03-07 | L3 | Galil AR \| Cold Fusion (Factory New) | 3.70 | 30 | 64.4 | 否 |
| 2026-03-07 | L1 | P250 \| Red Tide (Factory New) | 20.50 | 30 | 62.9 | 否 |
| 2026-03-07 | L1 | UMP-45 \| Moonrise (Factory New) | 21.00 | 30 | 47.4 | 否 |
| 2026-03-07 | L1 | MAC-10 \| Echoing Sands (Factory New) | 29.30 | 30 | 40.8 | 否 |
| 2026-03-07 | L1 | SG 553 \| Integrale (Factory New) | 833.50 | 30 | 37.8 | 否 |
| 2026-03-07 | L1 | MP7 \| Neon Ply (Factory New) | 499.90 | 30 | 4.3 | 否 |
| 2026-03-08 | L1 | M4A4 \| Converter (Factory New) | 12.20 | 30 | 86.9 | 是 |
| 2026-03-08 | L3 | FAMAS \| Crypsis (Factory New) | 9.66 | 30 | 73.9 | 是 |
| 2026-03-08 | L3 | FAMAS \| Teardown (Factory New) | 9.18 | 30 | 73.6 | 是 |
| 2026-03-08 | L1 | P90 \| Blind Spot (Factory New) | 140.00 | 30 | 72.6 | 是 |
| 2026-03-08 | L1 | SCAR-20 \| Assault (Factory New) | 6.59 | 30 | 66.9 | 否 |
| 2026-03-08 | L3 | FAMAS \| Colony (Factory New) | 12.00 | 30 | 66.9 | 否 |
| 2026-03-08 | L3 | MAC-10 \| Sienna Damask (Factory New) | 7.14 | 30 | 60.0 | 否 |
| 2026-03-08 | L3 | Galil AR \| Sage Spray (Factory New) | 16.40 | 30 | 52.3 | 否 |
| 2026-03-08 | M4 | Glock-18 \| Coral Bloom (Factory New) | 29.81 | 14 | 29.4 | 否 |
| 2026-03-08 | L1 | SG 553 \| Cyberforce (Factory New) | 7.33 | 30 | 15.0 | 否 |
| 2026-03-09 | L1 | MAC-10 \| Button Masher (Factory New) | 54.66 | 30 | 57.4 | 否 |
| 2026-03-09 | L1 | UMP-45 \| Plastique (Factory New) | 47.89 | 30 | 53.3 | 否 |
| 2026-03-09 | L1 | MP9 \| Ruby Poison Dart (Factory New) | 51.38 | 30 | 45.8 | 否 |
| 2026-03-09 | L1 | G3SG1 \| Ventilator (Factory New) | 6.40 | 30 | 45.7 | 否 |
| 2026-03-09 | L1 | Glock-18 \| Ironwork (Factory New) | 92.50 | 30 | 44.0 | 否 |
| 2026-03-09 | L1 | CZ75-Auto \| Hexane (Factory New) | 47.30 | 30 | 40.9 | 否 |
| 2026-03-09 | M4 | AUG \| Random Access (Factory New) | 79.00 | 14 | 36.0 | 否 |
| 2026-03-09 | L1 | P2000 \| Royal Baroque (Factory New) | 16.28 | 30 | 35.3 | 否 |
| 2026-03-09 | L1 | Galil AR \| Akoben (Factory New) | 17.60 | 30 | 15.9 | 否 |
| 2026-03-10 | L1 | AK-47 \| Aquamarine Revenge (Factory New) | 2100.00 | 30 | 81.9 | 是 |
| 2026-03-10 | L1 | MP5-SD \| Agent (Factory New) | 65.80 | 30 | 51.3 | 否 |
| 2026-03-10 | L3 | P250 \| Verdigris (Factory New) | 10.39 | 30 | 44.0 | 否 |
| 2026-03-10 | L1 | MAC-10 \| Lapis Gator (Factory New) | 27.76 | 30 | 42.7 | 否 |
| 2026-03-10 | L1 | MP7 \| Just Smile (Factory New) | 46.74 | 30 | 38.3 | 否 |
| 2026-03-10 | L1 | SSG 08 \| Hand Brake (Factory New) | 31.98 | 30 | 34.8 | 否 |
| 2026-03-10 | L1 | MAC-10 \| Classic Crate (Factory New) | 21.80 | 30 | 34.4 | 否 |
| 2026-03-10 | L3 | P90 \| Mustard Gas (Factory New) | 1.93 | 30 | 33.4 | 否 |
| 2026-03-10 | L1 | MP5-SD \| Gauss (Factory New) | 52.89 | 30 | 21.6 | 否 |
| 2026-03-10 | L1 | MAC-10 \| Whitefish (Factory New) | 23.78 | 30 | 20.0 | 否 |
| 2026-03-11 | L1 | Sawed-Off \| Clay Ambush (Factory New) | 18.18 | 30 | 60.7 | 否 |
| 2026-03-11 | L1 | MP9 \| Dark Age (Factory New) | 736.00 | 30 | 60.5 | 否 |
| 2026-03-11 | L1 | Dual Berettas \| Rose Nacre (Factory New) | 1.93 | 30 | 60.3 | 否 |
| 2026-03-11 | L1 | R8 Revolver \| Nitro (Factory New) | 11.40 | 30 | 42.9 | 否 |
| 2026-03-11 | L3 | Sawed-Off \| Snake Camo (Factory New) | 19.97 | 30 | 42.9 | 否 |
| 2026-03-11 | L1 | SG 553 \| Damascus Steel (Factory New) | 14.00 | 30 | 42.0 | 否 |
| 2026-03-11 | L1 | P90 \| Elite Build (Factory New) | 32.35 | 30 | 35.9 | 否 |
| 2026-03-11 | L1 | SG 553 \| Fallout Warning (Factory New) | 71.64 | 30 | 32.6 | 否 |
| 2026-03-11 | L1 | P250 \| Iron Clad (Factory New) | 39.99 | 30 | 28.3 | 否 |
| 2026-03-11 | L1 | Five-SeveN \| Violent Daimyo (Factory New) | 17.00 | 30 | 26.5 | 否 |
| 2026-03-11 | L1 | MAG-7 \| Foresight (Factory New) | 3.02 | 30 | 24.6 | 否 |
| 2026-03-12 | L1 | MP7 \| Tall Grass (Factory New) | 123.49 | 30 | 77.8 | 否 |
| 2026-03-12 | L1 | P90 \| Facility Negative (Factory New) | 7.29 | 30 | 72.5 | 否 |
| 2026-03-12 | L1 | MP5-SD \| Co-Processor (Factory New) | 7.32 | 30 | 65.5 | 否 |
| 2026-03-12 | L1 | Glock-18 \| Sacrifice (Factory New) | 76.70 | 30 | 63.4 | 否 |
| 2026-03-12 | L1 | FAMAS \| Commemoration (Factory New) | 562.00 | 30 | 50.0 | 否 |
| 2026-03-12 | L1 | Sawed-Off \| Full Stop (Factory New) | 6.30 | 30 | 44.3 | 否 |
| 2026-03-12 | L1 | Tec-9 \| Garter-9 (Factory New) | 2.49 | 30 | 34.7 | 否 |
| 2026-03-12 | L1 | UMP-45 \| Scaffold (Factory New) | 64.99 | 30 | 16.4 | 否 |
| 2026-03-12 | L1 | USP-S \| Desert Tactical (Factory New) | 47.80 | 30 | 13.4 | 否 |
| 2026-03-12 | L1 | AUG \| Condemned (Factory New) | 15.80 | 30 | 11.3 | 否 |
| 2026-03-12 | L1 | AUG \| Amber Slipstream (Factory New) | 6.99 | 30 | 10.9 | 否 |
| 2026-03-12 | L1 | AUG \| Amber Fade (Factory New) | 26.80 | 30 | 10.7 | 否 |
| 2026-03-12 | L1 | Tec-9 \| Slag (Factory New) | 7.28 | 30 | 10.3 | 否 |
| 2026-03-12 | L1 | Tec-9 \| Brother (Factory New) | 41.00 | 30 | 9.4 | 否 |
| 2026-03-13 | L3 | UMP-45 \| Riot (Factory New) | 9.60 | 30 | 71.8 | 是 |
| 2026-03-13 | L1 | MP7 \| Forest DDPAT (Factory New) | 11.00 | 30 | 41.7 | 否 |
| 2026-03-13 | L3 | Sawed-Off \| Brake Light (Factory New) | 6.83 | 30 | 26.7 | 否 |
| 2026-03-13 | L1 | AUG \| Radiation Hazard (Factory New) | 67.00 | 30 | 14.1 | 否 |
| 2026-03-13 | L1 | PP-Bizon \| Urban Dashed (Factory New) | 6.00 | 30 | 12.9 | 否 |
| 2026-03-13 | L1 | AUG \| Luxe Trim (Factory New) | 18.30 | 30 | 9.7 | 否 |
| 2026-03-13 | L1 | MP9 \| Sand Scale (Factory New) | 14.39 | 30 | 8.3 | 否 |
| 2026-03-13 | L1 | MP9 \| Black Sand (Factory New) | 9.90 | 30 | 6.2 | 否 |
| 2026-03-13 | L1 | MP5-SD \| Phosphor (Factory New) | 148.00 | 30 | 5.3 | 否 |
| 2026-03-14 | L1 | 'Two Times' McCoy \| USAF TACP | 81.50 | 30 | 100.0 | 是 |
| 2026-03-14 | L3 | FAMAS \| Meow 36 (Factory New) | 13.40 | 30 | 98.0 | 是 |
| 2026-03-14 | L1 | MP7 \| Urban Hazard (Factory New) | 13.81 | 30 | 59.3 | 否 |
| 2026-03-14 | L1 | M4A1-S \| Atomic Alloy (Factory New) | 2000.00 | 30 | 58.6 | 否 |
| 2026-03-14 | L1 | MP5-SD \| Liquidation (Factory New) | 9.99 | 30 | 51.3 | 否 |
| 2026-03-14 | L1 | Dual Berettas \| Anodized Navy (Factory New) | 116.49 | 30 | 30.5 | 否 |
| 2026-03-14 | L1 | P90 \| Teardown (Factory New) | 6.80 | 30 | 29.7 | 否 |
| 2026-03-14 | M4 | CZ75-Auto \| Silver (Factory New) | 65.00 | 14 | 28.0 | 否 |
| 2026-03-14 | L1 | SG 553 \| Anodized Navy (Factory New) | 4.96 | 30 | 26.3 | 否 |
| 2026-03-14 | M4 | G3SG1 \| Orange Crash (Factory New) | 5.01 | 14 | 22.7 | 否 |
| 2026-03-14 | L3 | SSG 08 \| Tiger Tear (Factory New) | 1.67 | 30 | 12.0 | 否 |
| 2026-03-14 | L1 | P250 \| Sand Dune (Factory New) | 8.42 | 30 | 10.3 | 否 |
| 2026-03-14 | L1 | UMP-45 \| Gunsmoke (Factory New) | 13.99 | 30 | 7.6 | 否 |
| 2026-03-15 | L3 | M4A4 \| Poly Mag (Factory New) | 15.40 | 30 | 73.0 | 是 |
| 2026-03-15 | L1 | MP5-SD \| Bamboo Garden (Factory New) | 55.80 | 30 | 56.8 | 否 |
| 2026-03-15 | L3 | SG 553 \| Waves Perforated (Factory New) | 6.70 | 30 | 38.7 | 否 |
| 2026-03-15 | L1 | Tec-9 \| Red Quartz (Factory New) | 3.96 | 30 | 20.5 | 否 |
| 2026-03-15 | M4 | SCAR-20 \| Torn (Factory New) | 31.67 | 14 | 11.8 | 否 |
| 2026-03-15 | L1 | P90 \| Wash me (Factory New) | 1.45 | 30 | 8.7 | 否 |
| 2026-03-15 | L3 | P250 \| Cassette (Factory New) | 3.17 | 30 | 2.7 | 否 |
| 2026-03-16 | L3 | R8 Revolver \| Junk Yard (Factory New) | 15.90 | 30 | 93.4 | 是 |
| 2026-03-16 | L3 | MP9 \| Army Sheen (Factory New) | 9.99 | 30 | 72.0 | 是 |
| 2026-03-16 | L3 | XM1014 \| Quicksilver (Factory New) | 11.00 | 30 | 40.5 | 否 |
| 2026-03-16 | L1 | XM1014 \| Blue Steel (Factory New) | 5.49 | 30 | 26.0 | 否 |
| 2026-03-16 | L1 | G3SG1 \| Polar Camo (Factory New) | 5.49 | 30 | 24.0 | 否 |
| 2026-03-16 | L1 | SG 553 \| Bleached (Factory New) | 6.28 | 30 | 6.7 | 否 |
| 2026-03-17 | M4 | Five-SeveN \| Silver Quartz (Factory New) | 6.66 | 14 | 33.4 | 否 |
| 2026-03-17 | L1 | MP9 \| Deadly Poison (Factory New) | 84.50 | 30 | 29.5 | 否 |
| 2026-03-17 | L1 | PP-Bizon \| Night Ops (Factory New) | 2.70 | 30 | 29.4 | 否 |
| 2026-03-17 | L1 | Glock-18 \| Ramese's Reach (Factory New) | 1102.00 | 30 | 25.1 | 否 |
| 2026-03-17 | L1 | PP-Bizon \| Water Sigil (Factory New) | 46.99 | 30 | 14.2 | 否 |
| 2026-03-17 | L1 | SG 553 \| Danger Close (Factory New) | 11.00 | 30 | 3.8 | 否 |
| 2026-03-18 | L3 | MAG-7 \| Heaven Guard (Factory New) | 8.90 | 30 | 84.8 | 是 |
| 2026-03-18 | L3 | MP7 \| Armor Core (Factory New) | 18.70 | 30 | 70.9 | 是 |
| 2026-03-18 | L3 | UMP-45 \| Urban DDPAT (Factory New) | 10.00 | 30 | 67.8 | 否 |
| 2026-03-18 | L3 | M4A1-S \| VariCamo (Factory New) | 18.06 | 30 | 42.3 | 否 |
| 2026-03-18 | L1 | P90 \| Vent Rush (Factory New) | 20.48 | 30 | 38.1 | 否 |
| 2026-03-18 | M3 | MP5-SD \| Agent (Field-Tested) | 4.22 | 14 | 36.1 | 否 |
| 2026-03-18 | L1 | P90 \| Death Grip (Factory New) | 439.00 | 30 | 23.5 | 否 |
| 2026-03-18 | L1 | Galil AR \| Amber Fade (Factory New) | 724.50 | 30 | 23.3 | 否 |
| 2026-03-18 | L1 | Five-SeveN \| Hybrid (Factory New) | 58.88 | 30 | 19.5 | 否 |
| 2026-03-19 | L1 | Chem-Haz Specialist \| SWAT | 137.78 | 30 | 100.0 | 否 |
| 2026-03-19 | L3 | P2000 \| Gnarled (Factory New) | 18.00 | 30 | 89.8 | 是 |
| 2026-03-19 | L3 | Five-SeveN \| Flame Test (Factory New) | 11.80 | 30 | 77.7 | 是 |
| 2026-03-19 | L3 | PP-Bizon \| Night Riot (Factory New) | 9.95 | 30 | 73.1 | 是 |
| 2026-03-19 | L1 | AK-47 \| Uncharted (Factory New) | 32.60 | 30 | 59.5 | 否 |
| 2026-03-19 | L1 | SCAR-20 \| Blueprint (Factory New) | 9.39 | 30 | 56.1 | 否 |
| 2026-03-19 | M3 | MP9 \| Setting Sun (Factory New) | 672.29 | 14 | 47.3 | 否 |
| 2026-03-19 | L1 | Dual Berettas \| Twin Turbo (Factory New) | 331.50 | 30 | 40.9 | 否 |
| 2026-03-19 | L1 | AWP \| Exoskeleton (Factory New) | 464.00 | 30 | 40.7 | 否 |
| 2026-03-19 | L3 | P2000 \| Lifted Spirits (Factory New) | 12.00 | 30 | 39.8 | 否 |
| 2026-03-19 | L1 | USP-S \| Lead Conduit (Factory New) | 256.50 | 30 | 38.8 | 否 |
| 2026-03-19 | L1 | AWP \| Elite Build (Factory New) | 3400.00 | 30 | 26.1 | 否 |
| 2026-03-19 | L1 | Five-SeveN \| Boost Protocol (Factory New) | 97.90 | 30 | 11.3 | 否 |
| 2026-03-19 | L1 | Desert Eagle \| Blue Ply (Factory New) | 47.00 | 30 | 10.0 | 否 |
| 2026-03-19 | L1 | Desert Eagle \| Cobalt Disruption (Factory New) | 1259.50 | 30 | 5.6 | 否 |
| 2026-03-20 | L3 | R8 Revolver \| Bone Forged (Factory New) | 9.99 | 30 | 85.0 | 是 |
| 2026-03-20 | L1 | Glock-18 \| Catacombs (Factory New) | 40.00 | 30 | 77.3 | 是 |
| 2026-03-20 | L3 | CZ75-Auto \| Circaetus (Factory New) | 17.98 | 30 | 73.9 | 否 |
| 2026-03-20 | L1 | XM1014 \| Black Tie (Factory New) | 52.45 | 30 | 60.9 | 否 |
| 2026-03-20 | L3 | P250 \| X-Ray (Factory New) | 9.99 | 30 | 59.8 | 否 |
| 2026-03-20 | L1 | MAC-10 \| Acid Hex (Factory New) | 1.88 | 30 | 53.0 | 否 |
| 2026-03-20 | L1 | MAG-7 \| Core Breach (Factory New) | 158.40 | 30 | 44.8 | 否 |
| 2026-03-20 | L3 | XM1014 \| Slipstream (Factory New) | 8.70 | 30 | 43.9 | 否 |
| 2026-03-20 | L1 | Dual Berettas \| Briar (Factory New) | 54.00 | 30 | 41.2 | 否 |
| 2026-03-20 | L1 | P2000 \| Red Wing (Factory New) | 9.00 | 30 | 34.7 | 否 |
| 2026-03-20 | L1 | MP9 \| Goo (Factory New) | 46.00 | 30 | 29.2 | 否 |
| 2026-03-20 | L1 | MAC-10 \| Oceanic (Factory New) | 11.17 | 30 | 22.0 | 否 |
| 2026-03-20 | L1 | P90 \| Cocoa Rampage (Factory New) | 31.00 | 30 | 16.5 | 否 |
| 2026-03-20 | L1 | FAMAS \| Decommissioned (Factory New) | 134.00 | 30 | 10.9 | 否 |
| 2026-03-20 | L1 | Desert Eagle \| The Bronze (Factory New) | 90.70 | 30 | 9.5 | 否 |
| 2026-03-20 | L1 | CZ75-Auto \| Copper Fiber (Factory New) | 2.08 | 30 | 8.4 | 否 |
| 2026-03-20 | L1 | FAMAS \| Yeti Camo (Factory New) | 46.50 | 30 | 6.7 | 否 |
| 2026-03-20 | L1 | MP7 \| Vault Heist (Factory New) | 153.44 | 30 | 5.9 | 否 |
| 2026-03-21 | L3 | MP9 \| Sand Dashed (Factory New) | 14.90 | 30 | 98.9 | 是 |
| 2026-03-21 | L1 | Zeus x27 \| Electric Blue (Factory New) | 3.93 | 30 | 85.0 | 否 |
| 2026-03-21 | L3 | P90 \| Ancient Earth (Factory New) | 18.58 | 30 | 64.7 | 否 |
| 2026-03-21 | L1 | SSG 08 \| Mainframe 001 (Factory New) | 9.86 | 30 | 48.7 | 否 |
| 2026-03-21 | L1 | Tec-9 \| Blast From the Past (Factory New) | 289.99 | 30 | 45.7 | 否 |
| 2026-03-21 | L3 | Five-SeveN \| Capillary (Factory New) | 19.40 | 30 | 41.1 | 否 |
| 2026-03-21 | L1 | MP9 \| Stained Glass (Factory New) | 1745.00 | 30 | 35.2 | 否 |
| 2026-03-21 | L1 | AWP \| Acheron (Factory New) | 51.90 | 30 | 32.3 | 否 |
| 2026-03-21 | L1 | MP9 \| Shredded (Factory New) | 14.00 | 30 | 32.3 | 否 |
| 2026-03-21 | L1 | UMP-45 \| Full Stop (Factory New) | 38.00 | 30 | 30.3 | 否 |
| 2026-03-21 | L1 | ★ Bloodhound Gloves \| Bronzed (Field-Tested) | 1720.00 | 30 | 22.5 | 否 |
| 2026-03-21 | L1 | Glock-18 \| Royal Legion (Factory New) | 609.00 | 30 | 16.9 | 否 |
| 2026-03-21 | L1 | Desert Eagle \| Corinthian (Factory New) | 14.10 | 30 | 15.4 | 否 |
| 2026-03-21 | L1 | Dual Berettas \| Cobra Strike (Factory New) | 1980.00 | 30 | 10.4 | 否 |
| 2026-03-21 | L1 | SSG 08 \| Necropos (Factory New) | 68.80 | 30 | 6.5 | 否 |
| 2026-03-22 | L3 | PP-Bizon \| Anolis (Factory New) | 11.50 | 30 | 86.7 | 是 |
| 2026-03-22 | L3 | SG 553 \| Ol' Rusty (Factory New) | 6.47 | 30 | 58.3 | 否 |
| 2026-03-22 | L1 | Glock-18 \| Clear Polymer (Factory New) | 48.20 | 30 | 43.3 | 否 |
| 2026-03-22 | L1 | Glock-18 \| Off World (Factory New) | 109.50 | 30 | 40.9 | 否 |
| 2026-03-22 | L1 | Dual Berettas \| Balance (Factory New) | 87.99 | 30 | 39.1 | 否 |
| 2026-03-22 | L1 | MP5-SD \| Desert Strike (Factory New) | 13.29 | 30 | 38.2 | 否 |
| 2026-03-22 | L1 | P2000 \| Acid Etched (Factory New) | 207.00 | 30 | 31.5 | 否 |
| 2026-03-22 | L1 | Dual Berettas \| Tread (Factory New) | 65.00 | 30 | 30.9 | 否 |
| 2026-03-22 | L1 | P2000 \| Marsh (Factory New) | 2.25 | 30 | 25.3 | 否 |
| 2026-03-22 | L1 | FAMAS \| Rapid Eye Movement (Factory New) | 260.00 | 30 | 21.4 | 否 |
| 2026-03-22 | L1 | Desert Eagle \| Urban DDPAT (Factory New) | 338.00 | 30 | 8.0 | 否 |
| 2026-03-22 | L1 | AK-47 \| Orbit Mk01 (Factory New) | 1320.00 | 30 | 2.8 | 否 |
| 2026-03-23 | L3 | SSG 08 \| Blue Spruce (Factory New) | 9.79 | 30 | 74.1 | 是 |
| 2026-03-23 | L1 | MP7 \| Sunbaked (Factory New) | 16.40 | 30 | 70.2 | 是 |
| 2026-03-23 | L3 | AUG \| Storm (Factory New) | 18.60 | 30 | 67.6 | 否 |
| 2026-03-23 | L1 | P2000 \| Urban Hazard (Factory New) | 30.89 | 30 | 62.9 | 否 |
| 2026-03-23 | L1 | R8 Revolver \| Grip (Factory New) | 15.00 | 30 | 56.6 | 否 |
| 2026-03-23 | L1 | MP7 \| Prey (Factory New) | 11.60 | 30 | 53.3 | 否 |
| 2026-03-23 | L1 | MP7 \| Akoben (Factory New) | 25.00 | 30 | 52.0 | 否 |
| 2026-03-23 | L3 | AUG \| Tom Cat (Factory New) | 16.00 | 30 | 49.7 | 否 |
| 2026-03-23 | L1 | MAC-10 \| Palm (Factory New) | 37.00 | 30 | 48.7 | 否 |
| 2026-03-23 | L1 | CZ75-Auto \| Syndicate (Factory New) | 258.00 | 30 | 41.6 | 否 |
| 2026-03-23 | L1 | Galil AR \| Tornado (Factory New) | 305.00 | 30 | 39.4 | 否 |
| 2026-03-23 | L1 | Galil AR \| Destroyer (Factory New) | 12.20 | 30 | 30.8 | 否 |
| 2026-03-23 | L3 | P2000 \| Coral Halftone (Factory New) | 5.59 | 30 | 25.5 | 否 |
| 2026-03-23 | L1 | Sawed-Off \| Forest DDPAT (Factory New) | 4.49 | 30 | 14.3 | 否 |
| 2026-03-23 | L1 | Dual Berettas \| Royal Consorts (Factory New) | 118.50 | 30 | 10.0 | 否 |
| 2026-03-24 | L3 | PP-Bizon \| Jungle Slipstream (Factory New) | 14.40 | 30 | 100.0 | 是 |
| 2026-03-24 | M4 | P90 \| Verdant Growth (Factory New) | 60.00 | 14 | 94.2 | 是 |
| 2026-03-24 | L3 | SSG 08 \| Prey (Factory New) | 9.80 | 30 | 72.9 | 是 |
| 2026-03-24 | L1 | Sawed-Off \| Origami (Factory New) | 6.48 | 30 | 64.0 | 否 |
| 2026-03-24 | L1 | MP5-SD \| Agent (Minimal Wear) | 14.90 | 30 | 53.2 | 否 |
| 2026-03-24 | L1 | R8 Revolver \| Survivalist (Factory New) | 23.00 | 30 | 45.8 | 否 |
| 2026-03-24 | L1 | XM1014 \| Gum Wall Camo (Factory New) | 2.26 | 30 | 31.4 | 否 |
| 2026-03-24 | L1 | P2000 \| Pathfinder (Factory New) | 260.00 | 30 | 16.0 | 否 |
| 2026-03-24 | L1 | SCAR-20 \| Green Marine (Factory New) | 18.00 | 30 | 5.3 | 否 |
| 2026-03-25 | L1 | M4A4 \| Etch Lord (Factory New) | 107.00 | 30 | 72.5 | 是 |
| 2026-03-25 | L1 | AK-47 \| Rat Rod (Factory New) | 822.00 | 30 | 44.2 | 否 |
| 2026-03-25 | L1 | ★ Broken Fang Gloves \| Yellow-banded (Field-Tested) | 445.00 | 30 | 44.0 | 否 |
| 2026-03-25 | L1 | ★ Broken Fang Gloves \| Needle Point (Minimal Wear) | 970.00 | 30 | 16.3 | 否 |
| 2026-03-25 | L1 | G3SG1 \| Murky (Factory New) | 23.50 | 30 | 10.0 | 否 |
| 2026-03-25 | L1 | CZ75-Auto \| The Fuschia Is Now (Factory New) | 461.99 | 30 | 9.1 | 否 |
| 2026-03-25 | L1 | UMP-45 \| Gold Bismuth (Factory New) | 217.63 | 30 | 6.9 | 否 |
| 2026-03-25 | L1 | USP-S \| Orange Anolis (Factory New) | 1920.00 | 30 | 4.0 | 否 |
| 2026-03-25 | L1 | ★ Moto Gloves \| Finish Line (Minimal Wear) | 2377.00 | 30 | 2.0 | 否 |
| 2026-03-25 | L1 | ★ Hand Wraps \| Desert Shamagh (Minimal Wear) | 1010.00 | 30 | 1.8 | 否 |
| 2026-03-26 | L3 | Dual Berettas \| Stained (Factory New) | 17.39 | 30 | 99.0 | 是 |
| 2026-03-26 | L3 | PP-Bizon \| Jungle Slipstream (Factory New) | 18.09 | 30 | 95.5 | 是 |
| 2026-03-26 | L3 | G3SG1 \| Jungle Dashed (Factory New) | 13.90 | 30 | 88.4 | 是 |
| 2026-03-26 | L3 | MAG-7 \| Cobalt Core (Factory New) | 18.48 | 30 | 86.7 | 是 |
| 2026-03-26 | L3 | UMP-45 \| Motorized (Factory New) | 7.40 | 30 | 75.3 | 是 |
| 2026-03-26 | L3 | MAC-10 \| Calf Skin (Factory New) | 12.00 | 30 | 71.1 | 是 |
| 2026-03-26 | L3 | Dual Berettas \| Cobalt Quartz (Factory New) | 9.90 | 30 | 65.6 | 否 |
| 2026-03-26 | L3 | P250 \| Ripple (Factory New) | 17.50 | 30 | 45.7 | 否 |
| 2026-03-26 | L1 | P2000 \| Ivory (Factory New) | 89.79 | 30 | 44.8 | 否 |
| 2026-03-26 | L1 | M4A1-S \| Boreal Forest (Factory New) | 228.50 | 30 | 33.8 | 否 |
| 2026-03-26 | L1 | USP-S \| Overgrowth (Factory New) | 819.50 | 30 | 9.6 | 否 |
| 2026-03-26 | L1 | ★ Moto Gloves \| 3rd Commando Company (Minimal Wear) | 1328.00 | 30 | 1.0 | 否 |
| 2026-03-27 | L3 | FAMAS \| Half Sleeve (Factory New) | 9.98 | 30 | 76.1 | 是 |
| 2026-03-27 | L3 | MAG-7 \| Navy Sheen (Factory New) | 13.00 | 30 | 76.0 | 是 |
| 2026-03-27 | L3 | Dual Berettas \| Shred (Factory New) | 18.00 | 30 | 75.3 | 是 |
| 2026-03-27 | L3 | Tec-9 \| Rebel (Factory New) | 17.48 | 30 | 73.8 | 是 |
| 2026-03-27 | L3 | Sawed-Off \| Parched (Factory New) | 12.70 | 30 | 72.6 | 是 |
| 2026-03-27 | L3 | Sawed-Off \| Morris (Factory New) | 18.80 | 30 | 69.8 | 否 |
| 2026-03-27 | L3 | SCAR-20 \| Jungle Slipstream (Factory New) | 9.90 | 30 | 67.9 | 否 |
| 2026-03-27 | L3 | XM1014 \| Charter (Factory New) | 15.00 | 30 | 66.6 | 否 |
| 2026-03-27 | L3 | Dual Berettas \| Ventilators (Factory New) | 13.00 | 30 | 59.7 | 否 |
| 2026-03-27 | L3 | UMP-45 \| Labyrinth (Factory New) | 9.73 | 30 | 46.0 | 否 |
| 2026-03-28 | L1 | MP7 \| Anodized Navy (Factory New) | 12.67 | 30 | 28.7 | 否 |
| 2026-03-28 | L3 | AUG \| Contractor (Factory New) | 20.00 | 30 | 22.1 | 否 |
| 2026-03-28 | L3 | Five-SeveN \| Scrawl (Factory New) | 10.00 | 30 | 8.7 | 否 |
| 2026-03-28 | L1 | USP-S \| Purple DDPAT (Factory New) | 805.00 | 30 | 2.5 | 否 |
| 2026-03-29 | L3 | P250 \| Drought (Factory New) | 14.50 | 30 | 46.8 | 否 |
| 2026-03-29 | L1 | MAC-10 \| Rangeen (Factory New) | 16.78 | 30 | 23.0 | 否 |
| 2026-03-29 | L1 | SG 553 \| Aerial (Factory New) | 10.28 | 30 | 22.6 | 否 |
| 2026-03-29 | L1 | AUG \| Ricochet (Factory New) | 37.00 | 30 | 22.4 | 否 |
| 2026-03-29 | L1 | FAMAS \| Survivor Z (Factory New) | 34.16 | 30 | 18.9 | 否 |
| 2026-03-29 | L1 | Tec-9 \| Flash Out (Factory New) | 41.71 | 30 | 14.7 | 否 |
| 2026-03-29 | L1 | Galil AR \| Signal (Factory New) | 49.90 | 30 | 13.8 | 否 |
| 2026-03-29 | L1 | SSG 08 \| Azure Glyph (Factory New) | 41.00 | 30 | 13.6 | 否 |
| 2026-03-29 | L1 | Dual Berettas \| Elite 1.6 (Factory New) | 18.00 | 30 | 10.9 | 否 |
| 2026-03-29 | L1 | P90 \| Off World (Factory New) | 17.00 | 30 | 9.1 | 否 |
| 2026-03-29 | L1 | PP-Bizon \| Sand Dashed (Factory New) | 11.99 | 30 | 6.0 | 否 |
| 2026-03-29 | L1 | AUG \| Surveillance (Factory New) | 18.60 | 30 | 5.7 | 否 |
| 2026-03-30 | L1 | P90 \| Desert DDPAT (Factory New) | 10.10 | 30 | 52.9 | 否 |
| 2026-03-30 | L1 | P2000 \| Imperial (Factory New) | 28.98 | 30 | 37.9 | 否 |
| 2026-03-30 | L1 | Tec-9 \| Groundwater (Factory New) | 19.76 | 30 | 32.2 | 否 |
| 2026-03-30 | L1 | Five-SeveN \| Scumbria (Factory New) | 68.00 | 30 | 24.8 | 否 |
| 2026-03-30 | L1 | SG 553 \| Triarch (Factory New) | 72.99 | 30 | 14.1 | 否 |
| 2026-03-30 | L1 | UMP-45 \| Briefing (Factory New) | 20.90 | 30 | 4.2 | 否 |
| 2026-03-30 | L1 | Dual Berettas \| Colony (Factory New) | 12.39 | 30 | 2.9 | 否 |
| 2026-03-31 | L1 | XM1014 \| Oxide Blaze (Factory New) | 6.90 | 30 | 68.0 | 否 |
| 2026-03-31 | L1 | MP5-SD \| Acid Wash (Factory New) | 46.90 | 30 | 52.4 | 否 |
| 2026-03-31 | L1 | P90 \| Grim (Factory New) | 13.94 | 30 | 40.6 | 否 |
| 2026-03-31 | L1 | Dual Berettas \| Hideout (Factory New) | 4.67 | 30 | 36.2 | 否 |
| 2026-03-31 | L1 | SCAR-20 \| Outbreak (Factory New) | 9.65 | 30 | 35.5 | 否 |
| 2026-03-31 | L1 | P250 \| Re.built (Factory New) | 9.50 | 30 | 17.6 | 否 |
| 2026-03-31 | L1 | XM1014 \| Blue Spruce (Factory New) | 8.99 | 30 | 10.6 | 否 |
| 2026-04-01 | M4 | SG 553 \| Atlas (Factory New) | 16.78 | 14 | 21.1 | 否 |
| 2026-04-01 | L1 | Galil AR \| Robin's Egg (Factory New) | 3.22 | 30 | 21.1 | 否 |
| 2026-04-01 | M4 | UMP-45 \| Oscillator (Factory New) | 5.00 | 14 | 8.3 | 否 |
| 2026-04-01 | M4 | SG 553 \| Aloha (Factory New) | 5.37 | 14 | 6.5 | 否 |
| 2026-04-01 | L1 | Galil AR \| Acid Dart (Factory New) | 2.76 | 30 | 3.0 | 否 |
| 2026-04-02 | L1 | MAG-7 \| Justice (Factory New) | 393.50 | 30 | 29.2 | 否 |
| 2026-04-02 | L1 | R8 Revolver \| Desert Brush (Factory New) | 14.00 | 30 | 25.5 | 否 |
| 2026-04-02 | M4 | Sawed-Off \| Apocalypto (Factory New) | 57.56 | 14 | 20.7 | 否 |
| 2026-04-02 | L1 | MP9 \| Bioleak (Factory New) | 10.40 | 30 | 12.0 | 否 |
| 2026-04-02 | M4 | USP-S \| Flashback (Factory New) | 33.68 | 14 | 6.9 | 否 |
| 2026-04-03 | M4 | SG 553 \| Dragon Tech (Factory New) | 22.77 | 14 | 96.9 | 是 |
| 2026-04-03 | L3 | G3SG1 \| Hunter (Factory New) | 15.00 | 30 | 39.4 | 否 |
| 2026-04-03 | L1 | MP9 \| Modest Threat (Factory New) | 9.87 | 30 | 38.6 | 否 |
| 2026-04-03 | L1 | XM1014 \| Hieroglyph (Factory New) | 7.10 | 30 | 33.0 | 否 |
| 2026-04-03 | L1 | Dual Berettas \| Polished Malachite (Factory New) | 8.64 | 30 | 15.0 | 否 |
| 2026-04-03 | L1 | SSG 08 \| Dezastre (Factory New) | 8.58 | 30 | 11.6 | 否 |
| 2026-04-03 | L1 | AWP \| Capillary (Factory New) | 127.50 | 30 | 3.0 | 否 |
| 2026-04-04 | L1 | Tec-9 \| Ice Cap (Factory New) | 14.80 | 30 | 10.4 | 否 |
| 2026-04-04 | L1 | Tec-9 \| Re-Entry (Factory New) | 77.00 | 30 | 8.8 | 否 |
| 2026-04-04 | L1 | Five-SeveN \| Silver Quartz (Factory New) | 8.50 | 30 | 5.8 | 否 |
| 2026-04-05 | L1 | G3SG1 \| Desert Storm (Factory New) | 7.88 | 30 | 90.8 | 是 |
| 2026-04-05 | L1 | MAG-7 \| Heat (Factory New) | 180.50 | 30 | 33.1 | 否 |
| 2026-04-05 | L1 | G3SG1 \| Orange Crash (Factory New) | 6.60 | 30 | 10.0 | 否 |
| 2026-04-06 | L3 | SCAR-20 \| Sand Mesh (Factory New) | 9.98 | 30 | 76.2 | 是 |
| 2026-04-06 | L3 | MP5-SD \| Agent (Field-Tested) | 4.13 | 30 | 45.0 | 否 |
| 2026-04-06 | L1 | SG 553 \| Candy Apple (Factory New) | 141.40 | 30 | 35.0 | 否 |
| 2026-04-06 | L1 | P90 \| Sand Spray (Factory New) | 9.00 | 30 | 15.2 | 否 |
| 2026-04-06 | L1 | FAMAS \| Djinn (Factory New) | 985.00 | 30 | 10.2 | 否 |
| 2026-04-07 | L1 | Glock-18 \| Wraiths (Factory New) | 121.00 | 30 | 44.0 | 否 |
| 2026-04-07 | L1 | P250 \| Bengal Tiger (Factory New) | 498.00 | 30 | 38.4 | 否 |
| 2026-04-07 | M4 | Galil AR \| Cold Fusion (Factory New) | 6.80 | 14 | 34.2 | 否 |
| 2026-04-07 | M4 | MAG-7 \| Insomnia (Factory New) | 7.20 | 14 | 7.3 | 否 |
| 2026-04-08 | M4 | SCAR-20 \| Assault (Factory New) | 9.18 | 14 | 43.8 | 否 |
| 2026-04-08 | M4 | FAMAS \| Crypsis (Factory New) | 24.68 | 14 | 30.9 | 否 |
| 2026-04-08 | M4 | SG 553 \| Cyberforce (Factory New) | 7.50 | 14 | 30.7 | 否 |
| 2026-04-08 | M4 | FAMAS \| Colony (Factory New) | 31.60 | 14 | 11.2 | 否 |
| 2026-04-08 | M4 | FAMAS \| Teardown (Factory New) | 16.50 | 14 | 10.0 | 否 |
| 2026-04-09 | M4 | P90 \| Verdant Growth (Factory New) | 58.70 | 14 | 77.7 | 是 |
| 2026-04-09 | M4 | FAMAS \| Halftone Wash (Factory New) | 5.80 | 14 | 7.2 | 否 |
| 2026-04-09 | M4 | P2000 \| Sure Grip (Factory New) | 11.65 | 14 | 3.2 | 否 |
| 2026-04-09 | L1 | MP9 \| Cobalt Paisley (Factory New) | 19.58 | 30 | 3.0 | 否 |
| 2026-04-10 | L1 | SSG 08 \| Hand Brake (Factory New) | 55.88 | 30 | 47.6 | 否 |
| 2026-04-10 | M4 | SCAR-20 \| Grotto (Factory New) | 10.85 | 14 | 30.8 | 否 |
| 2026-04-10 | M4 | MAG-7 \| Popdog (Factory New) | 26.19 | 14 | 17.9 | 否 |
| 2026-04-10 | M4 | P90 \| Module (Factory New) | 19.65 | 14 | 8.2 | 否 |
| 2026-04-10 | M4 | Desert Eagle \| Urban Rubble (Factory New) | 10.60 | 14 | 3.0 | 否 |
| 2026-04-11 | M4 | P90 \| Freight (Factory New) | 8.44 | 14 | 50.5 | 否 |
| 2026-04-11 | M4 | Sawed-Off \| Snake Camo (Factory New) | 21.08 | 14 | 47.9 | 否 |
| 2026-04-11 | L1 | Dual Berettas \| Rose Nacre (Factory New) | 2.98 | 30 | 7.1 | 否 |
| 2026-04-12 | L3 | Tec-9 \| Garter-9 (Factory New) | 2.73 | 30 | 58.4 | 否 |
| 2026-04-12 | M4 | AUG \| Amber Slipstream (Factory New) | 16.99 | 14 | 24.1 | 否 |
| 2026-04-12 | L1 | Desert Eagle \| Mint Fan (Factory New) | 42.65 | 30 | 2.4 | 否 |
| 2026-04-13 | L1 | XM1014 \| Urban Perforated (Factory New) | 224.34 | 30 | 44.9 | 否 |
| 2026-04-14 | M4 | FAMAS \| Meow 36 (Factory New) | 15.69 | 14 | 29.4 | 否 |
| 2026-04-14 | M4 | SCAR-20 \| Trail Blazer (Factory New) | 11.00 | 14 | 15.8 | 否 |
| 2026-04-15 | L1 | ★ Driver Gloves \| Lunar Weave (Field-Tested) | 7487.77 | 30 | 83.1 | 是 |
| 2026-04-15 | M4 | Tec-9 \| Red Quartz (Factory New) | 5.98 | 14 | 33.1 | 否 |
| 2026-04-15 | M3 | Galil AR \| Dusk Ruins (Factory New) | 797.50 | 14 | 24.1 | 否 |
| 2026-04-15 | M3 | MP9 \| Setting Sun (Factory New) | 419.50 | 14 | 13.3 | 否 |
| 2026-04-15 | M4 | SSG 08 \| Fever Dream (Factory New) | 54.70 | 14 | 4.6 | 否 |
| 2026-04-16 | M3 | Chem-Haz Capitaine \| Gendarmerie Nationale | 185.37 | 14 | 100.0 | 否 |
| 2026-04-16 | L3 | XM1014 \| Blue Steel (Factory New) | 11.15 | 30 | 81.6 | 是 |
| 2026-04-16 | M3 | P2000 \| Imperial Dragon (Factory New) | 461.99 | 14 | 14.2 | 否 |
| 2026-04-17 | M4 | P250 \| Red Tide (Factory New) | 22.18 | 14 | 28.7 | 否 |
| 2026-04-18 | L1 | MP7 \| Armor Core (Factory New) | 34.70 | 30 | 46.1 | 否 |
| 2026-04-19 | L1 | P250 \| Contamination (Factory New) | 151.99 | 30 | 60.5 | 否 |
| 2026-04-22 | L3 | SG 553 \| Dragon Tech (Factory New) | 19.48 | 30 | 30.8 | 否 |
| 2026-04-22 | L3 | MP9 \| Sand Dashed (Factory New) | 19.70 | 30 | 8.4 | 否 |
| 2026-04-23 | L3 | Sawed-Off \| Forest DDPAT (Factory New) | 8.20 | 30 | 6.4 | 否 |
| 2026-04-24 | L3 | Sawed-Off \| Black Sand (Factory New) | 14.59 | 30 | 8.0 | 否 |
| 2026-04-25 | L3 | SG 553 \| Ol' Rusty (Factory New) | 4.23 | 30 | 64.5 | 否 |
| 2026-04-25 | M3 | MP9 \| Stained Glass (Factory New) | 1020.00 | 14 | 59.0 | 否 |
| 2026-04-25 | L3 | SG 553 \| Anodized Navy (Factory New) | 5.05 | 30 | 58.7 | 否 |
| 2026-04-26 | L3 | MAG-7 \| Heaven Guard (Factory New) | 9.45 | 30 | 38.5 | 否 |
| 2026-04-27 | L3 | MAG-7 \| Navy Sheen (Factory New) | 14.50 | 30 | 42.7 | 否 |
| 2026-04-27 | L3 | R8 Revolver \| Bone Forged (Factory New) | 13.13 | 30 | 30.0 | 否 |
| 2026-04-27 | L3 | Dual Berettas \| Ventilators (Factory New) | 8.67 | 30 | 13.5 | 否 |
| 2026-04-28 | M4 | UMP-45 \| Mechanism (Factory New) | 61.80 | 14 | 75.3 | 否 |
| 2026-04-28 | L3 | Sawed-Off \| Full Stop (Factory New) | 7.89 | 30 | 34.3 | 否 |
| 2026-04-28 | L3 | SCAR-20 \| Assault (Factory New) | 11.00 | 30 | 19.7 | 否 |
| 2026-04-28 | L3 | AUG \| Storm (Factory New) | 19.28 | 30 | 9.4 | 否 |
| 2026-04-29 | L3 | SG 553 \| Danger Close (Factory New) | 19.18 | 30 | 15.0 | 否 |
| 2026-04-29 | L3 | G3SG1 \| Jungle Dashed (Factory New) | 10.70 | 30 | 7.9 | 否 |
| 2026-04-30 | M4 | P90 \| Verdant Growth (Factory New) | 70.50 | 14 | 60.6 | 否 |
| 2026-04-30 | L3 | SCAR-20 \| Jungle Slipstream (Factory New) | 8.09 | 30 | 48.3 | 否 |
| 2026-04-30 | M4 | Sawed-Off \| Origami (Factory New) | 6.07 | 14 | 34.8 | 否 |
| 2026-04-30 | L3 | SCAR-20 \| Blueprint (Factory New) | 10.60 | 30 | 19.5 | 否 |
| 2026-05-01 | M4 | MP5-SD \| Acid Wash (Factory New) | 40.99 | 14 | 28.5 | 否 |
| 2026-05-01 | M4 | SCAR-20 \| Trail Blazer (Factory New) | 10.50 | 14 | 11.5 | 否 |
| 2026-05-01 | M4 | UMP-45 \| Riot (Factory New) | 22.10 | 14 | 9.8 | 否 |
| 2026-05-03 | L3 | PP-Bizon \| Jungle Slipstream (Factory New) | 13.17 | 30 | 51.8 | 否 |
| 2026-05-03 | M4 | Glock-18 \| Off World (Factory New) | 69.80 | 14 | 44.0 | 否 |
| 2026-05-03 | M4 | MP9 \| Bioleak (Factory New) | 8.20 | 14 | 25.9 | 否 |
| 2026-05-04 | L3 | Dual Berettas \| Shred (Factory New) | 14.50 | 30 | 92.1 | 是 |
| 2026-05-04 | L3 | PP-Bizon \| Night Riot (Factory New) | 9.29 | 30 | 33.0 | 否 |
| 2026-05-04 | L3 | G3SG1 \| Hunter (Factory New) | 14.70 | 30 | 23.5 | 否 |
| 2026-05-04 | M4 | Five-SeveN \| Capillary (Factory New) | 24.49 | 14 | 10.8 | 否 |
| 2026-05-04 | M3 | XM1014 \| Copperflage (Factory New) | 5.50 | 14 | 8.1 | 否 |
| 2026-05-04 | M4 | P90 \| Off World (Factory New) | 19.00 | 14 | 7.3 | 否 |
| 2026-05-05 | L3 | Sawed-Off \| Morris (Factory New) | 16.00 | 30 | 80.5 | 是 |
| 2026-05-05 | L3 | P2000 \| Lifted Spirits (Factory New) | 9.31 | 30 | 56.5 | 否 |
| 2026-05-05 | L3 | SG 553 \| Aerial (Factory New) | 7.30 | 30 | 7.7 | 否 |
| 2026-05-05 | L3 | Dual Berettas \| Stained (Factory New) | 16.90 | 30 | 2.9 | 否 |
| 2026-05-06 | L3 | XM1014 \| Oxide Blaze (Factory New) | 4.83 | 30 | 47.7 | 否 |
| 2026-05-06 | M4 | G3SG1 \| Desert Storm (Factory New) | 6.90 | 14 | 32.1 | 否 |
| 2026-05-07 | M4 | P90 \| Sand Spray (Factory New) | 13.40 | 14 | 10.8 | 否 |
| 2026-05-10 | M3 | ★ Hand Wraps \| Badlands (Minimal Wear) | 4377.27 | 14 | 3.9 | 否 |
| 2026-05-10 | M3 | USP-S \| Purple DDPAT (Factory New) | 588.49 | 14 | 3.1 | 否 |
| 2026-05-11 | M3 | Lt. Commander Ricksaw \| NSWC SEAL | 158.00 | 14 | 100.0 | 否 |
| 2026-05-11 | M3 | Galil AR \| Dusk Ruins (Factory New) | 739.50 | 14 | 64.8 | 否 |
| 2026-05-11 | M3 | AK-47 \| Searing Rage (Factory New) | 212.50 | 14 | 38.2 | 否 |
| 2026-05-11 | M3 | M4A4 \| Hellfire (Factory New) | 2937.50 | 14 | 33.1 | 否 |
| 2026-05-11 | M3 | ★ Hand Wraps \| Spruce DDPAT (Minimal Wear) | 3888.00 | 14 | 21.8 | 否 |
| 2026-05-11 | M3 | AWP \| Crakow! (Factory New) | 982.00 | 14 | 19.5 | 否 |
| 2026-05-11 | M3 | ★ Hand Wraps \| Leather (Minimal Wear) | 5189.00 | 14 | 13.5 | 否 |
| 2026-05-12 | M3 | Zeus x27 \| Dragon Snore (Factory New) | 560.00 | 14 | 84.0 | 否 |
| 2026-05-12 | M3 | XM1014 \| Monster Melt (Factory New) | 81.99 | 14 | 77.8 | 否 |
| 2026-05-12 | M3 | AK-47 \| B the Monster (Factory New) | 4606.00 | 14 | 68.4 | 否 |
| 2026-05-12 | M3 | MAC-10 \| Stalker (Factory New) | 1146.45 | 14 | 55.8 | 否 |
| 2026-05-12 | M3 | P90 \| Reef Grief (Factory New) | 8.40 | 14 | 39.1 | 否 |
| 2026-05-12 | M3 | FAMAS \| Pulse (Factory New) | 293.00 | 14 | 37.3 | 否 |
| 2026-05-12 | M3 | P2000 \| Imperial (Factory New) | 11.73 | 14 | 4.8 | 否 |
| 2026-05-13 | M3 | Cmdr. Mae 'Dead Cold' Jamison \| SWAT | 153.50 | 14 | 100.0 | 否 |
| 2026-05-13 | M3 | AWP \| Green Energy (Factory New) | 459.50 | 14 | 33.8 | 否 |
| 2026-05-14 | M3 | MAC-10 \| Poplar Thicket (Factory New) | 5.79 | 14 | 33.3 | 否 |
| 2026-05-14 | M3 | ★ Sport Gloves \| Arid (Minimal Wear) | 10489.00 | 14 | 18.3 | 否 |
| 2026-05-14 | M3 | ★ Specialist Gloves \| Emerald Web (Field-Tested) | 8888.00 | 14 | 16.5 | 否 |
| 2026-05-16 | M3 | MP9 \| Shredded (Factory New) | 7.49 | 14 | 69.6 | 否 |
| 2026-05-16 | M3 | AUG \| Eye of Zapems (Factory New) | 105.00 | 14 | 66.4 | 否 |
| 2026-05-16 | M3 | M4A1-S \| Stratosphere (Factory New) | 509.00 | 14 | 39.0 | 否 |
| 2026-05-16 | M3 | ★ Hand Wraps \| Slaughter (Field-Tested) | 3780.00 | 14 | 21.7 | 否 |
| 2026-05-17 | M3 | Glock-18 \| Glockingbird (Factory New) | 47.40 | 14 | 28.5 | 否 |
| 2026-05-18 | M4 | Glock-18 \| Sacrifice (Factory New) | 91.00 | 14 | 35.3 | 否 |
| 2026-05-18 | M3 | XM1014 \| Gum Wall Camo (Factory New) | 1.17 | 14 | 14.7 | 否 |
| 2026-05-18 | M3 | ★ Specialist Gloves \| Emerald Web (Minimal Wear) | 12000.00 | 14 | 5.4 | 否 |
| 2026-05-19 | M3 | MP5-SD \| Gold Leaf (Factory New) | 4.77 | 14 | 62.3 | 否 |
| 2026-05-19 | M3 | ★ Hand Wraps \| Slaughter (Minimal Wear) | 5128.00 | 14 | 21.6 | 否 |
| 2026-05-19 | M3 | ★ Specialist Gloves \| Foundation (Minimal Wear) | 7310.00 | 14 | 10.1 | 否 |
| 2026-05-20 | M3 | Tec-9 \| Citric Acid (Factory New) | 1.04 | 14 | 54.6 | 否 |
| 2026-05-21 | M3 | AUG \| Creep (Factory New) | 9.99 | 14 | 84.9 | 是 |
| 2026-05-21 | M3 | USP-S \| Royal Guard (Factory New) | 56.30 | 14 | 57.8 | 否 |
| 2026-05-21 | M3 | UMP-45 \| Warm Blooded (Factory New) | 10.25 | 14 | 54.7 | 否 |
| 2026-05-21 | M3 | AWP \| Exothermic (Factory New) | 114.00 | 14 | 49.3 | 否 |
| 2026-05-21 | M3 | AWP \| The End (Factory New) | 630.00 | 14 | 44.5 | 否 |
| 2026-05-21 | M3 | ★ Moto Gloves \| Eclipse (Minimal Wear) | 3450.00 | 14 | 18.1 | 否 |
| 2026-05-21 | M3 | ★ Hand Wraps \| Badlands (Field-Tested) | 2499.99 | 14 | 17.4 | 否 |
| 2026-05-21 | M3 | ★ Hand Wraps \| Spruce DDPAT (Field-Tested) | 2299.50 | 14 | 10.5 | 否 |
| 2026-05-21 | M3 | ★ Driver Gloves \| Crimson Weave (Minimal Wear) | 9999.00 | 14 | 7.9 | 否 |
| 2026-05-21 | M3 | ★ Driver Gloves \| Diamondback (Minimal Wear) | 4149.49 | 14 | 7.2 | 否 |
| 2026-05-21 | M3 | CZ75-Auto \| Distressed (Factory New) | 13.90 | 14 | 7.1 | 否 |
| 2026-05-22 | M3 | Galil AR \| Sky Mandala (Factory New) | 14.90 | 14 | 90.6 | 否 |
| 2026-05-22 | M3 | P2000 \| Royal Baroque (Factory New) | 9.74 | 14 | 86.9 | 否 |
| 2026-05-22 | M3 | USP-S \| Bleeding Edge (Factory New) | 62.37 | 14 | 85.6 | 否 |
| 2026-05-22 | M3 | AK-47 \| Breakthrough (Factory New) | 105.49 | 14 | 83.3 | 否 |
| 2026-05-22 | M3 | SSG 08 \| Calligrafaux (Factory New) | 10.49 | 14 | 83.2 | 否 |
| 2026-05-22 | M3 | Zeus x27 \| Earth Mandala (Factory New) | 9.78 | 14 | 80.0 | 否 |
| 2026-05-22 | M3 | Five-SeveN \| Fraise Crane (Factory New) | 27.99 | 14 | 68.1 | 否 |
| 2026-05-22 | M3 | M4A1-S \| Glitched Paint (Factory New) | 68.00 | 14 | 65.7 | 否 |
| 2026-05-22 | M3 | M4A4 \| In Living Color (Factory New) | 688.50 | 14 | 55.0 | 否 |
| 2026-05-22 | M3 | Glock-18 \| Gamma Doppler (Factory New) | 930.00 | 14 | 49.9 | 否 |
| 2026-05-22 | M3 | M4A4 \| Royal Paladin (Factory New) | 1559.50 | 14 | 49.1 | 否 |
| 2026-05-22 | M3 | USP-S \| Tropical Breeze (Factory New) | 12.59 | 14 | 47.0 | 否 |
| 2026-05-22 | M3 | FAMAS \| Commemoration (Factory New) | 326.99 | 14 | 45.2 | 否 |
| 2026-05-22 | M3 | USP-S \| Orion (Factory New) | 945.61 | 14 | 42.3 | 否 |
| 2026-05-22 | M3 | M4A4 \| The Emperor (Factory New) | 1415.50 | 14 | 40.2 | 否 |
| 2026-05-22 | M3 | AK-47 \| Cartel (Factory New) | 418.86 | 14 | 38.0 | 否 |
| 2026-05-22 | M3 | ★ Specialist Gloves \| Foundation (Field-Tested) | 4998.50 | 14 | 36.8 | 否 |
| 2026-05-22 | M3 | Dual Berettas \| Sweet Little Angels (Factory New) | 76.50 | 14 | 36.6 | 否 |
| 2026-05-22 | M3 | P250 \| Muertos (Factory New) | 158.00 | 14 | 35.5 | 否 |
| 2026-05-22 | M3 | M4A1-S \| Golden Coil (Factory New) | 1560.00 | 14 | 35.0 | 否 |
| 2026-05-22 | M3 | ★ Sport Gloves \| Arid (Field-Tested) | 6868.00 | 14 | 31.7 | 否 |
| 2026-05-22 | M3 | MP9 \| Rose Iron (Factory New) | 91.70 | 14 | 31.3 | 否 |
| 2026-05-22 | M3 | Glock-18 \| Bullet Queen (Factory New) | 815.00 | 14 | 25.4 | 否 |
| 2026-05-22 | M3 | Desert Eagle \| Kumicho Dragon (Factory New) | 494.00 | 14 | 25.1 | 否 |
| 2026-05-22 | M3 | ★ Moto Gloves \| Boom! (Minimal Wear) | 4119.50 | 14 | 24.5 | 否 |
| 2026-05-22 | M3 | ★ Driver Gloves \| Crimson Weave (Field-Tested) | 8299.00 | 14 | 22.2 | 否 |
| 2026-05-22 | M3 | MP9 \| Deadly Poison (Factory New) | 46.00 | 14 | 21.2 | 否 |
| 2026-05-22 | M3 | M4A4 \| The Battlestar (Factory New) | 763.50 | 14 | 20.9 | 否 |
| 2026-05-22 | M3 | Glock-18 \| Winterized (Factory New) | 12.89 | 14 | 20.2 | 否 |
| 2026-05-22 | M3 | ★ Driver Gloves \| Lunar Weave (Field-Tested) | 4824.50 | 14 | 19.9 | 否 |
| 2026-05-22 | M3 | MAC-10 \| Pipsqueak (Factory New) | 23.90 | 14 | 19.8 | 否 |
| 2026-05-22 | M3 | M4A1-S \| Decimator (Factory New) | 318.00 | 14 | 18.5 | 否 |
| 2026-05-22 | M3 | Dual Berettas \| Hemoglobin (Factory New) | 111.00 | 14 | 17.4 | 否 |
| 2026-05-22 | M3 | CZ75-Auto \| Imprint (Factory New) | 20.00 | 14 | 17.3 | 否 |
| 2026-05-22 | M3 | P2000 \| Fire Elemental (Factory New) | 699.00 | 14 | 17.1 | 否 |
| 2026-05-22 | M3 | M4A4 \| Desert-Strike (Factory New) | 648.00 | 14 | 15.5 | 否 |
| 2026-05-22 | M3 | Galil AR \| Cerberus (Factory New) | 1730.00 | 14 | 14.4 | 否 |
| 2026-05-22 | M3 | ★ Hand Wraps \| Leather (Field-Tested) | 3138.00 | 14 | 14.2 | 否 |
| 2026-05-22 | M3 | M4A4 \| Cyber Security (Factory New) | 1096.50 | 14 | 9.9 | 否 |
| 2026-05-22 | M3 | ★ Driver Gloves \| Diamondback (Field-Tested) | 3180.00 | 14 | 7.8 | 否 |
| 2026-05-22 | M3 | AUG \| Carved Jade (Factory New) | 420.00 | 14 | 2.8 | 否 |
| 2026-05-22 | M3 | USP-S \| Orange Anolis (Factory New) | 890.00 | 14 | 2.4 | 否 |
| 2026-05-22 | M3 | AK-47 \| Panthera onca (Factory New) | 3298.00 | 14 | 2.0 | 否 |
| 2026-05-23 | M3 | Rezan The Ready \| Sabre | 55.90 | 14 | 100.0 | 否 |
| 2026-05-23 | M3 | SSG 08 \| Blush Pour (Factory New) | 7.88 | 14 | 84.1 | 否 |
| 2026-05-23 | M3 | Zeus x27 \| Tosai (Factory New) | 12.53 | 14 | 61.7 | 否 |
| 2026-05-23 | M3 | Five-SeveN \| Angry Mob (Factory New) | 584.50 | 14 | 52.5 | 否 |
| 2026-05-23 | M3 | Desert Eagle \| Tilted (Factory New) | 9.28 | 14 | 52.2 | 否 |
| 2026-05-23 | M3 | Desert Eagle \| The Daily Deagle (Factory New) | 8.59 | 14 | 46.9 | 否 |
| 2026-05-23 | M3 | ★ Driver Gloves \| Lunar Weave (Minimal Wear) | 6298.50 | 14 | 42.2 | 否 |
| 2026-05-23 | M3 | CZ75-Auto \| Tacticat (Factory New) | 32.29 | 14 | 41.8 | 否 |
| 2026-05-23 | M3 | Galil AR \| Sugar Rush (Factory New) | 1319.50 | 14 | 41.5 | 否 |
| 2026-05-23 | M3 | P2000 \| Handgun (Factory New) | 128.50 | 14 | 40.3 | 否 |
| 2026-05-23 | M3 | AUG \| Death by Puppy (Factory New) | 108.00 | 14 | 40.1 | 否 |
| 2026-05-23 | M3 | AK-47 \| Frontside Misty (Factory New) | 870.00 | 14 | 39.9 | 否 |
| 2026-05-23 | M3 | FAMAS \| Valence (Factory New) | 176.89 | 14 | 38.5 | 否 |
| 2026-05-23 | M3 | UMP-45 \| Plastique (Factory New) | 33.00 | 14 | 37.8 | 否 |
| 2026-05-23 | M3 | M4A4 \| Desolate Space (Factory New) | 549.50 | 14 | 36.9 | 否 |
| 2026-05-23 | M3 | AK-47 \| The Outsiders (Factory New) | 437.87 | 14 | 36.2 | 否 |
| 2026-05-23 | M3 | Sawed-Off \| Serenity (Factory New) | 36.79 | 14 | 31.8 | 否 |
| 2026-05-23 | M3 | PP-Bizon \| Brass (Factory New) | 27.60 | 14 | 28.0 | 否 |
| 2026-05-23 | M3 | ★ Moto Gloves \| Finish Line (Minimal Wear) | 1157.50 | 14 | 27.4 | 否 |
| 2026-05-23 | M3 | MP7 \| Impire (Factory New) | 119.50 | 14 | 27.3 | 否 |
| 2026-05-23 | M3 | Desert Eagle \| Starcade (Factory New) | 1490.00 | 14 | 20.2 | 否 |
| 2026-05-23 | M3 | Dual Berettas \| Anodized Navy (Factory New) | 94.90 | 14 | 16.1 | 否 |
| 2026-05-23 | M3 | M4A1-S \| Hyper Beast (Factory New) | 1800.00 | 14 | 12.9 | 否 |
| 2026-05-23 | M3 | Glock-18 \| Weasel (Factory New) | 159.50 | 14 | 8.7 | 否 |
| 2026-05-24 | M3 | Charm \| Lil' SAS | 1.27 | 14 | 100.0 | 否 |
| 2026-05-24 | M3 | Galil AR \| Stone Cold (Factory New) | 180.00 | 14 | 63.7 | 否 |
| 2026-05-24 | M3 | Glock-18 \| Coral Bloom (Factory New) | 17.15 | 14 | 62.3 | 否 |
| 2026-05-24 | M3 | MP9 \| Food Chain (Factory New) | 142.50 | 14 | 51.2 | 否 |
| 2026-05-24 | M3 | PP-Bizon \| Photic Zone (Factory New) | 28.00 | 14 | 50.8 | 否 |
| 2026-05-24 | M3 | Galil AR \| Rocket Pop (Factory New) | 74.00 | 14 | 45.6 | 否 |
| 2026-05-24 | M3 | Desert Eagle \| Serpent Strike (Factory New) | 13.55 | 14 | 43.0 | 否 |
| 2026-05-24 | M3 | Glock-18 \| Neo-Noir (Factory New) | 1260.00 | 14 | 39.8 | 否 |
| 2026-05-24 | M3 | Desert Eagle \| Golden Koi (Factory New) | 1789.00 | 14 | 38.8 | 否 |
| 2026-05-24 | M3 | Desert Eagle \| Calligraffiti (Factory New) | 66.90 | 14 | 35.5 | 否 |
| 2026-05-24 | M3 | P2000 \| Imperial Dragon (Factory New) | 356.00 | 14 | 34.7 | 否 |
| 2026-05-24 | M3 | USP-S \| Monster Mashup (Factory New) | 588.00 | 14 | 33.9 | 否 |
| 2026-05-24 | M3 | ★ Bloodhound Gloves \| Bronzed (Field-Tested) | 1049.50 | 14 | 31.6 | 否 |
| 2026-05-24 | M3 | PP-Bizon \| Carbon Fiber (Factory New) | 59.00 | 14 | 29.6 | 否 |
| 2026-05-24 | M3 | Five-SeveN \| Copper Galaxy (Factory New) | 180.40 | 14 | 26.8 | 否 |
| 2026-05-24 | M3 | Galil AR \| Black Sand (Factory New) | 77.83 | 14 | 19.9 | 否 |
| 2026-05-24 | M3 | M4A1-S \| Master Piece (Factory New) | 3499.50 | 14 | 19.6 | 否 |
| 2026-05-24 | M3 | AK-47 \| Asiimov (Factory New) | 2248.00 | 14 | 18.9 | 否 |
| 2026-05-24 | M3 | Glock-18 \| Franklin (Factory New) | 1019.00 | 14 | 18.1 | 否 |
| 2026-05-24 | M3 | Tec-9 \| Bamboozle (Factory New) | 62.00 | 14 | 16.7 | 否 |
| 2026-05-24 | M3 | Five-SeveN \| Forest Night (Factory New) | 21.00 | 14 | 15.0 | 否 |
| 2026-05-24 | M3 | Tec-9 \| Remote Control (Factory New) | 278.00 | 14 | 14.9 | 否 |
| 2026-05-24 | M3 | M4A1-S \| Control Panel (Factory New) | 978.49 | 14 | 12.2 | 否 |
| 2026-05-24 | M3 | Desert Eagle \| Naga (Factory New) | 218.48 | 14 | 9.0 | 否 |
| 2026-05-24 | M3 | SSG 08 \| Azure Glyph (Factory New) | 25.00 | 14 | 8.9 | 否 |
| 2026-05-24 | M3 | Sawed-Off \| Parched (Factory New) | 5.95 | 14 | 8.0 | 否 |
| 2026-05-24 | M3 | ★ Hand Wraps \| CAUTION! (Minimal Wear) | 1299.50 | 14 | 6.1 | 否 |
| 2026-05-25 | M3 | Col. Mangos Dabisi \| Guerrilla Warfare | 168.50 | 14 | 100.0 | 否 |
| 2026-05-25 | M3 | Lieutenant 'Tree Hugger' Farlow \| SWAT | 108.00 | 14 | 100.0 | 否 |
| 2026-05-25 | M3 | M4A4 \| Bullet Rain (Factory New) | 1734.44 | 14 | 75.6 | 否 |
| 2026-05-25 | M3 | FAMAS \| Meow 36 (Factory New) | 9.46 | 14 | 74.3 | 否 |
| 2026-05-25 | M3 | XM1014 \| Copperflage (Factory New) | 4.27 | 14 | 73.4 | 否 |
| 2026-05-25 | M3 | M4A1-S \| Player Two (Factory New) | 923.00 | 14 | 70.7 | 否 |
| 2026-05-25 | M3 | Desert Eagle \| Ocean Drive (Factory New) | 1555.00 | 14 | 69.8 | 否 |
| 2026-05-25 | M3 | Desert Eagle \| Heat Treated (Factory New) | 315.99 | 14 | 69.5 | 否 |
| 2026-05-25 | M3 | AWP \| Printstream (Factory New) | 1444.25 | 14 | 67.7 | 否 |
| 2026-05-25 | M3 | Dual Berettas \| Flora Carnivora (Factory New) | 31.90 | 14 | 63.8 | 否 |
| 2026-05-25 | M3 | P250 \| Epicenter (Factory New) | 167.50 | 14 | 60.6 | 否 |
| 2026-05-25 | M3 | SG 553 \| Darkwing (Factory New) | 29.90 | 14 | 59.8 | 否 |
| 2026-05-25 | M3 | MP9 \| Hypnotic (Factory New) | 120.80 | 14 | 58.3 | 否 |
| 2026-05-25 | M3 | M4A1-S \| Chantico's Fire (Factory New) | 1646.64 | 14 | 57.9 | 否 |
| 2026-05-25 | M3 | FAMAS \| Decommissioned (Factory New) | 57.50 | 14 | 54.8 | 否 |
| 2026-05-25 | M3 | Tec-9 \| Decimator (Factory New) | 759.00 | 14 | 54.1 | 否 |
| 2026-05-25 | M3 | Five-SeveN \| Fairy Tale (Factory New) | 2266.00 | 14 | 53.6 | 否 |
| 2026-05-25 | M3 | M4A1-S \| Moss Quartz (Factory New) | 774.50 | 14 | 51.8 | 否 |
| 2026-05-25 | M3 | ★ Moto Gloves \| Boom! (Field-Tested) | 2986.94 | 14 | 48.5 | 否 |
| 2026-05-25 | M3 | Tec-9 \| Avalanche (Factory New) | 98.90 | 14 | 46.7 | 否 |
| 2026-05-25 | M3 | M4A4 \| Tooth Fairy (Factory New) | 92.80 | 14 | 46.0 | 否 |
| 2026-05-25 | M3 | P250 \| Black & Tan (Factory New) | 98.80 | 14 | 43.6 | 否 |
| 2026-05-25 | M3 | P250 \| Valence (Factory New) | 12.00 | 14 | 42.0 | 否 |
| 2026-05-25 | M3 | MP9 \| Arctic Tri-Tone (Factory New) | 58.00 | 14 | 41.7 | 否 |
| 2026-05-25 | M3 | P90 \| Blind Spot (Factory New) | 100.00 | 14 | 40.2 | 否 |
| 2026-05-25 | M3 | MP7 \| Cirrus (Factory New) | 56.80 | 14 | 37.5 | 否 |
| 2026-05-25 | M3 | AK-47 \| Phantom Disruptor (Factory New) | 145.00 | 14 | 37.4 | 否 |
| 2026-05-25 | M3 | AUG \| Tom Cat (Factory New) | 7.69 | 14 | 36.6 | 否 |
| 2026-05-25 | M3 | M4A1-S \| VariCamo (Factory New) | 9.28 | 14 | 35.1 | 否 |
| 2026-05-25 | M3 | SSG 08 \| Rapid Transit (Factory New) | 47.00 | 14 | 33.8 | 否 |
| 2026-05-25 | M3 | M4A1-S \| Leaded Glass (Factory New) | 189.50 | 14 | 32.1 | 否 |
| 2026-05-25 | M3 | SSG 08 \| Ghost Crusader (Factory New) | 114.00 | 14 | 32.1 | 否 |
| 2026-05-25 | M3 | P2000 \| Urban Hazard (Factory New) | 16.40 | 14 | 31.2 | 否 |
| 2026-05-25 | M3 | MAC-10 \| Fade (Factory New) | 329.99 | 14 | 30.3 | 否 |
| 2026-05-25 | M3 | P2000 \| Pulse (Factory New) | 43.10 | 14 | 30.2 | 否 |
| 2026-05-25 | M3 | AK-47 \| X-Ray (Factory New) | 14350.00 | 14 | 28.9 | 否 |
| 2026-05-25 | M3 | MAG-7 \| Copper Coated (Factory New) | 56.00 | 14 | 28.7 | 否 |
| 2026-05-25 | M3 | MP9 \| Black Sand (Factory New) | 11.80 | 14 | 28.3 | 否 |
| 2026-05-25 | M3 | ★ Moto Gloves \| Spearmint (Minimal Wear) | 17000.00 | 14 | 27.4 | 否 |
| 2026-05-25 | M3 | AK-47 \| Elite Build (Factory New) | 53.60 | 14 | 26.2 | 否 |
| 2026-05-25 | M3 | USP-S \| Road Rash (Factory New) | 1000.00 | 14 | 26.0 | 否 |
| 2026-05-25 | M3 | MAC-10 \| Malachite (Factory New) | 54.49 | 14 | 25.8 | 否 |
| 2026-05-25 | M3 | Desert Eagle \| Fennec Fox (Factory New) | 3079.50 | 14 | 25.6 | 否 |
| 2026-05-25 | M3 | Tec-9 \| Mummy's Rot (Factory New) | 113.50 | 14 | 25.6 | 否 |
| 2026-05-25 | M3 | M4A4 \| Polysoup (Factory New) | 176.50 | 14 | 24.5 | 否 |
| 2026-05-25 | M3 | AWP \| Desert Hydra (Factory New) | 10698.50 | 14 | 23.1 | 否 |
| 2026-05-25 | M3 | AWP \| Hyper Beast (Factory New) | 1000.49 | 14 | 21.7 | 否 |
| 2026-05-25 | M3 | Dual Berettas \| Twin Turbo (Factory New) | 158.38 | 14 | 18.6 | 否 |
| 2026-05-25 | M3 | ★ Bloodhound Gloves \| Snakebite (Field-Tested) | 945.00 | 14 | 17.2 | 否 |
| 2026-05-25 | M3 | M4A4 \| Global Offensive (Factory New) | 415.00 | 14 | 15.5 | 否 |
| 2026-05-25 | M3 | ★ Broken Fang Gloves \| Needle Point (Minimal Wear) | 419.50 | 14 | 11.6 | 否 |
| 2026-05-25 | M3 | MAG-7 \| Sonar (Factory New) | 16.80 | 14 | 5.8 | 否 |
| 2026-05-25 | M3 | AK-47 \| Baroque Purple (Factory New) | 435.00 | 14 | 2.8 | 否 |
| 2026-05-25 | M3 | M4A1-S \| Boreal Forest (Factory New) | 116.50 | 14 | 2.4 | 否 |
| 2026-05-26 | M3 | 'Two Times' McCoy \| USAF TACP | 41.20 | 14 | 100.0 | 否 |
| 2026-05-26 | M3 | Arno The Overgrown \| Guerrilla Warfare | 104.50 | 14 | 100.0 | 否 |
| 2026-05-26 | M3 | Dragomir \| Sabre | 36.89 | 14 | 100.0 | 否 |
| 2026-05-26 | M3 | Rezan the Redshirt \| Sabre | 42.70 | 14 | 100.0 | 否 |
| 2026-05-26 | M3 | MAC-10 \| Snow Splash (Factory New) | 1.35 | 14 | 90.5 | 否 |
| 2026-05-26 | M3 | Glock-18 \| Trace Lock (Factory New) | 52.69 | 14 | 87.4 | 否 |
| 2026-05-26 | M3 | Tec-9 \| Brother (Factory New) | 36.02 | 14 | 77.6 | 否 |
| 2026-05-26 | M3 | R8 Revolver \| Banana Cannon (Factory New) | 27.58 | 14 | 75.5 | 否 |
| 2026-05-26 | M3 | AUG \| Syd Mead (Factory New) | 147.11 | 14 | 73.6 | 否 |
| 2026-05-26 | M3 | USP-S \| Kill Confirmed (Factory New) | 1535.00 | 14 | 69.3 | 否 |
| 2026-05-26 | M3 | MAC-10 \| Disco Tech (Factory New) | 176.00 | 14 | 67.6 | 否 |
| 2026-05-26 | M3 | M4A1-S \| Vaporwave (Factory New) | 1102.00 | 14 | 57.9 | 否 |
| 2026-05-26 | M3 | ★ Moto Gloves \| Cool Mint (Minimal Wear) | 9222.00 | 14 | 55.1 | 否 |
| 2026-05-26 | M3 | MP9 \| Hot Rod (Factory New) | 1017.99 | 14 | 53.2 | 否 |
| 2026-05-26 | M3 | Galil AR \| Urban Rubble (Factory New) | 174.00 | 14 | 52.9 | 否 |
| 2026-05-26 | M3 | USP-S \| The Traitor (Factory New) | 696.50 | 14 | 51.1 | 否 |
| 2026-05-26 | M3 | FAMAS \| Meltdown (Factory New) | 919.50 | 14 | 48.5 | 否 |
| 2026-05-26 | M3 | M4A1-S \| Atomic Alloy (Factory New) | 835.00 | 14 | 48.2 | 否 |
| 2026-05-26 | M3 | M4A4 \| Hellish (Factory New) | 1272.00 | 14 | 47.8 | 否 |
| 2026-05-26 | M3 | MAG-7 \| Praetorian (Factory New) | 39.49 | 14 | 47.1 | 否 |
| 2026-05-26 | M3 | MAG-7 \| Hard Water (Factory New) | 48.90 | 14 | 44.8 | 否 |
| 2026-05-26 | M3 | USP-S \| Guardian (Factory New) | 40.60 | 14 | 44.4 | 否 |
| 2026-05-26 | M3 | UMP-45 \| Blaze (Factory New) | 150.25 | 14 | 43.5 | 否 |
| 2026-05-26 | M3 | AK-47 \| Rat Rod (Factory New) | 399.98 | 14 | 43.1 | 否 |
| 2026-05-26 | M3 | Desert Eagle \| Corinthian (Factory New) | 6.40 | 14 | 42.7 | 否 |
| 2026-05-26 | M3 | MAC-10 \| Propaganda (Factory New) | 895.90 | 14 | 42.2 | 否 |
| 2026-05-26 | M3 | AK-47 \| Orbit Mk01 (Factory New) | 545.00 | 14 | 41.0 | 否 |
| 2026-05-26 | M3 | ★ Moto Gloves \| Spearmint (Field-Tested) | 11368.49 | 14 | 40.8 | 否 |
| 2026-05-26 | M3 | Zeus x27 \| Charged Up (Factory New) | 165.00 | 14 | 40.0 | 否 |
| 2026-05-26 | M3 | P90 \| Attack Vector (Factory New) | 114.00 | 14 | 39.5 | 否 |
| 2026-05-26 | M3 | AWP \| Capillary (Factory New) | 60.99 | 14 | 38.6 | 否 |
| 2026-05-26 | M3 | Five-SeveN \| Kami (Factory New) | 34.10 | 14 | 35.0 | 否 |
| 2026-05-26 | M3 | AUG \| Contractor (Factory New) | 11.67 | 14 | 32.1 | 否 |
| 2026-05-26 | M3 | SSG 08 \| Blood in the Water (Factory New) | 1019.50 | 14 | 32.1 | 否 |
| 2026-05-26 | M3 | CZ75-Auto \| Red Astor (Factory New) | 52.90 | 14 | 24.5 | 否 |
| 2026-05-26 | M3 | M4A4 \| Evil Daimyo (Factory New) | 47.60 | 14 | 24.5 | 否 |
| 2026-05-26 | M3 | SG 553 \| Heavy Metal (Factory New) | 9.80 | 14 | 24.2 | 否 |
| 2026-05-26 | M3 | XM1014 \| Black Tie (Factory New) | 35.00 | 14 | 22.4 | 否 |
| 2026-05-26 | M3 | Tec-9 \| Cracked Opal (Factory New) | 30.00 | 14 | 22.1 | 否 |
| 2026-05-26 | M3 | P250 \| Visions (Factory New) | 64.00 | 14 | 21.0 | 否 |
| 2026-05-26 | M3 | Tec-9 \| Flash Out (Factory New) | 22.46 | 14 | 19.0 | 否 |
| 2026-05-26 | M3 | AUG \| Amber Fade (Factory New) | 35.68 | 14 | 17.3 | 否 |
| 2026-05-26 | M3 | M4A1-S \| Party Animal (Factory New) | 455.00 | 14 | 12.3 | 否 |
| 2026-05-26 | M3 | ★ Bloodhound Gloves \| Charred (Field-Tested) | 1287.25 | 14 | 7.4 | 否 |
| 2026-05-26 | M3 | CZ75-Auto \| Polymer (Factory New) | 20.00 | 14 | 4.5 | 否 |
| 2026-05-27 | M3 | P2000 \| Sure Grip (Factory New) | 7.00 | 14 | 75.3 | 否 |
| 2026-05-27 | M3 | MP5-SD \| Phosphor (Factory New) | 87.50 | 14 | 64.0 | 否 |
| 2026-05-27 | M3 | PP-Bizon \| High Roller (Factory New) | 208.90 | 14 | 59.0 | 否 |
| 2026-05-27 | M3 | FAMAS \| Bad Trip (Factory New) | 427.00 | 14 | 54.8 | 否 |
| 2026-05-27 | M3 | Dual Berettas \| Hydro Strike (Factory New) | 37.46 | 14 | 52.3 | 否 |
| 2026-05-27 | M3 | MP7 \| Coral Paisley (Factory New) | 2.65 | 14 | 51.8 | 否 |
| 2026-05-27 | M3 | Sawed-Off \| Kiss♥Love (Factory New) | 108.70 | 14 | 48.2 | 否 |
| 2026-05-27 | M3 | XM1014 \| XOXO (Factory New) | 114.50 | 14 | 41.9 | 否 |
| 2026-05-27 | M3 | SSG 08 \| Mainframe 001 (Factory New) | 5.26 | 14 | 40.7 | 否 |
| 2026-05-27 | M3 | MP7 \| Abyssal Apparition (Factory New) | 109.50 | 14 | 36.8 | 否 |
| 2026-05-27 | M3 | MAC-10 \| Pipe Down (Factory New) | 52.00 | 14 | 35.3 | 否 |
| 2026-05-27 | M3 | SG 553 \| Dragon Tech (Factory New) | 10.57 | 14 | 32.3 | 否 |
| 2026-05-27 | M3 | USP-S \| Torque (Factory New) | 10.50 | 14 | 30.0 | 否 |
| 2026-05-27 | M3 | MP7 \| Special Delivery (Factory New) | 64.45 | 14 | 29.5 | 否 |
| 2026-05-27 | M3 | Five-SeveN \| Violent Daimyo (Factory New) | 11.50 | 14 | 27.7 | 否 |
| 2026-05-27 | M3 | P90 \| Neoqueen (Factory New) | 8.70 | 14 | 26.9 | 否 |
| 2026-05-27 | M3 | P250 \| Dark Filigree (Factory New) | 98.00 | 14 | 23.4 | 否 |
| 2026-05-27 | M3 | ★ Driver Gloves \| Racing Green (Minimal Wear) | 367.00 | 14 | 22.9 | 否 |
| 2026-05-27 | M3 | Tec-9 \| Urban DDPAT (Factory New) | 14.90 | 14 | 21.3 | 否 |
| 2026-05-27 | M3 | AWP \| Arsenic Spill (Factory New) | 7.40 | 14 | 20.0 | 否 |
| 2026-05-27 | M3 | MAC-10 \| Whitefish (Factory New) | 19.03 | 14 | 19.4 | 否 |
| 2026-05-27 | M3 | M4A1-S \| Rose Hex (Factory New) | 6.15 | 14 | 12.4 | 否 |
| 2026-05-27 | M3 | M4A4 \| Poly Mag (Factory New) | 11.49 | 14 | 9.2 | 否 |

## 连续状态变化

| 日期 | 规则 | 原状态 | 新状态 |
|---|---|---|---|
| 2026-02-01 | RB1 | active | watch |
| 2026-02-01 | RB2 | active | watch |
| 2026-02-01 | RB3 | active | watch |
| 2026-02-01 | RB4 | active | watch |
| 2026-02-01 | RB5 | active | watch |
| 2026-02-05 | S1 | active | probation |
| 2026-02-15 | RB1 | watch | active |
| 2026-02-26 | RB1 | active | probation |
| 2026-02-27 | RB2 | watch | probation |
| 2026-03-03 | RB3 | watch | probation |
| 2026-04-24 | RB4 | watch | probation |
| 2026-04-25 | RB5 | watch | probation |
| 2026-05-14 | L1 | active | probation |
| 2026-05-16 | L3 | active | probation |
| 2026-05-21 | M4 | active | probation |
| 2026-05-28 | M3 | active | probation |
