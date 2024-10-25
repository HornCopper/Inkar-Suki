table_head = """
<tr>
    <th class="short-column">排行</th>
    <th class="short-column">头像</th>
    <th class="short-column">昵称</th>
    <th class="short-column">QQ号</th>
    <th class="short-column">发言</th>
</tr>"""

template_body = """
<tr>
    <td class="short-column">{{ rank }}</td>
    <td class="short-column"><img src="{{ avatar }}" alt="icon" width="30" height="30"></td>
    <td class="short-column">{{ nickname }}</td>
    <td class="short-column">{{ user_id }}</td>
    <td class="short-column">{{ count }}</td>
</tr>
"""