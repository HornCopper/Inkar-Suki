zlrank_table_head = """
<tr>
    <th class="short-column">排行</th>
    <th class="short-column">头像</th>
    <th class="short-column">昵称</th>
    <th class="short-column">角色</th>
    <th class="short-column">资历</th>
</tr>"""

zlrank_template_body = """
<tr>
    <td class="short-column">{{ rank }}</td>
    <td class="short-column"><img src="{{ avatar }}" alt="icon" width="30" height="30"></td>
    <td class="short-column">{{ nickname }}</td>
    <td class="short-column">{{ role }}</td>
    <td class="short-column">{{ value }}</td>
</tr>
"""

rank_table_head = """
<tr>
    <th class="short-column">排名</th>
    <th class="short-column">心法</th>
    <th class="short-column">角色名</th>
    <th class="short-column">服务器</th>
    <th class="short-column">数值</th>
</tr>"""

rank_template_body = """
<tr>
    <td class="short-column">{{ rank }}</td>
    <td class="short-column"><img src="{{ kungfu_icon }}" alt="icon" width="30" height="30"></td>
    <td class="short-column">{{ name }}</td>
    <td class="short-column">{{ server }}</td>
    <td class="short-column">{{ value }}</td>
</tr>
"""