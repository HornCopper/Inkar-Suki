# Inkar Suki
[![License](https://img.shields.io/github/license/HornCopper/Inkar-Suki.svg)](LICENSE)
![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![OneBot Version](https://img.shields.io/badge/OneBot-v11-black.svg)
![GitHub pull requests](https://img.shields.io/github/issues-pr/HornCopper/Inkar-Suki)
![License](https://img.shields.io/github/license/HornCopper/Inkar-Suki)
![GitHub Repo stars](https://img.shields.io/github/stars/HornCopper/Inkar-Suki?style=social)
![GitHub Repo stars](https://img.shields.io/github/forks/HornCopper/Inkar-Suki?style=social)
![GitHub tag](https://img.shields.io/github/v/tag/HornCopper/Inkar-Suki?include_prereleases)
[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=HornCopper&repo=Inkar-Suki)](https://github.com/anuraghazra/github-readme-stats)
## 介绍
`Inkar Suki`是由`HornCopper`所编写，所有用户共同维护的`Python`机器人，基于[Nonebot2](https://github.com/nonebot/nonebot2)开发。

当然啦，你也可以叫她伊卡尔酱哦~

## 公告栏
> `Inkar Suki`正在规划`v0.8`大版本发布！此次更新有如下内容：
> - ~~将所有的绝对路径加入到配置文件中.env.dev~~（`v0.7.5-Hotfix`已修改为`config.py`）
> - 加入适配**所有MediaWiki**的wiki插件（目前仅适配[Minecraft Wiki](https://minecraft.fandom.com/zh/wiki/)和[维基百科](https://zh.wikipedia.org/wiki/)）。 
> - 正在迁移到新的文档！[Inkar-Suku Docs](https://www.inkar-suki.xyz/docs)
<!--
## 使用
### 准备环境
#### 系统
- **强烈建议使用`Linux`（尤其是`Debian`系）**，这样您的手动配置可以最少，若要使用`Windows`或`MacOS`，请注意平台兼容性。
- **强烈建议使用64位操作系统**，使用`x86`无大碍（除了性能限制），**使用`ARM`系统请注意平台兼容性。**
#### Python
- Python版本限制是`3.8`以上，当然，这**不是硬性限制**，你依然可以较低的版本，但是最低硬性限制是`3.7.3`。
- 建议使用`64-bit`（`amd64`，`x64`都是一样的意思），**部分小伙伴的电脑可能是32位系统+64位CPU，建议上网查询一下参数，避免被黑心电脑商家安装的系统所欺骗！**
- 如果是Windows用户，安装的时候请一定要勾选`添加至PATH`之类的字眼，否则`pip`可能无法直接使用。
- 如果是Linux用户，编译安装的时候请一定记得安装完成后创建到`/usr/local/bin`的软链接文件以便直接使用（`python`和`python3`以及`pip`和`pip3`等）。
#### 第三方库
~~想要偷懒？`pip install -r requirements.txt`~~
如果实在不想偷懒，那建议您自己去找了（
#### Chrome
运行下面的命令下载`Chrome`的安装包（以`Debian`系为例）：
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
```
随后，安装：
```bash
sudo dpkg -i google-chrome-stable_current_amd64.deb
```
- 如果使用`32位`操作系统，请将`amd64`改为`i386`。
- 安装完毕后，请前往[ChromeDriver](https://chromedriver.storage.googleapis.com/index.html)网站下载对应版本的`ChromeDriver`，将其放置在服务器上并在`src/tools/config.py`中写清楚**绝对路径**（Chrome的版本可通过`google-chrome --version`查看，如无法执行，请检查安装是否成功！）。
- 另外请运行`apt install psmisc`补全所需软件。
### 配置
首先打开我们的`.env.dev`，你会看到如下内容。
```dotenv
HOST=127.0.0.1
PORT=2333
COMMAND_START=["+"]

[FastAPI]
fastapi_reload = true
```
其中`PORT`和`HOST`可根据`go-cqhttp`的配置进行修改。
- `COMMAND_START`即命令前缀，比如`/cmd aabbb`中`/`即为前缀，以此类推，默认为`+`（某些地方也称为`明确调用`）。
你需要在`COMMAND_START`下方加一行`SUPERUSERS`，假设`QQ号`是`123456789`，那么请填写为`SUPERUSERS=["123456789"]`，具体可参考[Nonebot 2文档](https://v2.nonebot.dev/docs/tutorial/configuration)。
然后打开`bot.py`，找到这段代码：
```python3
nonebot.init(tools_path="C:/Users/HornC/Inkar-Suki/src/tools")
```
将其中的路径改为你想使用的路径，注意必须是绝对路径，~~相对路径懒得试~~。
**这样还没完哦**，打开`Inkar-Suki/src/tools`，这里有个`config.py`，~~这才是费脑的地方~~。
这里是默认配置：
```python3
class Config:
    '''
    Inkar-Suki内部的配置
    <变量名>:<类型> - <含义> - <格式>

    web_path: str - Webhook的路径 - "/webhook"
    bot: str - Bot的QQ号码 - ["123456789"]
    platform: bool - Bot运行平台，True为Linux，False为Windows - 格式：True或False
    owner: str - 您的QQ号/Bot主人 - 格式：Any
    html_path: str - help插件所生成的html的存放位置 - 格式："C:/Path/To/Your/HTML"
    size_path: str - help插件所生成的帮助图片的尺寸 - 格式："nxn"
    chromedriver_path: str - ChromeDriver的可执行文件存放位置 - 格式："C:/Path/To/Your/ChromeDriver"
    help_image_save_to: str - help插件所生成的png图片存放位置 - 格式："C:/Path/To/Your/ImagePath"
    font_path: str - help插件所用字体 - 格式："C:/Path/To/Your/TTF"
    global_path: str - 全局路径/插件路径，即src/plugins目录下的绝对路径 - 格式："C:/Bot/src/plugin"
    cqhttp: str - CQHTTP服务器 - 格式："http://127.0.0.1:2333/" 
    '''
    web_path = ""
    bot = ""
    platform = False
    owner = ""
    size = ""
    html_path = ""
    chromedriver_path = ""
    help_image_save_to = ""
    font_path = ""
    global_path = ""
    cqhttp = ""
```
- `web_path`作用在`webhook`插件中，主要控制`Webhook`的收地址，例如`Nonebot`已设置为`http://127.0.0.1:2333`，那么`http://127.0.0.1:2333/webhook`就是收取Webhook的地址；
- `bot`作用在`webhook`插件中，主要控制`Bot`传参，请填入您的Bot的`QQ`号，注意要打`"`或`'`；
- `platform`作用在`smallcmd`，主要控制不同平台的`关闭`操作，注意只能填`布尔值`（`True`或`False`）；
- `owner`作用在`op`，主要控制Bot的主人是谁，只能填字符串，例如`"123456789"`；
- `size`作用在`help`，控制帮助图片生成的尺寸，填入字符串，形如`axa`，`a`是纯数字，两处不必相同；
- `html_path`作用在`help`，控制帮助图片所依赖的`HTML`源文件的路径，填入字符串，形如`"C:/Bot/test.html`；
- `chromedriver_path`作用在`help`，请填入指向`chromedriver`可执行文件的**绝对路径**；
- `help_image_save_to`作用在`help`，请填入形如`"C:/cache.png"`的字符串；
- `font_path`作用在`help`，请填入形如`"file:///root/main.ttf"`或`"file://C:/main.ttf"`的字符串；
- `global_path`作用在`help`，请填入指向`src/plugins`文件夹的**绝对路径**；
- `cqhttp`作用在`sign`，请填入`CQHTTP`服务器的链接，参考`go-cqhttp`文档（见下）。

这里有一份运行在`/root/nb/`下的`Inkar Suki`实例，配置是这样的：
```python3
class Config:
    web_path = "/webhook" #意思是http://127.0.0.1:2333/webhook即为Webhook接收地址，2333端口在.env.dev中定义过了
    bot = ["3438531564"] #公共实例QQ号
    platform = True #使用Debian 11
    owner = "3349104868" #作者QQ号，这里填主人的QQ就可以了
    size = "750x1730" #帮助图片的尺寸
    html_path = "/root/nb/src/plugins/help/help.html" #帮助HTML的路径
    chromedriver_path = "/root/nb/src/plugins/help/chromedriver" #ChromeDriver可执行文件的路径，注意要安装Chrome对应版本！
    help_image_save_to = "/root/nb/src/plugins/help/help.png" #生成后的图片的保存位置
    font_path = "file:///root/nb/src/plugins/help/oppo_sans.ttf" #字体位置
    global_path = "/root/nb/src/plugins/" #全局路径
    cqhttp = "http://127.0.0.1:2334/" #CQHTTP服务器
```
> 有关`go-cqhttp`的配置，请前往`文档`（[点此前往](https://docs.go-cqhttp.org)）。
### 运行
由于第三方库补全时已经补全了`nb-cli`，**如果环境变量没有出问题**，那么可以用`nb run`启动，反之，请使用`python3 bot.py`。
## FAQ
### 为什么更新如此频繁，几乎几分钟就更新一次？
由于开发者能力不够强大，人员也只有1个，写代码方面可能会有些漏洞，但是一般commit都不是什么bug，偶尔才会有，请您下载release中最新版。
-->
