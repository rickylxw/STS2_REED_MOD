# 变更说明 (Changelog)

---

## v1.1.2

### 修复

- **修复 Reed.json 合并冲突标记导致模组无法加载的问题**
- **修复角色缩小效果立刻消失的问题**：`reed_chibi_sprite.gd` 不再每帧覆盖父节点 scale，让游戏的缩放效果系统（SetScaleAndHue / DoScaleTween）正常生效

### 变更

- 角色缩放从 0.4 调至 1.0
- 卡面图片从 .png 重命名为 .jpg（实际为 JPEG 格式），重建所有 .import 文件
- 初始遗物改用 RegisterCharacterStarterRelic 特性注册，移除废弃的 StartingRelicTypes 重写

### 新增

- 先古对话本地化：添加全部 9 位先古（THE_ARCHITECT、NEOW、PAEL、TANX、VAKUU、DARV、OROBAS、TEZCATARA、NONUPEIPE）的中英文对话文件
- 先古卡：永燃余烬（EternalEmber）— 先古专属卡牌及能力

### 卡牌调整

- 先古卡永燃余烬不再出现在抽卡池中：移除 RegisterCard，仅保留 DustyTomeCard 注册
- 先古卡升级改为减一费（3费→2费）

---

## v1.1.3

### 卡牌精简

删除 7 张机制重复的卡牌，保留各组性价比最优的一张：

| 删除卡牌 | 机制 | 保留替代 | 原因 |
|----------|------|----------|------|
| 暗焰潜行 (ShadowflameProwl) | 1费消耗纯格挡 | 烬盾 (CinderShield) | Common 更易获取，仅少1点格挡 |
| 烬火突刺 (CinderSpear) | 多段+灼燃 2次 | 烬枪连刺 (CinderSpearCombo) 3次 | 同费同稀有度，严格更优 |
| 炎鳞 (FlameScale) | 灼燃换格挡×1有上限 | 灼燃壁垒 (ScorchBastion) ×2无上限 | 同费同稀有度，严格更优 |
| 灼燃觉醒 (ScorchAwakening) | 灼燃换力量+消耗 | 焚身 (BurnAway) 回血+不消耗 | BurnAway 不消耗自身且可重复使用 |
| 传炬 (PassingTheTorch) | 消耗灼燃换伤害无基础 | 焚化 (Cremation) 有基础伤害 | Cremation 有可靠基础伤害 |
| 余烬 (Embers) | 0费抽2消耗自身 | 燃烬之眼 (EmberEye) 不消耗 | EmberEye Common更易获取，代价极小 |
| 余烬刃 (EmberBlade) | 1费伤+灼燃消耗 | 矛焰 (SpearFlame) 不消耗 | SpearFlame Common不消耗，仅少1伤 |

### 变更

- 修复角色缩小效果（reed_chibi_sprite.gd 不再每帧覆盖父节点 scale）

### 修复

- **修复消耗牌卡面重复显示"消耗"字样**：13 张消耗牌在代码中设置了 `CardKeyword.Exhaust`，游戏自动在卡面显示"消耗"关键字，描述文本中的 `[gold]消耗[/gold]` / `[gold]Exhaust[/gold]` 导致重复显示，已从中文和英文描述中全部移除

---

## 模板（用于后续版本）

### 新增

-

### 修复

-

### 变更

-

### 卡牌调整

-

### 删除

-
