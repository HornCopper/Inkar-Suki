from src.tools.dep import *

jx3_cmd_attribute3 = on_command(
    "jx3_attribute3",
    name="属性v3",
    aliases={'属性v3', '装备v3', '面板v3', '查装v3'},
    priority=5,
    catalog=permission.jx3.pvp.user.attribute,
    description="获取角色的属性",
    example=[
        Jx3Arg(Jx3ArgsType.server, is_optional=True),
        Jx3Arg(Jx3ArgsType.user, alias='id或uid'),
        Jx3Arg(Jx3ArgsType.pageIndex, default=0, alias='装备页面')
    ],
    document='''
    默认缓存1天内的角色信息
    保存30天内的装备变动信息
    根据角色装备属性分类：
    1.PVP-DPS  3.PVP-HPS  5.PVP-TANK
    2.PVE-DPS  4.PVE-HPS  6.PVE-TANK
    7.PVX      8.寻宝
    
    dps默认展示PVE-DPS，
    hps默认展示PVE-HPS，
    t默认展示PVE-TANK，
    ''',
)


@jx3_cmd_attribute3.handle()
async def jx3_attribute3(template: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_server, arg_user, arg_page = template
    if arg_page < 0 or arg_page >= len(BaseJx3UserAttributePage.types):
        arg_page = 0

    # 仅在30秒内缓存
    data = await Jx3PlayerDetailInfo.from_auto(arg_server, arg_user, cache_length=30)
    if data is None:
        return await jx3_cmd_attribute3.finish(f'未能找到来自[{arg_server}]的用户[{arg_user}]')

    user = data.user.to_dict()
    current = data.attributes[data.current_score]
    if arg_page == 0:
        current_kunfu = current.kungfu.type
        arg_page = BaseJx3UserAttributePage.types_mapper.get(current_kunfu)

    arg_page = BaseJx3UserAttributePage.types[arg_page]
    attributes = data.get_attributes(page=arg_page)

    if not attributes:
        attributes = {f'{data.current_score}': current}
    attributes = [data.attributes[x].to_dict() for x in attributes]

    result = {
        'user': user,
        'attributes': attributes,
    }
    return await jx3_cmd_attribute3.send(f'[测试]获取成功:data-length:{len(json.dumps(result))}')
