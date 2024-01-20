from jx3_event import *
from fastapi import Request, FastAPI
from src.tools.config import *
from src.tools.utils import *
from src.tools.dep.bot.bot_env.github import *
import nonebot
app: FastAPI = nonebot.get_app()


class GithubUpdateEvent(RecvEvent):
    """更新推送事件"""

    __event__ = "WsRecv.GithubUpdate"
    message_type = "GithubUpdate"

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return {
            "type": "机器人更新",
            "msg": self.server
        }

@app.post(Config.web_path)
async def on_git_update(req: Request):
    body = await req.json()
    repo = body["repository"]["full_name"]
    event = req.headers.get("X-GitHub-Event")
    current_handler = GithubHandle
    # current_handler = GithubBaseParser
    message = getattr(current_handler, event)(body)
    logger.debug(f'on_git_update new message:{message}')

    event = GithubUpdateEvent()
    event.server = message
    await BotEventController.handle_msg(event)
