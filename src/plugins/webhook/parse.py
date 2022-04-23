import re
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment as ms
class main:
    def push(body):
        pusher = body['pusher']['name']
        repo_name = body["repository"]["full_name"]
        commit = body['commits'][0]['message']
        ver = body["after"][0:6]
        return f"{pusher} pushed to {repo_name}.\n[{ver}]{commit}"
    def issues(body):
        action = body["action"]
        if action == "opened" or action == "closed" or action == "reopened":
            issue_actter = body["sender"]["login"]
            issue_num = str(body["issue"]["number"])
            issue_title = body["issue"]["title"]
            repo_name = body["repository"]["full_name"]
            issue_desc = body["issue"]["body"]
            msg = f"{issue_actter} {action} an issue on {repo_name}#{issue_num}.\nTitle:{issue_title}\nDescription:{issue_desc}"
            return msg
        elif action == "assigned" or action == "unassigned":
            issue_num = str(body["issue"]["number"])
            issue_title = body["issue"]["title"]
            repo_name = body["repository"]["full_name"]
            issue_desc = body["issue"]["body"]
            sender = body["sender"]["login"]
            assignee = body["assignee"]["login"]
            msg = f"{sender} {action} {assignee} on {repo_name}#{issue_num}.\nTitle:{issue_title}\nDescription:{issue_desc}"
            return msg
        elif action == "labeled" or "unlabeled":
            issue_num = str(body["issue"]["number"])
            issue_title = body["issue"]["title"]
            repo_name = body["repository"]["full_name"]
            issue_desc = body["issue"]["body"]
            label = body["label"]["name"]
            sender = body["sender"]["login"]
            msg = f"{sender} {action} \"{label}\" on {repo_name}#{issue_num}.\nTitle:{issue_title}\nDescription:{issue_desc}"
            return msg
    def issue_comment(body):
        action = body["action"]
        if action == "created":
            sender = body["sender"]["login"]
            msg = body["comment"]["body"]
            msg_regex = re.compile(r"!\[.*\]\((.*)\)")
            images = msg_regex.findall(msg)
            msg = re.sub(r"!\[.*\]\((.*)\)","[图片]",msg)
            for i in images:
                msg = msg + ms.image(i)          
            repo_name = body["repository"]["full_name"]
            issue_num = str(body["issue"]["number"])
            issue_title = body["issue"]["title"]
            msg = f"{sender} commented on {repo_name}#{issue_num}.\nTitle:{issue_title}\nDescription:{msg}"
            return msg
