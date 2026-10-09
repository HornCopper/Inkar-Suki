<div align="center">

<img width="256" src="https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/Logo.jpg" alt="Inkar Suki Logo">

# [Inkar Suki](https://inkar-suki.codethink.cn)

_基于 Nonebot 2 的多功能群聊机器人_

![Nonebot2](https://img.shields.io/badge/Nonebot2-Release_v2.2.1-brightgreen)
![GitHub](https://img.shields.io/github/license/HornCopper/Inkar-Suki)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/HornCopper/Inkar-Suki?include_prereleases)
![GitHub (Pre-)Release Date](https://img.shields.io/github/release-date-pre/HornCopper/Inkar-Suki)

_名字来源：Inkar-usi@DIA_

**万水千山总是情，点个 star 行不行？**

</div>

---

## 简介

Inkar Suki 是一个集成多种功能的群聊机器人，基于 [Nonebot 2](https://v2.nonebot.dev) 构建，旨在提供更加便捷的聊天和管理功能。

**不欢迎某个15元解锁特殊功能的机器人借鉴本项目的代码。**

## 文档

查看完整文档，请点击[这里](https://inkar-suki.codethink.cn/Inkar-Suki-Docs/)或访问[GitHub 文档仓库](https://github.com/HornCopper/Inkar-Suki-Docs)。

欢迎在参考文档后对我们的项目进行`Pull Request`！

**如果搭建过程中遇到问题，欢迎来提问或发起`Issue`，而不是使用本仓库的代码去纠缠数据源的人员！**

## 功能

### 机器人管理

- [x] 账号封禁系统；
- [x] 账号权限系统；
- [x] 账号货币系统；
- [x] 机器人多账号管理（含禁言等处理）；

Bot 主人可发送 `权限反查 用户 <权限节点> [页码]` 或 `权限反查 群 <权限节点> [页码]`（英文命令 `permissionholders`），按指定节点列出有权限的用户或群，每页 20 个。例如 `权限反查 群 group.application.chat_records`。查询具体节点，无需节点预先定义，因此也可查找旧节点或自定义节点；按实际生效权限匹配父节点、通配符授权和显式拒绝。用户列表包含 Bot 主人，群列表以已保存的群配置为范围。

### 个性化界面

- [x] 发送 `偏好 UI颜色 #7B61B5` 设置个人统一报告的主色；`偏好 UI颜色` 查询，`偏好 UI颜色 默认` 恢复默认。支持六位十六进制颜色；特色界面及有业务含义的颜色不受此偏好影响。

### 娱乐

- [x] 对诗；
- [x] 24点；
- [x] 今天吃什么/喝什么；
- [x] 随机狗图/龙图；
- [x] 签到（含独立奖池与个人背包）；
- [x] 入群欢迎；
- [x] 戳一戳回复；

#### 签到奖池与背包

奖池全局共享，在原有签到金币及幸运奖励之外，每次成功签到最多额外抽中一件奖品。每件奖品设置绝对中奖概率（百分数，最多四位小数）；上架总概率不超过 100%，剩余概率为未中奖。支持不限量和限量投放，限量奖品耗尽后停止抽取，其他奖品的概率不变。重复签到不会再次抽奖。

Bot 主人可使用 `setop u<QQ号> economy.checkin.pool.manage` 授予奖池管理权限。查看奖池和自己的背包无需该权限，修改奖池、查看其他用户的中奖记录和标记兑付均需要该权限。

| 命令 | 用途 |
| --- | --- |
| `签到奖池 [页码]` / `签到奖池 帮助` | 查看奖品或完整规则 |
| `签到奖池 投放 "纪念徽章" 5% 10` | 投放 10 件，中奖概率 5% |
| `签到奖池 投放 "纪念卡片" 1% 不限量` | 投放不限量奖品 |
| `签到奖池 概率 <奖品编号> <概率%>` | 调整中奖概率 |
| `签到奖池 补货 <奖品编号> <数量>` | 给限量奖品增加库存 |
| `签到奖池 <上架\|下架\|删除> <奖品编号>` | 控制奖品投放 |
| `背包 [页码]` / `我的背包 [页码]` | 以图片 UI 查看自己的奖品、投放人、获得时间及兑付状态 |
| `签到奖池 记录 <QQ号> [页码]` | 管理员以图片 UI 查看指定用户的背包 |
| `签到奖池 未兑奖 <奖品编号> [页码]` | 管理员以图片 UI 查看该奖品所有未兑奖记录，含获奖用户及记录编号 |
| `签到奖池 兑付 <背包记录编号>` | 管理员在实际发放后标记已兑付 |

中奖奖品自动存入背包，保留名称、投放人和获得时间；删除奖池奖品不会删除已有背包记录，也仍可使用原奖品编号查询未兑奖记录。`未兑奖` 支持别名 `未兑付`、`待兑付`，每页 10 条，按获奖记录编号从早到晚排列，已兑付记录不显示；同名但不同编号的投放分别统计。奖品由投放人安排发放，兑付命令仅记录发放状态，不会自动增加金币或调用外部服务，且不能重复兑付。首次启动自动创建奖池和背包数据表。

### 百科

- [x] MediaWiki 搜索；

### 雀魂

- [x] PT 查询；
- [x] 最近对局查询；
- [x] 玩家搜索；

### Minecraft

- [x] 服务器检索；
- [x] 版本获取；

### 剑网3

- [x] 成就百科
- [x] 官方公告；
- [x] 装备查询；
- [x] 加速阈值查询（`加速`／`急速 [基础帧数] [附加加速]`；如 `加速`、`加速 48`、`加速 24 50`、`加速 24 50U`。普通附加加速与装备合计受 256/1024 上限约束，`U` 表示附加加速不受限、仅装备部分受限；逐帧列出上限内可达到的最低加速等级，多个 0 面板加速档仅显示最快一档）；
- [x] 开团辅助；
- [x] 开服查询；
- [x] 情缘系统；
- [x] 日常查询；
- [x] 副本查询；
- [x] 随机表情；
- [x] 事件查询；
- [x] 科举查询；
- [x] 金价查询；
- [x] 马场查询；
- [x] 撩人骚话；
- [x] 贴吧查询；
- [x] 外观价格；
- [x] 沙盘、招募、挂件（需启用`JX3API`）；
- [x] 奇遇查询（含自助补全）；
- [x] 奇遇名片：`奇遇名片 服务器 ID 奇遇 [特大/大/中/小]`（ID 为游戏角色名，尺寸默认中，按名片尺寸计算）。复用名片查询，用纯图像算法自动选择水墨圈位置；后台线程计算，多个请求按收到顺序排队，生成后自动发送。例：`奇遇名片 梦江南 取净湖 三山四海 大`；
- [x] 事件推送（仅支持非挂机客户端类，需启用`JX3API WS`）；
- [x] 交易行价格（含试炼之地）；
- [x] 咸鱼微博推送（需在配置文件中启用）。

## 赞助支持

如果你喜欢这个项目并希望支持它的发展，欢迎通过以下方式赞助：

<details>
<summary>点击展开赞助二维码</summary>

<img src="https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/wechat_donate.jpg" height="300" alt="微信收款码">
<img src="https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/alipay_donate.png" height="300" alt="支付宝收款码">

</details>

---

## 友情链接

- [小可·Akaribot](https://github.com/Teahouse-Studios/akari-bot) - 茶馆群内 QQ 机器人（小可）by @OasisAkari；
- [轻雪机器人](https://bot.liteyuki.icu) - 神羽女生自用轻雪机器人 @Snowykami。

---

## 贡献者

**请忽略 `Serfend`，此人已被除名。**

### Inkar-Suki 项目贡献者

[![][contrib-image_iks]][contrib-link_iks]

### Inkar-Suki-Docs 项目贡献者

[![][contrib-image_iksdocs]][contrib-link_iksdocs]

[contrib-image_iks]: https://contrib.rocks/image?repo=HornCopper/Inkar-Suki

[contrib-link_iks]: https://github.com/HornCopper/Inkar-Suki/graphs/contributors

[contrib-image_iksdocs]: https://contrib.rocks/image?repo=codethink-cn/Inkar-Suki-Docs

[contrib-link_iksdocs]: https://github.com/codethink-cn/Inkar-Suki-Docs/graphs/contributors
