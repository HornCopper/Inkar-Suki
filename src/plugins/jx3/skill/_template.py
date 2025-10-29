table_head_talent = """
<tr>
    <th class="short-column">图标</th>
    <th class="short-column">名称</th>
    <th class="short-column">位置</th>
    <th class="short-column">描述</th>
</tr>"""

template_body_talent = """
<tr>
    <td class="short-column"><img src="{{ icon }}" alt="icon" width="30" height="30"></td>
    <td class="short-column">{{ name }}</td>
    <td class="short-column">{{ location }}</td>
    <td class="short-column">{{ desc }}</td>
</tr>
"""

table_head_skill = """
<tr>
    <th class="short-column">图标</th>
    <th class="short-column">ID</th>
    <th class="short-column">名称</th>
    <th class="short-column">备注</th>
    <th class="short-column">描述</th>
</tr>"""

template_body_skill = """
<tr>
    <td class="short-column"><img src="{{ icon }}" alt="icon" width="30" height="30"></td>
    <td class="short-column">{{ skill_id }}</td>
    <td class="short-column">{{ name }}</td>
    <td class="short-column">{{ remark }}</td>
    <td class="short-column">{{ desc }}</td>
</tr>
"""