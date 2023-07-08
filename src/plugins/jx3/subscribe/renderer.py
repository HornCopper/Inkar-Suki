from src.tools.dep import *
from src.plugins.jx3.subscribe.SubscribeRegister import *


async def render_subscribe(VALID_Subjects: dict[str, SubscribeSubject], subscribe_info: dict[str, dict], subject: SubscribeSubject, message: str = None):
    '''
    渲染订阅信息
    '''
    total = [VALID_Subjects[x].to_dict() for x in VALID_Subjects]
    data = {
        'all_subjects': total,
        'message': message,
        'subscribe_info': subscribe_info,
        'subject': subject and subject.to_dict(),
    }
    img = await get_render_image('src/views/jx3/subscribe/status.html', data)
    return img
