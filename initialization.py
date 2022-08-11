import os, json
def space():
    print("----------------------分割线----------------------")
try:
    os.mkdir("./src/data")
except FileExistsError:
    print("检测到`data`文件夹已创建。")
try:
    os.mkdir("./src/cache")
except FileExistsError:
    print("检测到`cache`文件夹已创建。")
try:
    os.mkdir("./src/assets")
    os.mkdir("./src/assets/arcaea")
    os.mkdir("./src/assets/arcaea/char")
    os.mkdir("./src/assets/arcaea/icon")
    os.mkdir("./src/assets/arcaea/song")
    os.mkdir("./src/assets/jx3")
    os.mkdir("./src/assets/jx3/skills")
    os.mkdir("./src/assets/jx3/icons")
    os.mkdir("./src/assets/jx3/maps")
    os.mkdir("./src/assets/jx3/achievement")
    os.mkdir("./src/assets/jx3/talents")
except FileExistsError:
    print("检测到`assets`文件夹已创建，已自动补全所有需要的文件夹。")
def write(file, something):
    with open(f"./src/tools/{file}",mode="w") as cache:
        cache.write(something)
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
    list_.append(str(bot))
    json_["bot"] = list_
    space()
    print("模块`developer_tools`需要使用`platform`的值，请输入0或任意字符串，0代表`Bot`运行在`Windows`上，`任意字符串`则代表运行在`Linux`（最好是`Debian/Ubuntu`）上，请注意：仅有`Debian`和`Ubuntu`运行效果最佳，其他平台有或多或少的问题。")
    platform = input("请输入platform的值：")
    if platform == "0":
        platform = False
    else:
        platform = bool(platform)
    json_["platform"] = platform
    if platform:
        abpath = __file__.replace("\\","/")[:-17] + "src/tools"
    else:
        abpath = __file__[:-17] + "src/tools"
    json_["abpath"] = abpath
    space()
    print("模块`op`需要使用`owner`的值，这里请填写一个list（列表），列表内的值为`Bot`主人的QQ号。")
    print("不限数量，例如`[\"123456789\"]`或`[\"123456789\",\"234567890\"]都是可以的。`")
    owner = input("请输入owner的值：")
    owner = json.loads(owner)
    permission = {}
    for i in owner:
        permission[i] = 10
    json_["owner"] = owner
    space()
    print("模块`developer_tools`需要使用`cqhttp`的值，请输入`go-cqhttp`的`HTTP`服务器地址，例如`http://127.0.0.1:2334`。")
    cqhttp = input("请输出cqhttp的值：")
    if cqhttp[-1] != "/":
        cqhttp = cqhttp + "/"
    json_["cqhttp"] = cqhttp
    space()
    print("模块`arcaea`使用了AUA（ArcaeaUnlimitedAPI），需要Token和API链接，请先输入API链接，格式为`https://xxx.xxx/botarcapi/`信息仅保存至本地，若有怀疑可检查源代码。")
    print("同时请您也务必保管好个人信息。")
    aua_api = input("请输入API地址：")
    json_["aua_api"] = aua_api
    space()
    print("Token也是必要的，没有固定格式，请输入AUA开发者给予你的Token。")
    aua_token = input("请输入Token：")
    json_["aua_token"] = aua_token
    final = json.dumps(json_)
    write("config.json",final)
    space()
    def clear():
        clean = input("是否需要重置ban.json、nnl.json和permission三个json文件，若初次使用请填写y(y/n)：")
        if clean == "y":
            write("ban.json","[]")
            write("permission.json",json.dumps(permission))
            write("nnl.json","[]")
            return
        elif clean == "n":
            return
        else:
            print("输出错误，请重试。")
            clear()
    clear()
    space()    
