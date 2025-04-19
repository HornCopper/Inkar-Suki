star = """
<svg width="20" height="20">
    <polygon points="10,0 13,7 20,7 14,12 16,19 10,15 4,19 6,12 0,7 7,7" style="fill:gold; stroke:gold; stroke-width:1px;" />
</svg>
"""

template_drop = """
<tr>
    <td class="short-column">
        <img src="{{ icon }}"></img>
    </td>
    <td class="short-column">{{ name }}</td>
    <td class="short-column">
        <div class="attrs">{{ attrs }}</div></td>
    <td class="short-column">{{ type }}</td>
    <td class="short-column">
        {{ stars }}
    </td>
    <td class="short-column">{{ quality }}</td>
    <td class="short-column">{{ score }}</td>
    <td class="short-column"><div class="attrs">{{ fivestone }}</div></td>
</tr>
"""

table_drop_head = """
<tr>
    <th class="short-column">图鉴</th>
    <th class="short-column">名称</th>
    <th class="short-column">属性</th>
    <th class="short-column">类型</th>
    <th class="short-column">最大精炼等级</th>
    <th class="short-column">品质等级</th>
    <th class="short-column">装备分数</th>
    <th class="short-column">熔嵌孔属性</th>
</tr>"""

template_zone_record = """
<tr>
    <td class="short-column">{{ zone_name }}</td>
    <td class="short-column">{{ zone_mode }}</td>
    <td>
    {{ images }}
    </td>
</tr>
"""

template_item = """
<tr>
    <td class="short-column">{{ time }}</td>
    <td class="short-column">{{ relate }}</td>
    <td class="short-column">{{ name }}</td>
    <td class="short-column">{{ role }}</td>
    <td class="short-column">{{ server }}</td>
    <td class="short-column">{{ map }}</td>
</tr>
"""

image_template = """
<img src="{{ image_path }}" height="20" width="20"></img>
"""

table_zone_record_head = """
<tr>
    <th class="short-column">副本</th>
    <th class="short-column">难度</th>
    <th>进度</th>
</tr>"""

table_item_head = """
<tr>
    <th class="short-column">时间</th>
    <th class="short-column">参考</th>
    <th class="short-column">物品</th>
    <th class="short-column">角色</th>
    <th class="short-column">区服</th>
    <th class="short-column">地图</th>
</tr>"""

template_monsters = """
<div class="el-tooltip u-column{{ flag }}">
    <div class="u-img"><img src="{{ icon }}" class="u-effect"></div>
    <div class="u-index"><span class="u-index-number">{{ count }}</span></div>
    <div class="u-name">{{ name }}</div>
    <div class="u-gift"><span class="u-tag">{{ desc }}</span><span class="u-coin">{{ coin }}</span></div>
    <div class="u-elite"></div>
</div>
"""

template_role_monsters = """
<div class="item">
    <div class="item-icon"><img src="{{ icon }}"></div>
    <div class="item-level">{{ level }}</div>
    <div class="item-name">{{ name }}</div>
</div>
"""

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Microsoft Edge\";v=\"114\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "Referer": "https://www.jx3mm.com/jx3fun/jevent/jcitem.html"
}