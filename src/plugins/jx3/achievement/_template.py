table_head = """
<tr>
    <th>图标</th>
    <th>名称</th>
    <th>类型</th>
    <th>描述</th>
    <th>资历</th>
    <th>进度</th>
    <th>状态</th>
</tr>"""

template_body = """
<tr>
    <td><img src="{{ image }}" alt="icon" width="30"></td>
    <td>{{ name }}</td>
    <td>{{ type }}</td>
    <td>{{ desc }}</td>
    <td>{{ value }}</td>
    <td style="width: 250px">
        <div class="progress-bar">
            <div class="progress" style="width: {{ progress }}%;"></div>
            <span class="progress-text">{{ current }}/{{ target }}</span>
        </div>
    </td>
    <td><span class="{{ status }}">{{ flag }}</span></td>
</tr>
"""