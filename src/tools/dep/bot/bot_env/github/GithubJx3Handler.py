from .GithubBaseParser import *
from src.tools.config import *


class GithubHandle(GithubBaseParser):
    def push(body):
        pusher = body["pusher"]["name"]
        commits = [x.get('message') for x in body.get('commits')]
        return f'{Config.name}又偷偷给自己更新啦~本次更新了来自{pusher}的{len(commits)}个包'

    def pull_request(body):
        action = body["action"]
        if action == 'opened':
            action = '申请的新更新'
        elif action == 'closed':
            action = '已批准的更新'
        else:
            return  # 不处理其他情况
        sender = body["sender"]["login"]
        source = body["pull_request"]["head"]["label"]
        return f'{Config.name}准备要更新啦~本次是来自{sender}的{action}。更新到{source}'

    def check_run(body):
        return ''

    def workflow_job(body):
        return ''
