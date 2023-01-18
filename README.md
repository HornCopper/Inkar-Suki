<div align="center">

# [Inkar Suki](https://www.inkar-suki.xyz)

_基于Nonebot 2的多功能的 QQ 群聊机器人_

![Nonebot2](https://img.shields.io/badge/Nonebot2-Release_v2.0.0_beta.5-brightgreen)
![go-cqhttp](https://img.shields.io/badge/go--cqhttp-v1.0.0_rc3-brightgreen)
<br>
![GitHub](https://img.shields.io/github/license/codethink-cn/Inkar-Suki)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/codethink-cn/Inkar-Suki?include_prereleases)
![GitHub (Pre-)Release Date](https://img.shields.io/github/release-date-pre/codethink-cn/Inkar-Suki)

名字不完整来源：Inkar-usi@DIA

**万水千山总是情，点个star行不行？**

</div>
    
# 简介
各种功能于一体的[QQ](https://im.qq.com)群聊机器人，基于[Nonebot 2](https://v2.nonebot.dev)。

# 功能
**由于功能设计初衷是为群聊服务，以下大部分功能将在私聊不可用，食用方法请移步[文档](https://inkar-suki.codethink.cn)。**

**2022年11月27日更新文档：已同步最新版本，迁移至[此](https://inkar-suki.codethink.cn)，原域名将在2023年4月-7月失效，不再跳转至现有域名。**

- [剑网3](https://jx3.xoyo.com)相关功能。
    - 以下功能数据来源为[JX3BOX](https://www.jx3box.com)。
        - [x] 查看心法下所有技能（由于某公司对聊天记录把控比较严格，此功能比较看脸，~~但不知道为什么莫问心法一般都不会吃风控~~）；
        - [x] 获取技能系数；
        - [x] 获取奇穴数据；
        - [x] 获取宠物数据；
        - [x] 获取成就信息；
        - [x] 获取任务信息；
        - [x] 获取buff信息。
    - 以下功能数据来源于[JX3API](https://www.jx3api.com)，*斜体为付费功能，即您需要向JX3API购买Token方可使用的功能*。
        - [x] 获取马匹刷新地点；
        - [x] 获取服务器状态；
        - [x] 获取心法对应宏命令以及推荐奇穴搭配；
        - [x] 获取日常和周常；
        - [x] 获取科举答案；
        - [x] 获取阵眼效果；
        - [x] 获取推荐装备（PVP/PVE各一套）；
        - [x] 获取奇遇条件（不支持宠物奇遇）；
        - [x] 获取剑网3新闻；
        - [x] 获取一条剑网3推栏“万花谷”频道的骚话；
        - [x] 获取当前赛季推荐的小药；
        - [x] 获取服务器外观的物价；
        - [x] 获取服务器的金价；
        - [x] 订阅新闻、开服与维护、*玄晶、马匹、奇遇、扶摇*；
        - [x] *获取奇遇/烟花记录*；
        - [x] *获取服务器的团队招募*；
        - [x] 获取一条舔狗日志；
        - [x] *获取服务器花价*；
        - [x] *获取角色装备属性*；
        - [x] *获取未来日常*。
    - 以下为辅助性功能。
        - [x] 团长群内开团（不同步至游戏）；
        - [x] 团内预定坑位；
        - [x] 查看预定列表；
        - [x] 提交金团记录；
        - [x] 提交特殊掉落；
        - [x] 结算以上数据，归档保存；
        - [x] 获取团长开团信息；
        - [x] 修改开团信息；
        - [x] 设置团主要服务器；
        - [x] 设置团牌；
        - [x] 团队认证
- [Arcaea（韵律源点）](https://arcaea.lowiro.com/zh)相关功能。
    - 以下数据来源为[Arcaea Unlimited API]。
        - [x] 获取用户信息以及最近游玩记录；
        - [x] 获取用户单曲最佳成绩；
        - [x] 绑定Arcaea用户。
- [Minecraft（我的世界）](https://www.minecraft.net/zh-hans)相关功能。
    - [x] 获取Minecraft服务器信息；
    - [x] 获取Minecraft最新版本号。
- 娱乐功能。
    - [x] 结婚（包含求婚、接受/拒绝、离婚）；
    - 以下数据来源于[QQ音乐](https://y.qq.com)和[网易云音乐](https://music.163.com)。
        - [x] 点歌（支持QQ、网易云音乐）；
    - 以下数据来源于[墨迹天气](http://m.moji.com/)。
        - [x] 查询天气。
- 机器人使用帮助类。
    - 以下功能仅供机器人主人进行调试/维护。
        - [x] 查看/修改帮助图片的尺寸（请根据实际情况修改）；
        - [x] 关闭/重启机器人；
        - [x] 清除图片缓存；
        - [x] 让机器人发送消息；
        - [x] 测试机器人是否在线；
        - [x] 前/后台执行命令；
        - [x] 发送全域公告（所有机器人加入的群聊都会收到）；
        - [x] 调用CQHTTP API，具体请参考[go-cqhttp文档](https://docs.go-cqhttp.org)；
        - [x] 截图网页（需网络支持）；
        - [x] 设置**机器人**管理员；
        - [x] 封禁/解封某人；
        - [x] **数据注册，清除或创建群聊数据，请注意，机器人新加入的群聊无法直接使用机器人，需要`8`级以上机器人管理员发送`+register`方可使用（快捷方式：`+reg`），此功能所有命令都需要在对应的群聊内方可执行，部分全域命令除外。**
    - 以下功能任何人均可使用（除少部分需要**群**权限）。
        - [x] 修改新人欢迎语；
        - [x] 获取帮助文件；
    - 以下功能供群管理/机器人管理者使用。
        - [x] 违禁词设置（若机器人拥有群内管理权限，触发则禁言1分钟）。
- [Wiki](https://www.mediawiki.org)相关功能。
    - [x] 设置群内Interwiki；
    - [x] Interwiki搜索；
    - [x] 设置初始Wiki；
    - [x] 初始Wiki搜索；
    - [x] 跨Wiki搜索。
- [GitHub](https://github.com)相关功能。
    - [x] 获取仓库信息；
    - [x] Webhook推送；
    - [x] 推送机器人代码至GitHub，或拉取GitHub代码至本地（非常推荐您fork主仓库并克隆自己的仓库，这样可以让此功能**正常工作**，直接克隆主仓库**仅可使用拉取**，若直接下载，则此功能**均不可使用**）。

# 公共实例
- 目前作者的公共实例位于香港，QQ号为`3438531564`，想要使用请发起[issue](https://github.com/codethink-cn/Inkar-Suki/issues)或联系作者QQ（`3349104868`）。

# 机器人交流群
- 欢迎加入`Inkar-Suki用户群`，群号为[650495414](https://jq.qq.com/?_wv=1027&k=JazIPJxf)，您可以在这里与其他使用机器人的用户交流。

感谢您使用`Inkar Suki`，幸甚有您！

# 赞助
欢迎[投喂](https://afdian.net/a/Inkar-Suki)。

# 友情链接
- [Nonebot 2](https://v2.nonebot.dev/) - 跨平台 Python 异步机器人框架；
- [go-cqhttp](https://docs.go-cqhttp.org/) - 基于 Mirai 以及 MiraiGo 的 OneBot Golang 原生实现；
- [小可·Akaribot](https://github.com/Teahouse-Studios/akari-bot) - 茶馆群内QQ机器人（小可）by @OasisAkari；
- [团子机器人](https://github.com/JustUndertaker/mini_jx3_bot) - 基于nonebot2的剑网三群聊机器人，采用jx3api作为数据源 by @JustUndertaker；
- [资源酒肆](https://jq.qq.com/?_wv=1027&k=urh2dqal) - 欢迎来这里畅聊`Minecraft`相关内容；
