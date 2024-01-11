from .BaseCatalog import *


class permission(BaseCatalog):
    '''权限根节点'''
    class jx3(BaseCatalog):
        '''剑网三'''
        class pvp(BaseCatalog):
            '''pvp'''
            class jjc(BaseCatalog):
                '''竞技场'''
                class records(BaseCatalog):
                    '''战绩'''
                class rank(BaseCatalog):
                    '''排行榜'''
                class statistics(BaseCatalog):
                    '''统计'''
            class gf(BaseCatalog):
                '''攻防'''
                class worldmap(BaseCatalog):
                    '''沙盘'''
            class user(BaseCatalog):
                '''角色'''
                class property(BaseCatalog):
                    '''属性'''
                class location(BaseCatalog):
                    '''定位'''
        class pve(BaseCatalog):
            '''pve'''
        class pvx(BaseCatalog):
            '''pvx'''
            class property(BaseCatalog):
                '''资产'''
                class horse(BaseCatalog):
                    '''马匹'''
                    class chitu(BaseCatalog):
                        '''赤兔'''
                    class dilu(BaseCatalog):
                        '''的卢'''
                    class info(BaseCatalog):
                        '''马场'''
        class pvg(BaseCatalog):
            '''pvg'''
            class price(BaseCatalog):
                '''物价'''
                class trade(BaseCatalog):
                    '''交易行'''
                class wbl(BaseCatalog):
                    '''万宝楼'''
                class tieba(BaseCatalog):
                    '''贴吧'''
        class common(BaseCatalog):
            '''通用'''
            class wiki(BaseCatalog):
                '''萌新接引人'''
            class event(BaseCatalog):
                '''事件'''
                class subscribe(BaseCatalog):
                    '''订阅'''
                class notice(BaseCatalog):
                    '''公告'''
    class mgr(BaseCatalog):
        '''机器人管理'''
        class group(BaseCatalog):
            '''群管理'''
            class exit(BaseCatalog):
                '''退群'''
            class apply(BaseCatalog):
                '''申请'''
    class user(BaseCatalog):
        '''用户管理'''
        class group(BaseCatalog):
            '''群管理'''
    class bot(BaseCatalog):
        '''机器人配置'''
        class docs(BaseCatalog):
            '''文档配置'''
            class help(BaseCatalog):
                '''帮助文档'''
        class group(BaseCatalog):
            '''机器人群'''
            class apply(BaseCatalog):
                '''处理申请'''
