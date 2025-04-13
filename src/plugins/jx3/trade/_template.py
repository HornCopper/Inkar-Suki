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

template_v3_name_unique = """
<span style="color: rgb{{ color }}">{{ name }}</span>"""

template_v3_name_mulit = """
<div style="display: flex;align-items: center;">
        <img src="{{ icon }}" style="margin-right: 10px;">
        <span style="color: rgb{{ color }}">{{ name }}</span>
</div>
"""

template_v3_price = """
<tr>
    <td><span class="server-tag">{{ server }}</span></td>
    <td>{{ name }}</td>
    <td class="time-cell">{{ time }}</td>
    <td>{{ count }}</td>
    <td class="price-cell">
        {{ price }}
    </td>
    <td>{{ percent }}</td>
</tr>
"""

template_v3_log = """
<div class="summary-card">
    <h3>30日底价</h3>
    <div class="summary-value">
        {{ lowest }}
    </div>
</div>
<div class="summary-card">
    <h3>30日均价</h3>
    <div class="summary-value">
        {{ avg }}
    </div>
</div>
<div class="summary-card">
    <h3>30日顶价</h3>
    <div class="summary-value">
        {{ highest }}
    </div>
</div>
"""

template_v3_element_prefix = """
<p><strong>品级</strong>：{{ quality }}</p>
<p><strong>属性</strong>：<span style="color: rgb(0, 210, 75)">{{ attr }}</span></p>
"""
template_v3_element = """
<p><strong>效果</strong>：<span style="color: rgb(0, 210, 75);font-size: 18px">{{ effect }}</span></p>"""

template_v3_element_shilian = """
<p><strong>无修</strong>：<span style="color: rgb(255, 165, 0);font-size: 18px">{{ special }}</span></p>"""

template_v3_info = """
<div class="item-info">
    <div class="item-info-left">
        <h2 style="display: flex;align-items: center">
            <img src="{{ icon }}"
                style="width: 50px;height: 50px;margin-right: 10px;">
            <span style="color: rgb{{ color }}">{{ name }}</span>
        </h2>
        {{ element }}
    </div>
    <div class="item-info-right">
        <p><strong>页眉价参考日期</strong>：<br>{{ date }}</p>
    </div>
</div>"""