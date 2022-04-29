# Inkar Suki
[![License](https://img.shields.io/github/license/HornCopper/Inkar-Suki.svg)](LICENSE)
![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![OneBot Version](https://img.shields.io/badge/OneBot-v11-black.svg)
![GitHub pull requests](https://img.shields.io/github/issues-pr/HornCopper/Inkar-Suki)
![License](https://img.shields.io/github/license/HornCopper/Inkar-Suki)
![GitHub Repo stars](https://img.shields.io/github/stars/HornCopper/Inkar-Suki?style=social)
![GitHub Repo stars](https://img.shields.io/github/forks/HornCopper/Inkar-Suki?style=social)
![GitHub tag](https://img.shields.io/github/v/tag/HornCopper/Inkar-Suki?include_prereleases)
## 介绍
`Inkar Suki`是由`HornCopper`所编写，所有用户共同维护的`Python`机器人，基于`[Nonebot2](https://github.com/nonebot/nonebot2)开发`。

当然啦，你也可以叫她伊卡尔酱哦~

## 公告栏
> `Inkar Suki`正在规划`v0.8`大版本发布！此次更新有如下内容：
> - 将所有的绝对路径加入到配置文件中（`.env.dev`）；
> - 加入适配**所有MediaWiki**的wiki插件（目前仅适配[Minecraft Wiki](https://minecraft.fandom.com/zh/wiki/)和[维基百科](https://zh.wikipedia.org/wiki/)）。
## 使用
### 准备环境
#### 系统
- **强烈建议使用`Linux`**，若要使用`Windows`或`MacOS`，请注意平台兼容性。
- **强烈建议使用64位操作系统**，使用`x86`无大碍（除了性能限制），**使用`ARM`系统请注意平台兼容性。**
#### Python
- Python版本限制是`3.8`以上，当然，这**不是硬性限制**，你依然可以较低的版本，但是最低硬性限制是`3.7.3`。
- 建议使用`64-bit`（`amd64`，`x64`都是一样的意思），**部分小伙伴的电脑可能是32位系统+64位CPU，建议上网查询一下参数，避免被黑心电脑商家安装的系统所欺骗！**
- 如果是Windows用户，安装的时候请一定要勾选`添加至PATH`之类的字眼，否则`pip`可能无法直接使用。
- 如果是Linux用户，编译安装的时候请一定记得安装完成后创建到`/usr/local/bin`的软链接文件以便直接使用（`python`和`python3`以及`pip`和`pip3`等）。
#### 第三方库
~~想要偷懒？
`
pip install -r requirements.txt
`~~
