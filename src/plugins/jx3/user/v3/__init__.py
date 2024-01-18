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
        Jx3Arg(Jx3ArgsType.string, default='0', alias='装备页面')
    ],
    document='''
    默认缓存1天内的角色信息
    保存30天内的装备变动信息
    根据角色装备属性分类：
    1.PVP-DPS  3.PVP-HPS  5.PVP-TANK
    2.PVE-DPS  4.PVE-HPS  6.PVE-TANK
    7.PVX      8.寻宝
    
    当输入-1时
    dps默认展示PVE-DPS，
    hps默认展示PVE-HPS，
    t默认展示PVE-TANK，
    ''',
)


def get_attributes_from_data(data: Jx3PlayerDetailInfo, arg_page: int | str) -> tuple[list[Jx3UserAttributeInfo], AttributeType]:
    '''根据筛选类型返回属性列表'''
    def from_filter_type(filter_type: AttributeType):
        if filter_type == AttributeType.Unknown:
            return data.attributes
        return data.get_attributes(page=filter_type), filter_type

    if not checknumber(arg_page):
        filter_type = AttributeType.from_alias(arg_page)
        return from_filter_type(filter_type)

    arg_page = get_number(arg_page)
    if arg_page < 0 or arg_page >= len(BaseJx3UserAttributePage.types):
        arg_page = -1

    if arg_page == -1:
        # 默认取当前心法对应的配装
        current_kunfu = current.kungfu.type
        arg_page = BaseJx3UserAttributePage.types_mapper.get(current_kunfu)

    if arg_page > 0:
        # 设置了过滤则取对应，否则取全部
        page_setting = BaseJx3UserAttributePage.types[arg_page]
        return from_filter_type(page_setting[0])

    return data.attributes, AttributeType.Unknown


async def get_jx3_attribute3(template: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_server, arg_user, arg_page = template

    # 仅在30秒内缓存
    data = await Jx3PlayerDetailInfo.from_auto(arg_server, arg_user, cache_length=30)
    err_msg = '角色信息获取失败' if data is None else data.err_msg
    if err_msg:
        err_msg = f',原因:{err_msg}'
        return await jx3_cmd_attribute3.finish(f'未能找到来自[{arg_server}]的角色[{arg_user}]{err_msg}')
    user = data.user.to_dict()
    current = data.attributes[data.current_score]

    attributes, filter_type = get_attributes_from_data(data, arg_page)
    if no_DATA := not attributes:
        attributes = {f'{data.current_score}': current}
    attributes = [data.attributes[x].to_view() for x in attributes]

    result = {
        'user': user,
        'attributes': attributes,
        'no_data': no_DATA,
        'attributeType': filter_type.value,
        'attributeTypes': [[x[0].name, x[0].value, x[1]] for x in BaseJx3UserAttributePage.types],
        'attributeTypeDict': [[x.name, x.value] for x in AttributeType],
        'kunfu': current.kungfu.to_dict(),  # 当前心法
        'stone_slots': Jx3Stone.slot,
        'attributesTypeAvail': [],  # TODO 缓存历史可用的页面
    }
    return result


@jx3_cmd_attribute3.handle()
async def jx3_attribute3(template: list[Any] = Depends(Jx3Arg.arg_factory)):
    result = await get_jx3_attribute3(template)
    img = await get_render_image(f"src/views/jx3/user_attribute/common.html", result, delay=200)
    return await jx3_cmd_attribute3.send(ms.image(Path(img).as_uri()))
