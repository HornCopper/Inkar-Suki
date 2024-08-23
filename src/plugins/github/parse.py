from nonebot.adapters.onebot.v11 import MessageSegment as ms

import re

"""
解析类，没什么好看的。

建议自行查阅文档或者发起一些用于测试的`Webhook`以便于观察数据结构，欢迎`Pull Request`，此处仅解析部分常见`Event`。
"""

def process2(markdown_text: str):
    markdown_text = re.sub(r"```.*?```", "", markdown_text, flags=re.DOTALL)
    markdown_text = re.sub(r"#+ .*", "", markdown_text)
    markdown_text = re.sub(r"\n\s*\n", "\n", markdown_text)
    markdown_text = markdown_text.strip()
    return markdown_text

def process(raw: str):
    markdown_text = raw
    pattern = r"!\[([^]]*)\]\(([^)]*)\)" 
    matches = re.finditer(pattern, markdown_text)  
    processed_text = ""  
    current_pos = 0  
    for match in matches:  
        processed_text += markdown_text[current_pos:match.start()]  
        image_url = match.group(2)  
        result = ms.image(image_url)  
        processed_text += str(result)  
        current_pos = match.end()  
    processed_text += markdown_text[current_pos:]  
    return process2(processed_text)

class GithubBaseParser:
    def __init__(self):
        pass

    def push(self, body):
        pusher = body["pusher"]["name"]
        repo_name = body["repository"]["full_name"]
        if body["ref"].find("tags") != -1:
            tag = body["ref"]
            tag = tag[tag.find("refs/tags/")+10:]
            msg = f"{pusher} pushed to {repo_name}(Tag {tag})."
            return msg
        branch = body["ref"]
        branch = branch[branch.find("refs/heads/")+11:]
        commit = body["commits"][0]["message"]
        ver = body["commits"][0]["id"][0:7]
        msg = f"{pusher} pushed to {repo_name}:{branch}.\n[{ver}]{commit}"
        return msg

    def pull_request(self, body):
        action = body["action"]
        if action == "opened":
            source = body["pull_request"]["head"]["label"]
            goal = body["pull_request"]["base"]["label"]
            title = body["pull_request"]["title"]
            repo = body["repository"]["full_name"]
            sender = body["sender"]["login"]
            num = body["pull_request"]["number"]
            msg = f"{sender} opened a pull request on {repo}#{num}.\nFrom {source} to {goal}.\nTitle:{title}"
        elif action == "closed":
            source = body["pull_request"]["head"]["label"]
            goal = body["pull_request"]["base"]["label"]
            title = body["pull_request"]["title"]
            repo = body["repository"]["full_name"]
            sender = body["sender"]["login"]
            num = body["pull_request"]["number"]
            merged = body["pull_request"]["merged"]
            if merged is True:
                msg = f"{sender} merged the pull request on {repo}#{num}.\nFrom {source} to {goal}.\nTitle:{title}"
            else:
                msg = f"{sender} closed the pull request on {repo}#{num}.\nFrom {source} to {goal}.\nTitle:{title}"
        return msg

    def issues(self, body):
        action = body["action"]
        if action == "opened" or action == "closed" or action == "reopened":
            issue_actter = body["sender"]["login"]
            issue_num = str(body["issue"]["number"])
            issue_title = body["issue"]["title"]
            repo_name = body["repository"]["full_name"]
            if action == "opened":
                issue_comment = "\nComment:  " + process(body["issue"]["body"])
            else:
                issue_comment = ""
            msg = f"{issue_actter} {action} an issue on {repo_name}#{issue_num}.\nTitle: {issue_title}" + issue_comment
            return msg
        elif action == "assigned" or action == "unassigned":
            issue_num = str(body["issue"]["number"])
            issue_title = body["issue"]["title"]
            repo_name = body["repository"]["full_name"]
            issue_desc = body["issue"]["body"]
            sender = body["sender"]["login"]
            assignee = body["assignee"]["login"]
            msg = f"{sender} {action} {assignee} on {repo_name}#{issue_num}.\nTitle:{issue_title}\nComment: {issue_desc}"
            return msg
        elif action == "labeled" or action == "unlabeled":
            issue_num = str(body["issue"]["number"])
            issue_title = body["issue"]["title"]
            repo_name = body["repository"]["full_name"]
            label = body["label"]["name"]
            sender = body["sender"]["login"]
            msg = f"{sender} {action} \"{label}\" on {repo_name}#{issue_num}.\nTitle: {issue_title}"
            return msg
        elif action == "edited":
            issue_num = str(body["issue"]["number"])
            issue_title = body["issue"]["title"]
            repo_name = body["repository"]["full_name"]
            sender = body["sender"]["login"]
            from_ = body["changes"]["body"]["from"]
            to_ = body["issue"]["body"]
            user = body["issue"]["user"]["login"]
            if user == sender:
                user = "self"
            msg = f"{sender} {action} the comment by {user} on {repo_name}#{issue_num}.\nTitle: {issue_title}\nComment: {to_}"
            return msg

    def issue_comment(self, body):
        action = body["action"]
        if action == "created":
            try:
                body["issue"]["pull_request"]
                itype = "pull request"
            except Exception as _:
                itype = "issue"
            sender = body["sender"]["login"]
            msg = process(body["comment"]["body"]) 
            repo_name = body["repository"]["full_name"]
            issue_num = str(body["issue"]["number"])
            issue_title = body["issue"]["title"]
            msg = f"{sender} commented on {itype} on {repo_name}#{issue_num}.\nTitle:{issue_title}\nComment: {msg}"
            return msg

    def commit_comment(self, body):
        action = body["action"]
        if action == "created":
            sender = body["sender"]["login"]
            msg = process(body["comment"]["body"])  
            repo_name = body["repository"]["full_name"]
            commit = body["comment"]["commit_id"][0:7]
            msg = f"{sender} commented on {repo_name} commit {commit}.\n{msg}"
            return msg

    def release(self, body):
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

    def fork(self, body):
        to_ = body["forkee"]["full_name"]
        from_ = body["repository"]["full_name"]
        forker = body["sender"]["login"]
        total = body["repository"]["forks_count"]
        msg = f"{forker} forked from {from_} to {to_}.\n(total {total} forks)"
        return msg

    def ping(self, body):
        repo_name = body["repository"]["full_name"]
        return f"{repo_name} has already binded successfully."

    def watch(self, body):
        if body["action"] == "started":
            repo = body["repository"]["full_name"]
            sender = body["sender"]["login"]
            total = body["repository"]["watchers_count"]
            msg = f"{sender} started watching {repo}.\n(total {total} watchers)"
        return msg

    def star(self, body):
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