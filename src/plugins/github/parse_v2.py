from .parse import main
from src.tools.dep import *


class GithubHandle(main):
    def push(body):
        pusher = body["pusher"]["name"]
        commits = [x.get('message') for x in body.get('commits')]
        return f'{Config.name}又偷偷给自己更新啦~本次更新了来自{pusher}的{len(commits)}个包'

    def pull_request(body):
        action = '申请的新更新' if body["action"] == 'opened' else '已批准的更新'
        sender = body["sender"]["login"]
        source = body["pull_request"]["head"]["label"]
        return f'{Config.name}准备要更新啦~本次是来自{sender}的{action}。更新到{source}'
