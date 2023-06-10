import requests
a = requests.get("https://tieba.baidu.com/f/search/res?ie=utf-8&qw=3328236362").text
b = open("D:/cheater.html", mode="w", encoding="utf-8")
b.write(a)
b.close()