table_chutian_head = """
<tr>
    <th class="short-column">时间</th>
    <th class="short-column">地点</th>
    <th class="short-column">阶段</th>
    <th class="short-column">详情</th>
</tr>"""

template_chutian = """
<tr>
    <td class="short-column">{{ time }}</td>
    <td class="short-column">{{ site }}</span></td>
    <td class="short-column"><img src="{{ icon }}" style="vertical-align: middle;">{{ section }}</td>
    <td class="short-column">{{ desc }}</td>
</tr>"""

template_zhue = """
<tr>
    <td class="short-column">{{ time }}</td>
    <td class="short-column">{{ map }}</td>
    <td class="short-column">{{ relate }}</td>
</tr>"""

table_zhue_head = """
<tr>
    <th class="short-column">时间</th>
    <th class="short-column">地图</th>
    <th class="short-column">参考</th>
</tr>"""