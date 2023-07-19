from ... import *


def test_server_status():

    test_data = {
        'action': 2001,  # 开服
        'data': {
            'status': True,
            'server': '唯满侠'
        }
    }
    content = json.dumps(test_data)
    func = ws_client._handle_msg(content)
    asyncio.run(func)
    pass
