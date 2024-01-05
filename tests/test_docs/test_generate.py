from .. import *


def test_docs_generate():
    import src.plugins.developer_tools.help_document
    raw_matcher = src.plugins.developer_tools.help_document.dev_cmd_show_help
    mc = MessageCallback()
    src.plugins.developer_tools.help_document.dev_cmd_show_help = mc

    func = src.plugins.developer_tools.help_document.dev_show_help
    state = {}
    event = SFGroupMessageEvent()
    event.message = obMessage(mc.tag)
    args = Jx3Arg.arg_factory(raw_matcher, event)
    task = ext.SyncRunner.as_sync_method(func(event, args))
    mc.check_counter()

    return state
