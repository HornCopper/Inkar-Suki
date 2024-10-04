template_dilu = """
<tr>
    <td class="short-column">{{ server }}</td>
    <td class="short-column">刷新：{{ flush }}<br>捕获：{{ captured }}<br>竞拍：{{ sell }}</td>
    <td class="short-column">{{ map }}</td>
    <td class="short-column">{{ capturer }}<br>{{ ci }}<span style="color: grey;font-size:small">{{ cc }}</span></td>
    <td class="short-column">{{ auctioner }}<br>{{ bi }}<span style="color: grey;font-size:small">{{ bc }}</span></td>
    <td class="short-column">{{ price }}</td>
</tr>
"""

bad = "<img src=\"https://jx3wbl.xoyocdn.com/img/icon-camp-bad.07567e9f.png\">"
good = "<img src=\"https://jx3wbl.xoyocdn.com/img/icon-camp-good.0db444fe.png\">"

table_dilu_head = """
<tr>
    <th class="short-column">区服</th>
    <th class="short-column">时间</th>
    <th class="short-column">地图</th>
    <th class="short-column">捕捉</th>
    <th class="short-column">拍卖</th>
    <th class="short-column">金额</th>
</tr>"""