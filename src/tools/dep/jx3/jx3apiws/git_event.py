from fastapi import Request, FastAPI
from src.tools.config import *
from src.tools.utils import *
from src.tools.dep.bot.bot_env.github import *
import nonebot
app: FastAPI = nonebot.get_app()


@app.post(Config.web_path)
async def on_git_update(req: Request):
    body = await req.json()
    repo = body["repository"]["full_name"]
    event = req.headers.get("X-GitHub-Event")
    current_handler = GithubHandle
    # current_handler = GithubBaseParser
    message = getattr(current_handler, event)(body)
    logger.debug(f'on_git_update new message:{message}')
