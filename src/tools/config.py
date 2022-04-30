class Config:
    '''
    Inkar-Suki内部的配置
    <变量名>:<类型> - <含义> - <格式>

    web_path: str - Webhook的路径 - "/webhook"
    bot: str - Bot的QQ号码 - "123456789"
    platform: bool - Bot运行平台，True为Linux，False为Windows - 格式：True或False
    owner: str - 您的QQ号/Bot主人 - 格式：Any
    html_path: str - help插件所生成的html的存放位置 - 格式："C:/Path/To/Your/HTML"
    size: str - help插件所生成的帮助图片的尺寸 - 格式："nxn"
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