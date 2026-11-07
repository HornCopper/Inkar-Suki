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

官方群在未匹配真实群号时默认停用业务功能，包括已经加入但尚未匹配的群；仅保留 `官号信息`（`qq身份`）、`匹配群`、`匹配个人` 作为配置入口，匹配操作仍需要 `manage.identity.bind` 权限。匹配群号后，下一条消息自动按对应群号正常处理，无需重启。此限制不影响 OneBot 群聊和官方单聊。

开团辅助无需逐个匹配个人。团表显示用户头像和职业角标；QQ 号码直接获取头像，官方负数身份使用本地保存的原始 OpenID，兼容已有报名，获取失败时使用职业图标。头像缓存一小时，失败缓存五分钟。团表和团队列表中，未匹配个人的官方身份显示创建或报名时记录的昵称；没有昵称的历史记录显示“群友”。OneBot 用户和已匹配的官方用户仍显示 QQ 号，报名归属和团长权限继续按原有身份判断。

业务命令继续使用 OneBot 接口，协议差异由 `src/adapters/qq_official` 处理。兼容 Bot 对插件暴露 OneBot 协议，与转换后的消息段保持一致，Alconna/UniSeg 也按 OneBot 解析图片，实际连接和发送仍使用 QQ 官方协议。官方接口兼容范围如下：

| OneBot 接口 | 官方接入的处理方式 |
| --- | --- |
| `get_group_list`、`get_friend_list` | 统计当前应用在本地已识别的群聊、单聊会话，合并已匹配号码、去除重复身份，不代表官方完整名单。管理员 `ping` 无需改动业务代码也能回复。 |
| `get_group_info` | 调用官方群资料接口；未获授权时显示群号，省略未知人数。官方单聊返回单聊上下文名称。 |
| `get_group_member_info` | 当前发送者使用消息事件中的身份；机器人自身及其他已知成员使用官方查询接口，OpenID 限定在当前应用和当前群。 |
| `get_group_member_list` | 调用官方接口并遍历分页，按匹配后的身份去重；未获白名单权限时跳过，不伪造完整名单。 |
| `get_stranger_info`、`get_image` | 昵称使用当前事件或本次查询已确认的成员资料，未知昵称以 ID 显示；图片解析只使用当前消息的真实附件地址。 |
| `upload_group_file`、`upload_private_file` | 转为当前会话的官方文件消息，支持生成的 APNG 文件；保留文件名，上传时关闭自动发送，再按原消息被动回复。超过 5MB 的二进制使用分片上传，上传上限为 200MB。 |
| `set_group_ban` | 将匹配前后用户 ID 转回当前群成员 OpenID；支持禁言和解除禁言，最长 30 天，仍需官方授予相应权限及机器人群管理员身份。 |
| `get_cookies`、`get_group_file_url`、`set_group_leave`、`set_group_add_request` | 没有可直接复用的官方对应能力或 OneBot 事件参数；含这些直接调用的业务响应器会提前跳过，避免发送无法完成的确认提示。 |

完整成员查询等能力受官方白名单限制，配置 OpenID 匹配不会自动获得接口权限。任意业务跨群发送和其他 OneBot 专属事件仍不在此接入范围内。接口依据见 [官方群资料接口](https://bot.q.qq.com/wiki/develop/api-v2/autogen/api/v2_groups_group_openid_info.get.html)、[群成员接口](https://bot.q.qq.com/wiki/develop/api-v2/autogen/api/v2_groups_group_openid_members.get.html)、[富媒体上传](https://bot.q.qq.com/wiki/develop/api-v2/autogen/api/v2_groups_group_openid_files.post.html)。

公告、微博卡片、日常和活动提醒等经共用 `send_subscribe` 发送的群订阅已接入官方主动推送，支持文字和图片，沿用原订阅项目及区服筛选。官方群必须先匹配真实群号、在对应群开启订阅，并在 QQ 客户端允许机器人主动发送消息；不需要先发消息来维持五分钟回复窗口。当前工作进程中的 OneBot 已向同群成功投递时不再重复发送官 Bot；OneBot 发送失败或不在群内时，尝试已知的官方群 OpenID。两种协议分别连接在不同工作进程时，仍可能各推送一次；同群避免同时使用两个推送账号。

官方推送记录进群、退群和主动消息开关事件，退群或关闭主动消息后暂停投递；不依赖需白名单的群状态查询接口，遗漏事件时以官方发送结果为准。兼容层按未认证应用的保守额度排队等待（每应用 30 条/分钟、每群 20 条/分钟），每群每天最多尝试 1000 条，日界线为北京时间零点。十分钟内同一应用、群、订阅项目、区服和相同内容的同一消息分段只尝试一次，以避免多进程重复发送；失败不自动重试，避免超时后重复触达。状态、限额和去重摘要保存在本地 `qq_official.sqlite3`，权限、配额及媒体失败会写入 `WARNING` 日志，不影响其他群继续推送。平台实际权限与额度仍以 [官方主动消息规则](https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/overview.html) 及 [群消息接口](https://bot.q.qq.com/wiki/develop/api-v2/autogen/api/v2_groups_group_openid_messages.post.html) 为准。

新成员欢迎语支持将官方 `GROUP_MEMBER_ADD` 转成 OneBot 入群通知，复用现有欢迎语响应器、`修改欢迎语` 命令和群配置。WebSocket 需要先获平台授权，再在本地 YAML 的 `qq_official` 中设置 `group_member_events: true` 并重启；该选项默认关闭，对应 `GROUP_MEMBER_EVENT (1<<24)`，未授权订阅可能导致平台关闭连接，未订阅时上线日志会提示。Webhook 则需在官方后台订阅成员加入事件。官方群须已匹配群号并允许主动消息；`禁用欢迎语` 设置会生效，重复通知只处理一次，不同成员及同一成员的再次入群按不同事件处理。现有欢迎语命令继续使用纯文字配置，通知回复兼容文字和图片；装饰性的 @ 和引用段会省略。发送使用主动消息额度，不把成员事件 ID 冒充用户消息 ID。机器人自己加入未匹配群时仍不会发送业务欢迎信息。事件字段和权限要求见 [官方成员加入事件](https://bot.q.qq.com/wiki/develop/api-v2/autogen/event/group_member_add.html) 及 [事件订阅说明](https://bot.q.qq.com/wiki/develop/api-v2/dev-prepare/interface-framework/event-emit.html)。

兼容层会将未适配接口、功能提前跳过、权限不足、查询降级、无法转换的消息段及未接入事件写入 `WARNING` 日志，默认 `LOG_LEVEL=SUCCESS` 即可看到。日志包含应用、群、用户和消息 ID，以及可取得的接口名、命令、响应器和官方错误码，不输出正文、API 参数、附件地址或服务端响应体。同一条消息的相同原因只记录一次；随正文省略的装饰性 @、引用段使用 `DEBUG`，避免普通回复刷屏。

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

个人负数身份仍可独立保存签到、背包、权限、个人偏好和角色；未匹配群号的官方群暂停业务处理，历史数据保留。匹配时列表去重合并；冲突配置按非默认字段和列表有效数据量比较，数据较多的一侧优先，同分保留号码侧，另一侧补全默认或缺失项。金币、签到次数、最后签到时间分别取较大值，不相加；权限显式拒绝继续优先；群授权期限取永久或较晚值。相关团队和历史记录一并迁移，完全相同的历史去重，独立奖品保留原记录编号和兑付状态。

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

`签到` 支持别名 `打卡`、`祈祷`。奖池全局共享，在原有签到金币及幸运奖励之外，每次成功签到最多额外抽中一件奖品。每件奖品设置绝对中奖概率（百分数，最多四位小数）；上架总概率不超过 100%，剩余概率为未中奖。支持不限量和限量投放，限量奖品耗尽后停止抽取，其他奖品的概率不变。重复签到不会再次抽奖。

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
| `兑奖 <背包记录编号> [群号]` / `签到奖池 兑奖 <背包记录编号> [群号]` | 中奖者自助领取权限奖品；群权限可指定群号，省略时使用当前群；个人权限授予本人 |

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
