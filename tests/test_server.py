def test_server_map():
    from src.plugins import jx3
    assert jx3.server_mapping('唯满侠') == '唯我独尊'
    assert jx3.server_mapping('双梦') == '梦江南'
    assert jx3.server_mapping('风骨霸刀') == '绝代天骄'
    assert jx3.server_mapping('飞龙在天') == '飞龙在天'
    assert jx3.server_mapping('念破') == '破阵子'
    pass
