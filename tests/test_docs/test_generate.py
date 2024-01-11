from .. import *


def test_docs_generate():
    from src.plugins.developer_tools import help_document
    raw_matcher = help_document.dev_cmd_show_help
    mc = MessageCallback()
    mc.name = 'show_help'
    help_document.dev_cmd_show_help = mc

    func = help_document.dev_show_help
    state = {}
    event = SFGroupMessageEvent()
    event.group_id = 776484255
    mc.tag = ''
    event.message = obMessage(mc.tag)
    args = Jx3Arg.arg_factory(raw_matcher, event)
    ext.SyncRunner.as_sync_method(func(None, event, args))
    mc.check_counter()

    return state


def test_docs_generate_detail():
    from src.plugins.developer_tools import help_document
    raw_matcher = help_document.dev_cmd_show_help
    mc = MessageCallback()
    mc.name = 'show_help'
    help_document.dev_cmd_show_help = mc

    func = help_document.dev_show_help
    state = {}
    event = SFGroupMessageEvent()
    event.group_id = 776484255
    mc.tag = '帮助 属性'
    event.message = obMessage(mc.tag)
    args = Jx3Arg.arg_factory(raw_matcher, event)
    ext.SyncRunner.as_sync_method(func(None, event, args))
    mc.check_counter()

    return state
