import sys
import nonebot
import json
# sys用于添加新的path，方便导入src/tools下的工具包
from nonebot import on_command # on_command响应器
from nonebot.adapters import Message 
from nonebot.adapters.onebot.v11 import GroupMessageEvent # 只处理群消息事件，因为数据要从群内的数据中获取，所以不处理私聊。
from nonebot.params import CommandArg
TOOLS = nonebot.get_driver().config.tools_path # 获取工具包路径
sys.path.append(TOOLS) # 导入工具包路径
DATA = TOOLS[:-5] + "data" # 拼接数据路径
from .arcaea import getUserBestBySongName, getUserInfo, judgeWhetherPlayer, getUserCode
from utils import checknumber # 导入检测是否为数字的函数，来自src/tools/utils.py
from file import read, write # 导入文件操作函数，来自src/tools/file.py

arcaea_userinfo = on_command("arcuser",priority=5)
@arcaea_userinfo.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    `arcaea_userinfo`，用于获取`Arcaea`用户信息。
    示例：
    ```
    User: 
        +arcuser HornCopper
    Bot: 
        查询到玩家HornCopper（791691022）：
        注册时间：2022年02月04日 21:54:16
        PTT：535
        [歌曲图片]
        上次游玩：inkar-usi（Future）
        Easy Complete 95%
        分数：9287603 A
        PURE 414 FAR 32 LOST 17
        游玩时间：2022年08月04日 00:09:03
        单曲PTT：6.792009999999999
        搭档：
        [搭档图片]
    '''
    arg = args.extract_plain_text()
    info = ""
    if arg == "":
        info = getUserCode(event.group_id, event.user_id) # 通过群聊获取用户绑定的UserCode
        if info == False:
            await arcaea_userinfo.finish("未绑定Arcaea账号且未给出任何信息，没办法找啦！") # 若没绑定则告知
        msg = await getUserInfo(usercode=info)
        await arcaea_userinfo.finish(msg)
    else:
        if checknumber(arg):
            msg = await getUserInfo(usercode=int(arg))
        else:
            msg = await getUserInfo(nickname=arg)
        await arcaea_userinfo.finish(msg)

arcaea_binduser = on_command("arcbind",priority=5)
@arcaea_binduser.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    在用户所在群聊绑定群聊用户和`Arcaea`用户。
    '''
    arg = args.extract_plain_text()
    if arg == False:
        await arcaea_binduser.finish("未给出任何信息，没办法绑定哦~")
    present_data = json.loads(read(DATA + "/" + str(event.group_id) + "/arcaea.json"))
    if checknumber(arg):
        resp = await judgeWhetherPlayer(usercode=int(arg))
    else:
        resp = await judgeWhetherPlayer(nickname=arg)
    if resp:
        present_data[str(event.user_id)] = resp[1]
        write(DATA + "/" + str(event.group_id) + "/arcaea.json", json.dumps(present_data))
        await arcaea_binduser.finish("绑定成功：" +  resp[0] + "（" + str(resp[1]) + "）") 
    else:
        await arcaea_binduser.finish("您输入的好友码/用户名查不到哦，请检查后重试~")
        
arcaea_unbind = on_command("arcunbind",priority=5)
@arcaea_unbind.handle()
async def _(event: GroupMessageEvent):
    '''
    相反操作，解绑。
    '''
    present_data = json.loads(read(DATA + "/" + str(event.group_id) + "/arcaea.json"))
    if present_data[str(event.user_id)]:
        present_data.pop(str(event.user_id)) # 删除用户键值
        write(DATA + "/" + str(event.group_id) + "/arcaea.json", json.dumps(present_data))
        await arcaea_unbind.finish("已解绑Arcaea账号~以后使用相关命令均需重新绑定哦~") 
    else:
        await arcaea_unbind.finish("唔……尚未绑定过Arcaea，无法解绑啦！")

arcaea_best = on_command("arcbest", priority=5)
@arcaea_best.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取用户单曲最佳成绩，需要指定歌曲以及难度。
    '''
    arg = args.extract_plain_text()
    arg = arg.split(" ")
    if len(arg) < 2:
        await arcaea_best.finish("缺少必要信息，没办法搜索，请查看帮助文件。")
    if len(arg) == 2:
        final = arg[0]
        difficulty = arg[1]
    elif len(arg) >= 3:
        difficulty = arg[-1] # 适配了例如`+arcbest Infinity Heaven ftr`的情况，最后一个空格被作为歌曲名和难度的区分线，`split`函数分割的最后一部分为难度，前面均为歌曲名。
        arg.remove(arg[-1])
        final = " ".join(arg)
    user_code = getUserCode(event.group_id, event.user_id)
    msg = await getUserBestBySongName(user_code, final, difficulty)
    await arcaea_best.finish(msg)