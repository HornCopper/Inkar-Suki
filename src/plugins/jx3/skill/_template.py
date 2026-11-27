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

skill_table_css = """
.item-table td.skill-description {
    max-width: 900px;
    white-space: normal;
    overflow-wrap: anywhere;
    text-align: left;
}
.skill-description .skill-talent-effect {
    color: #2fa8a7;
}
.skill-description .noun-reference {
    text-decoration: underline;
    text-decoration-thickness: 1px;
    text-underline-offset: 3px;
}
.skill-description .skill-talent-icon {
    width: 24px;
    height: 24px;
    object-fit: contain;
    vertical-align: -4px;
}
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
    <td class="skill-description">{{ desc }}</td>
</tr>
"""
