table_head = """
<tr>
    <th class="short-column">排行</th>
    <th class="short-column">头像</th>
    <th class="short-column">昵称</th>
    <th class="short-column">角色</th>
    <th class="short-column">资历</th>
</tr>"""

template_body = """
<tr>
    <td class="short-column">{{ rank }}</td>
    <td class="short-column"><img src="{{ avatar }}" alt="icon" width="30" height="30"></td>
    <td class="short-column">{{ nickname }}</td>
    <td class="short-column">{{ role }}</td>
    <td class="short-column">{{ value }}</td>
</tr>
"""