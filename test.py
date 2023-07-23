# from tests.test_jx3.test_pvx.test_flower import test_flower_price as func
# func()
import re
raw = '''
`    # 以上三者都请访问：“https://vip.jx3api.com”

    sfapi_wslink = "123"  # SFAPI WebSocket地址

    sfapi_wstoken = ""  # SFAPI WebSocket Token

    ght = ""  # GitHub Personal Access Token

'''
xxx = re.compile('(sfapi_wstoken)[ ]*=[ ]*"(\w*)"')
x = xxx.search(raw)
v = x.span()
print(v[0],v[1])
print(raw[v[0]:v[1]])