template_calculator = """
<div class="skill">
    <div class="skill-header">
        <strong>{{ skill }} - {{ count }}</strong><span>{{ percent }} - {{ value }}</span>
    </div>
    <div class="progress-bar-container">
        <div class="progress-bar" style="width: {{ display }};"></div>
    </div>
</div>"""

template_calculator_v2 = """
<div class="skill-row">
    <div class="skill-header">
        <span>{{ skill }} - {{ count }}</span>
        <span>总伤害 {{ value }} ｜ 期望会心 {{ critical }} ｜ 占比 {{ percent }}</span>
    </div>
    <div class="bar-container">
        <div class="bar" style="width: {{ display }};"></div>
    </div>
</div>
"""

template_attr = """
<div class="attribute">
    <strong>{{ name }}</strong><br><span>{{ value }}<br><span><strong>收益：</strong>{{ income }}</span></span>
</div>"""

bla_template_body = """
<div class="skill">
    <img src="{{ icon }}" width="50px" height="50px">
    <div class="skill-content">
        <div class="skill-header">
            <strong>{{ name }}</strong>
        </div>
        <div class="progress-bar-container" style="width: 700px">
            <div class="progress-bar" style="width: {{ display }}%; background-color: {{ color }};"></div>
        </div>
    </div>
    <div class="extra-col">
        <span class="dps-num">{{ rdps }}</span>
    </div>

    <div class="extra-col">
        <span class="dps-num">{{ percent }}</span>
    </div>
</div>"""

fal_table_head = """
<tr>
    <th class="short-column">时间</th>
    <th class="short-column">攻击者</th>
    <th class="short-column">被攻击者</th>
    <th class="short-column">技能ID</th>
</tr>"""

fal_template_body = """
<tr>
    <td class="short-column">{{ time }}</td>
    <td class="short-column">{{ releaser }}</td>
    <td class="short-column">{{ target }}</td>
    <td class="short-column">{{ skill }}</td>
</tr>
"""

yxc_table_head = """
<tr>
    <th class="short-column">心法</th>
    <th class="short-column">角色名</th>
    <th class="short-column">有效治疗</th>
</tr>"""

yxc_template_body_main = """
<tr class="main-row">
    <td>
        <img src="{{ icon }}" width="50" height="50">
    </td>
    <td>{{ name }}</td>
    <td>{{ value }}</td>
</tr>
"""

yxc_template_body_sub = """
<tr class="sub-row">
    <td class="sub-skill">
        {{ name }}
    </td>
    <td class="sub-value">
        {{ count }}
    </td>
    <td class="sub-value">
        {{ value }}({{ percent }})
    </td>
</tr>
"""