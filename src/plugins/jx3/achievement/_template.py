table_head = """
<tr>
    <th class="icon-column">图标</th>
    <th class="name-column">名称</th>
    <th class="type-column">类型</th>
    <th class="description-column">描述</th>
    <th class="qualification-column">资历</th>
    <th class="status-column">状态</th>
</tr>"""

template_body = """
<tr>
    <td class="icon-column"><img src="{{ image }}" alt="icon" width="30"></td>
    <td class="name-column">{{ name }}</td>
    <td class="type-column">{{ type }}</td>
    <td class="description-column">{{ desc }}</td>
    <td class="qualification-column">{{ value }}</td>
    <td class="status-column"><span class="{{ status }}">{{ flag }}</span></td>
</tr>
"""