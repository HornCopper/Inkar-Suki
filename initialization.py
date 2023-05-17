import os, json
os.mkdir("./src/data")

def write(file, something):
    with open(f"./src/tools/{file}",mode="w") as cache:
        cache.write(something)

def space():
    print("----------------------分割线----------------------")
json_ = {}
if __name__ == "__main__":
    print("模块`github`需要使用`web_path`，如果您填写的值为`/a`，那么通过`http://127.0.0.1:2333/a`可传入Webhook，但内网显然不行，因此您需要手动配置Nginx或Apache2进行反向代理，代理地址为`http://127.0.0.1:2333/a`。")
    print("此处提供Nginx配置文件写法（当填入值为`/a`时：）")
    print("location = /")
    print("{")
    print("    proxy_pass http://127.0.0.1:2333/a;")
    print("}")
    web_path = input("请输入web_path的值：")
    json_["web_path"]=web_path
    space()
    print("模块`github`需要使用`bot`的值，，您需要获取您的Bot的QQ号，输入时请输入纯数字。")
    bot = int(input("请输入bot的值："))
    list_ = []
    list_.append(bot)
    json_["bot"] = list_
    space()
    print("模块`developer_tools`需要使用`platform`的值，请输入0或任意字符串，0代表`Bot`运行在`Windows`上，`任意字符串`则代表运行在`Linux`（最好是`Debian/Ubuntu`）上，请注意：仅有`Debian`和`Ubuntu`运行效果最佳，其他平台有或多或少的问题。")
    platform = int(input("请输入platform的值："))
    if platform == 0:
        json_["platform"] == False
    else:
        json_["platform"] == True
    space()
    print("模块`op`需要使用`owner`的值，这里请填写一个list（列表），列表内的值为`Bot`主人的QQ号。")
    print("不限数量，例如`[\"123456789\"]`或`[\"123456789\",\"234567890\"]都是可以的。`)
    owner = input("请输入owner的值：")
    owner = json.loads(owner)
    json_["owner"] == owner
    space()
    print("模块`developer_tools`需要使用`cqhttp`的值，请输入`go-cqhttp`的`HTTP`服务器地址，例如`http://127.0.0.1:2334/`，注意末尾处的`/`是必要的。")
    cqhttp = input("请输出cqhttp的值：")
    json_["cqhttp"] = cqhttp
    final = json.dumps(json_)
    write("config.json",final)
    write("ban.json","[]")
    write("permission.json","{}")
