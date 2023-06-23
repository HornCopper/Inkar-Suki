from .api import *

jx3_cmd_pet = on_command("jx3_pet", aliases={"宠物"}, priority=5)


@jx3_cmd_pet.handle()
async def jx3_pet(state: T_State, args: Message = CommandArg()):
    '''
    查询宠物信息：

    Example：-宠物 静静
    '''
    data = args.extract_plain_text()
    pets = await get_pet(data)
    state['pets'] = pets
    if not len(pets):
        return await jx3_cmd_pet.finish("唔……没有找到你要的宠物，请检查后重试~")
    if len(pets) == 1:
        state["num"] = 0
        return await __handle_number(state, 0)
    msg = str.join(
        "\n", [f'{index}.{x.name}' for index, x in enumerate(pets)])
    return await jx3_cmd_pet.send(msg)


@jx3_cmd_pet.got("num", prompt="发送序号以搜索，发送其他内容则取消搜索。")
async def num(state: T_State, num: Message = Arg()):
    num = num.extract_plain_text()
    return await __handle_number(state, num)


async def __handle_number(state: T_State, num: int):
    if not checknumber(num):
        return await jx3_cmd_pet.finish(PROMPT_NumberInvalid)
    pets = state['pets']
    if len(state['pets']) <= num:
        return await jx3_cmd_pet.finish(PROMPT_NumberNotExist)
    pet:PetInfo = pets[num]
    msg = f"查询到「{pet.name}」：\n参考:{pet.url}\n线索:{pet.clue}\n描述:{pet.desc}"
    return await jx3_cmd_pet.finish(msg)
