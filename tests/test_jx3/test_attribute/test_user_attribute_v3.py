from ... import *


@pytest.mark.skipif('Jx3TuilanNoticeFactory' not in dir(), reason='无api可用')
@pytest.mark.skipif(not Config.jx3api_globaltoken, reason="无apitoken时不测试")
def test_fetch():
    task = Jx3PlayerDetailInfo.from_username('破阵子', '烤冷面不加蛋')
    data = asyncio.run(task)
    assert data.user
    assert data.attributes
    task = Jx3PlayerDetailInfo.from_username('斗转星移', '云澈')
    data = asyncio.run(task)
    assert data.user
    assert data.attributes

    # 判断是否有效存储
    filebase_database.Database.save_all()


@pytest.mark.skipif('Jx3TuilanNoticeFactory' not in dir(), reason='无api可用')
def test_fetch_by_uid():
    task = Jx3PlayerDetailInfo.from_uid('破阵子', '1234')
    data = asyncio.run(task)
    assert data is None  # 不存在或无效的

    task = Jx3PlayerDetailInfo.from_uid('破阵子', '3674275')
    data = asyncio.run(task)
    assert data.user
    assert data.attributes


@pytest.mark.skipif('Jx3TuilanNoticeFactory' not in dir(), reason='无api可用')
def test_user_not_exist():
    task = Jx3PlayerDetailInfo.from_username('唯满侠', '包某人')
    data = asyncio.run(task)
    assert data.uid is None and data.err_msg == PROMPT_UserNotExist  # 不存在或无效的


@pytest.mark.skipif('Jx3TuilanNoticeFactory' not in dir(), reason='无api可用')
def test_fetch_and_generate():
    import src.plugins.jx3
    func = src.plugins.jx3.jx3_attribute3
    mc = MessageCallback()
    src.plugins.jx3.user.v3.jx3_cmd_attribute3 = mc

    event = SFGroupMessageEvent(group_id=1120115)
    # event.message = obMessage("属性 唯满侠 包某 2")
    event.message = obMessage("属性 纵月 藏忧 3")

    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_attribute3, event)
    task = func(args)
    asyncio.run(task)
    mc.check_counter()
    # 重复进行一次判断缓存是否生效
    task = func(args)
    asyncio.run(task)
    mc.check_counter()


@pytest.mark.skipif('Jx3TuilanNoticeFactory' not in dir(), reason='无api可用')
def test_fetch_with_page():
    import src.plugins.jx3
    func = src.plugins.jx3.get_jx3_attribute3

    event = SFGroupMessageEvent(group_id=1120115)
    # event.message = obMessage("属性 唯满侠 而遇 pve-dps")
    event.message = obMessage("属性 纵月 藏忧 3")
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_attribute3, event)
    task = func(args)
    result = asyncio.run(task)
    assert AttributeType(result.get('attributeType')) == AttributeType.PVP | AttributeType.HPS
    assert result.get('attribute')

    event.message = obMessage("属性 纵月 藏忧 pvpdps")
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_attribute3, event)
    task = func(args)
    result = asyncio.run(task)
    assert AttributeType(result.get('attributeType')) == AttributeType.PVP | AttributeType.DPS
    assert result.get('attribute')

    event.message = obMessage("属性 纵月 藏忧 pve")
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_attribute3, event)
    task = func(args)
    result = asyncio.run(task)
    assert AttributeType(result.get('attributeType')) == AttributeType.PVE
    assert result.get('attribute')

    event.message = obMessage("属性 纵月 藏忧 pvehps")
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_attribute3, event)
    task = func(args)
    result = asyncio.run(task)
    assert AttributeType(result.get('attributeType')) == AttributeType.PVE | AttributeType.HPS
    assert result.get('attribute')

    event.message = obMessage("属性 纵月 藏忧 pvepvp")
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_attribute3, event)
    task = func(args)
    result = asyncio.run(task)
    assert AttributeType(result.get('attributeType')) == AttributeType.PVE | AttributeType.PVP
    assert result.get('no_data')
