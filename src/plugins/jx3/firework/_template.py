template_firework_head = """
<tr>
    <th class="short-column">服务器</th>
    <th class="short-column">发送方</th>
    <th class="short-column">接收方</th>
    <th class="short-column">地图</th>
    <th class="short-column">烟花</th>
    <th class="short-column">时间</th>
</tr>"""

template_firework = """
<tr>
    <td class="short-column"><span class="server-tag">{{ server }}</span></td>
    <td class="short-column">{{ sender }}</span></td>
    <td class="short-column">{{ receiver }}</td>
    <td class="short-column">{{ map_name }}</td>
    <td class="short-column">{{ firework }}</td>
    <td class="short-column">{{ time }}</td>
</tr>"""