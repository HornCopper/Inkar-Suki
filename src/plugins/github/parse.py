import re
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment as ms
class main:
    def push(body):
        pusher = body["pusher"]["name"]
        repo_name = body["repository"]["full_name"]
        if body["ref"].find("tags") != -1:
            tag = body["ref"]
            tag = tag[tag.find("refs/tags/")+10:]
            msg =  f"{pusher} pushed to {repo_name}(Tag {tag})."
            return msg
        branch = body["ref"]
        branch = branch[branch.find("refs/heads/")+11:]
        commit = body["commits"][0]["message"]
        ver = body["commits"][0]["id"][0:7]
        msg = f"{pusher} pushed to {repo_name}:{branch}.\n[{ver}]{commit}"
        return msg
    def pull_request(body):
        action = body["action"]
        if action == "opened":
            source = body["pull_request"]["head"]["label"]
            goal = body["pull_request"]["base"]["label"]
            title = body["pull_request"]["title"]
            comment = body["pull_request"]["body"]
            repo = body["repository"]["full_name"]
            sender = body["sender"]["login"]
            num = body["pull_request"]["number"]
            msg = f"{sender} opened a pull request on {repo}#{num}.\nFrom {source} to {goal}.\nTitle:{title}\nDescription:{comment}"
        elif action == "closed":
            source = body["pull_request"]["head"]["label"]
            goal = body["pull_request"]["base"]["label"]
            title = body["pull_request"]["title"]
            comment = body["pull_request"]["body"]
            repo = body["repository"]["full_name"]
            sender = body["sender"]["login"]
            num = body["pull_request"]["number"]
            merged = body["pull_request"]["merged"]
            if merged == True:
                msg = f"{sender} closed the pull request on {repo}#{num}.\nFrom {source} to {goal}.\n(Already merged)\nTitle:{title}\nDescription:{comment}"
            else:
                msg = f"{sender} closed the pull request on {repo}#{num}.\nFrom {source} to {goal}.\nTitle:{title}\nDescription:{comment}"
        return msg
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
        elif action == "labeled" or action == "unlabeled":
            issue_num = str(body["issue"]["number"])
            issue_title = body["issue"]["title"]
            repo_name = body["repository"]["full_name"]
            issue_desc = body["issue"]["body"]
            label = body["label"]["name"]
            sender = body["sender"]["login"]
            msg = f"{sender} {action} \"{label}\" on {repo_name}#{issue_num}.\nTitle:{issue_title}\nDescription:{issue_desc}"
            return msg
        elif action == "edited":
            issue_num = str(body["issue"]["number"])
            issue_title = body["issue"]["title"]
            repo_name = body["repository"]["full_name"]
            sender = body["sender"]["login"]
            from_ = body["changes"]["body"]["from"]
            to_ = body["issue"]["body"]
            user = body["issue"]["user"]["login"]
            msg = f"{sender} {action} the comment by {user} on {repo_name}#{issue_num}.\nTitle:{issue_title}\nSource Commment:{from_}\nChanged Comment:{to_}"
            return msg
    def issue_comment(body):
        action = body["action"]
        if action == "created":
            try:
                pr = body["issue"]["pull_request"]
                itype = "pull request"
            except:
                itype = "issue"
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
            msg = f"{sender} commented on {itype} on {repo_name}#{issue_num}.\nTitle:{issue_title}\nDescription:{msg}"
            return msg
    def commit_comment(body):
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
            commit = body["comment"]["commit_id"][0:7]
            msg = f"{sender} commented on {repo_name} commit {commit}.\n{msg}"
            return msg
    def release(body):
        action = body["action"]
        if action == "created":
            sender = body["sender"]["login"]
            repo_name = body["repository"]["full_name"]
            release_name = body["release"]["name"]
            tag_name = body["release"]["tag_name"]
            msg = f"{sender} created a release on {repo_name}.\n{tag_name} - {release_name}"
            return msg
        elif action == "published":
            sender = body["sender"]["login"]
            repo_name = body["repository"]["full_name"]
            release_name = body["release"]["name"]
            tag_name = body["release"]["tag_name"]
            release_msg = body["release"]["body"]
            msg = f"{sender} published a release on {repo_name}.\n{tag_name} - {release_name}\n{release_msg}"
            return msg
        elif action == "released":
            sender = body["sender"]["login"]
            repo_name = body["repository"]["full_name"]
            release_name = body["release"]["name"]
            tag_name = body["release"]["tag_name"]
            msg = f"{sender} released a release on {repo_name}.\n{tag_name} - {release_name}"
            return msg
    def fork(body):
        to_ = body["forkee"]["full_name"]
        from_ = body["repository"]["full_name"]
        forker = body["sender"]["login"]
        total = body["repository"]["forks_count"]
        msg = f"{forker} forked from {from_} to {to_}.\n(total {total} forks)"
        return msg
    def ping(body):
        repo_name = body["repository"]["full_name"]
        return f"{repo_name} has already binded successfully."
    def watch(body):
        if body["action"] == "started":
            repo = body["repository"]["full_name"]
            sender = body["sender"]["login"]
            total = body["repository"]["watchers_count"]
            msg = f"{sender} started watching {repo}.\n(total {total} watchers)"
        return msg
    def star(body):
        if body["action"] == "created":
            sender = body["sender"]["login"]
            repo = body["repository"]["full_name"]
            total = body["repository"]["stargazers_count"]
            msg = f"{sender} starred {repo}.\n(total {total} stargazers)"
        elif body["action"] == "deleted":
            sender = body["sender"]["login"]
            repo = body["repository"]["full_name"]
            total = body["repository"]["stargazers_count"]
            msg = f"{sender} cancelled starring {repo}.\n(total {total} stargazers)"
        return msg