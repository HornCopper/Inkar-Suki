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

slrank_table_head = """
<tr>
    <th class="short-column">排名</th>
    <th class="short-column">服务器</th>
    <th class="short-column">角色名</th>
    <th class="short-column">层数</th>
    <th class="short-column">通关评分</th>
    <th class="short-column">装备分数</th>
</tr>"""

slrank_template_body = """
<tr>
    <td class="short-column">{{ rank }}</td>
    <td class="short-column">{{ server }}</td>
    <td class="short-column">{{ role_name }}</td>
    <td class="short-column">{{ level }}</td>
    <td class="short-column">{{ grade }}</td>
    <td class="short-column">{{ score }}</td>
</tr>
"""

cqcrank_table_head = """
<tr>
    <th class="short-column">排名</th>
    <th class="short-column">心法</th>
    <th class="short-column">角色名</th>
    <th class="short-column">服务器</th>
    <th class="short-column">总伤/总疗</th>
    <th class="short-column">秒伤/秒疗</th>
</tr>"""

cqcrank_template_body = """
<tr>
    <td class="short-column">{{ rank }}</td>
    <td class="short-column"><img src="{{ kungfu_icon }}" alt="icon" width="30" height="30"></td>
    <td class="short-column">{{ name }}</td>
    <td class="short-column">{{ server }}</td>
    <td class="short-column">{{ value }}</td>
    <td class="short-column">{{ value_per_second }}</td>
</tr>
"""

teamrank_anyone_template = """
<div class="player">
    <div class="class-icon">
        <img src="{{ kungfu_icon }}"
            style="width: 25px;height: 25px;">
    </div>
    <span class="player-name">{{ name }}</span>
</div>
"""

teamrank_team_template = """
<div class="content">
    <div class="logo-section">
        <div class="logo">
            <img src="{{ team_icon }}">
            <div style="font-size: 24px; color: #ffcc00; font-weight: bold;">{{ team_name }}</div>
        </div>
        <div class="logo-text">{{ team_name }}</div>
        <div>{{ server }}</div>
        <div style="text-align: center;">通关时间：<br>{{ finish_time }}</div>
        <div>用时：{{ time_cost }}</div>
    </div>

    <div class="rankings">
        {{ players }}
    </div>
</div>
"""