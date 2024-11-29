table_head = """
<tr>
    <th class="short-column">心法</th>
    <th class="short-column">增强类食品</th>
    <th class="short-column">辅助类食品</th>
    <th class="short-column">增强类药品</th>
    <th class="short-column">辅助类药品</th>
</tr>"""

template_table = """
<tr>
    <td class="short-column"><img src="{{ image }}" width="50px" height="50px"></td>
    {% for value in values %}
    <td class="short-column">{{ value }}</td>
    {% endfor %}
</tr>"""
