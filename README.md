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

### QQ 官方机器人接入

支持原有 OneBot v11 与 QQ 官方协议同时运行。官方接入优先复用文字、图片查询功能，支持 QQ 群聊与 C2C 单聊，其他未适配的接口和消息类型会跳过。在 `src/config/config.yml` 的 `qq_official` 中填写 `enabled`、`app_id`、`app_secret` 和 `use_websocket`；凭证保存在本地配置，不提交到仓库。发送 `官号信息` 可查看官方身份内部 ID 及匹配后的业务 ID。

同机多工作进程部署时，官方 WebSocket 使用进程锁保持每个分片只有一个连接；连接进程退出后，其他工作进程自动接管。现有 OneBot 服务可继续使用多进程。

**如果搭建过程中遇到问题，欢迎来提问或发起`Issue`，而不是使用本仓库的代码去纠缠数据源的人员！**

## 功能

### 机器人管理

- [x] 账号封禁系统；
- [x] 账号权限系统；
- [x] 账号货币系统；
- [x] 机器人多账号管理（含禁言等处理）；

Bot 主人可发送 `权限反查 用户 <权限节点> [页码]` 或 `权限反查 群 <权限节点> [页码]`（英文命令 `permissionholders`），按指定节点列出有权限的用户或群，每页 20 个。例如 `权限反查 群 group.application.chat_records`。查询具体节点，无需节点预先定义，因此也可查找旧节点或自定义节点；按实际生效权限匹配父节点、通配符授权和显式拒绝。用户列表包含 Bot 主人，群列表以已保存的群配置为范围。

拥有 `manage.identity.bind` 权限的管理员可关联官方 OpenID 身份与 OneBot 号码，并归并本地数据。Bot 主人默认具有该权限，也可给负责核对身份的管理员授权（以下数字均为示例，需替换）：

```text
setop u1234567 manage.identity.bind
匹配个人 -123456789 1234567
匹配群 -987654321 7654321
```

两个匹配命令的参数都不需要 `u`、`g` 前缀，由命令区分类型。左侧必须是 `官号信息` 中本项目已记录的负数用户或群 ID，右侧为管理员确认的正数号码。用户只能匹配用户，群只能匹配群；重复匹配相同目标不会重复合并，已匹配的身份不能直接改绑。不同群或单聊中的个人身份可分别关联到同一个 QQ 号。

群匹配后，后续官方消息进入插件前会将 `event.group_id` 替换成对应群号；个人匹配后，`event.user_id` 使用对应 QQ 号，与 OneBot 共用业务数据。协议层保留原 OpenID 用于回复。`官号信息` 同时显示内部 ID 和业务 ID；映射在重启后继续生效，管理命令及共用账号、群设置入口也会解析旧负数 ID。

负数身份可先独立保存签到、背包、权限、个人偏好、角色与群配置。匹配时列表去重合并；冲突配置按非默认字段和列表有效数据量比较，数据较多的一侧优先，同分保留号码侧，另一侧补全默认或缺失项。金币、签到次数、最后签到时间分别取较大值，不相加；权限显式拒绝继续优先；群授权期限取永久或较晚值。相关团队和历史记录一并迁移，完全相同的历史去重，独立奖品保留原记录编号和兑付状态。

映射、数据库迁移及原始记录快照在同一个 SQLite 事务中提交，操作失败时回滚。合并快照和操作者保存在 `src/data/qq_official.sqlite3` 的 `identity_merge_history`，供排查恢复；备份时请同时保存 OpenID、账号、缓存和日志数据库。归并范围为本项目管理的本地数据，外部服务保存的数据不自动迁移；后续请求会使用匹配后的业务 ID。

### 个性化界面

- [x] 发送 `偏好 UI颜色 #7B61B5` 设置个人统一报告的主色；`偏好 UI颜色` 查询，`偏好 UI颜色 默认` 恢复默认。支持六位十六进制颜色；特色界面及有业务含义的颜色不受此偏好影响。

### 娱乐

- [x] 对诗；
- [x] 24点；
- [x] 今天吃什么/喝什么；
- [x] 随机狗图/龙图；
- [x] 随机数：`随机数 x y`，返回闭区间 `[x, y]` 内的随机整数，支持负数；
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
- [x] 自定义成就提示条。
- [x] 官方公告；
- [x] 装备查询；
- [x] 加速阈值查询；
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
- [x] 奇遇名片；
- [x] 社交名片；
- [x] 事件推送（仅支持非挂机客户端类，需启用`JX3API WS`）；
- [x] 体服公告差异推送；
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
