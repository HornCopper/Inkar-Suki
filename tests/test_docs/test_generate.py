from .. import *


def test_docs_generate():
    from src.plugins.developer_tools import help_document
    raw_matcher = help_document.dev_cmd_show_help
    mc = MessageCallback()
    help_document.dev_cmd_show_help = mc

    func = help_document.dev_show_help
    state = {}
    event = SFGroupMessageEvent()
    event.message = obMessage(mc.tag)
    args = Jx3Arg.arg_factory(raw_matcher, event)
    ext.SyncRunner.as_sync_method(func(event, args))
    mc.check_counter()

    return state
