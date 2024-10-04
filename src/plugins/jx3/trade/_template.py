template_msgbox = """
<div class="message-box">
    <div class="element">
        <div class="cell"><span style="color:green">当日最低价↓</span></div>
        <div class="cell">{{ low }}</div>
    </div>
    <div class="element">
        <div class="cell">当日均价</div>
        <div class="cell">{{ avg }}</div>
    </div>
    <div class="element">
        <div class="cell"><span style="color:red">当日最高价↑</span></div>
        <div class="cell">{{ high }}</div>
    </div>
</div>"""

template_table = """
<tr>
    <td class="short-column"><img src="{{ icon }}"></td>
    <td class="short-column"><span style="color:rgb{{ color }}">{{ name }}</span></td>
    <td class="short-column">{{ time }}</td>
    <td class="short-column">{{ limit }}</td>
    <td class="short-column">{{ price }}</td>
</tr>"""

template_wujia = """
<tr>
    <td>{{ date }}</td>
    <td>{{ server }}</td>
    <td>{{ price }}</td>
</tr>"""

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Host": "www.aijx3.cn",
    "Origin": "https://wj.aijx3.cn",
    "Referer": "https://wj.aijx3.cn/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "wjKey": "auHxiYtcg59JEtZ5nARiX8gLPcWt2ut9"
}

aliases_map = {
    "金羁饰影礼盒": "金羁饰影三选一礼盒"
}