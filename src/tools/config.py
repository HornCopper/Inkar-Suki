class Config:
    web_path = "/webhook" #意思是http://127.0.0.1:2333/webhook即为Webhook接收地址，2333端口在.env.dev中定义过了
    bot = ["3438531564"] #公共实例QQ号
    platform = True #使用Debian 11
    owner = "3349104868" #作者QQ号，这里填主人的QQ就可以了
    size = "1000x1730" #帮助图片的尺寸
    html_path = "/root/Inkar-Suki/src/plugins/help/help.html" #帮助HTML的路径
    chromedriver_path = "/root/Inkar-Suki/src/plugins/help/chromedriver" #ChromeDriver可执行文件的路径，注意要安装Chrome对应版本！
    help_image_save_to = "/root/Inkar-Suki/src/plugins/help/help.png" #生成后的图片的保存位置
    font_path = "file:///root/Inkar-Suki/src/plugins/help/oppo_sans.ttf" #字体位置
    global_path = "/root/Inkar-Suki/src/plugins/" #全局路径
    cqhttp = "http://127.0.0.1:2334/" #CQHTTP服务器
    version = "0.7.5-Hotfix"