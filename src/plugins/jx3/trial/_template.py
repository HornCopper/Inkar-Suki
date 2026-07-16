SLRANK_TABLE_HEAD = """
<th class="short-column">排名</th>
<th class="short-column">服务器</th>
<th class="short-column">角色名</th>
<th class="short-column">层数</th>
<th class="short-column">通关评分</th>
<th class="short-column">装备分数</th>
"""

SLRANK_TABLE_BODY = """
<tr>
    <td class="short-column">{{ rank }}</td>
    <td class="short-column">{{ server }}</td>
    <td class="short-column">{{ role_name }}</td>
    <td class="short-column">{{ level }}</td>
    <td class="short-column">{{ grade }}</td>
    <td class="short-column">{{ score }}</td>
</tr>
"""
