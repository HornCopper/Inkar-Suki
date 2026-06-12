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

yxc_table = f"""
<table class="rank-table">
    <thead>
        {yxc_table_head}
    </thead>

    <tbody>
        {{{{ tables }}}}
    </tbody>
</table>
"""

hps_detail_template_body_main = """
<tr class="main-row">
    <td>
        <img src="{{ icon }}" width="50" height="50">
    </td>
    <td>{{ name }}</td>
    <td>{{ value }}</td>
</tr>
"""

hps_detail_template_body_sub = """
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

rod_table_head = """
<tr>
    <th class="short-column">重伤时间</th>
    <th class="short-column">玩家名</th>
    <th class="short-column">最后5次有效伤害</th>
    <th class="short-column">备注</th>
</tr>"""

rod_template_body = """
<tr>
    <td class="short-column">{{ time }}</td>
    <td class="short-column"><img src="{{ icon }}" width="50px" height="50px">{{ name }}</td>
    <td class="short-column">{{ skills }}</td>
    <td class="short-column">{{ remark }}</td>
</tr>
"""

rod_css = """
.item-table td:nth-child(3)
{
    text-align: left;
    white-space: normal;
    line-height: 1.5;
}

.item-table td:nth-child(2)
{
    display: flex;
    align-items: center;
    gap: 8px;
}

.item-table td:nth-child(1),
.item-table td:nth-child(2)
{
    vertical-align: top;
}
"""

asn_qte_table_head = """
<tr>
    <th class="short-column">角色名</th>
    <th class="short-column">完美击破</th>
    <th class="short-column">单层击破</th>
</tr>"""

asn_qte_table = f"""
<table class="rank-table">
    <thead>
        {asn_qte_table_head}
    </thead>

    <tbody>
        {{{{ tables }}}}
    </tbody>
</table>
"""

asn_qte_template_body_main = """
<tr class="main-row">
    <td>
        {{ name }}
    </td>
    <td>{{ good }}</td>
    <td>{{ bad }}</td>
</tr>
"""

lgz_table_head = """
<tr>
    <th class="short-column">状态</th>
    <th class="short-column">心法</th>
    <th class="short-column">角色名</th>
    <th class="short-column">时间</th>
</tr>"""

lgz_table = f"""
<table class="rank-table">
    <thead>
        {lgz_table_head}
    </thead>

    <tbody>
        {{{{ tables }}}}
    </tbody>
</table>
"""

lgz_detail_template_body_main = """
<tr class="main-row">
    <td>
        <div style="display: flex; align-items: center; justify-content: center; gap: 6px;">
            <img src="{{ status_icon }}" width="25" height="25">
            <span>{{ status }}</span>
        </div>
    </td>
    <td>
        <img src="{{ icon }}" width="50" height="50">
    </td>
    <td>{{ name }}</td>
    <td>{{ time }}</td>
</tr>
"""

lgz_detail_template_body_sub = """
<tr class="sub-row">
    <td class="sub-value">
        <div style="display: flex; align-items: center; justify-content: center; gap: 6px;">
            <img src="{{ status_icon }}" width="25" height="25">
            <span>{{ status }}</span>
        </div>
    </td>
    <td>
        <img src="{{ icon }}" width="25" height="25">
    </td>
    <td class="sub-value">
        {{ name }}
    </td>
    <td class="sub-value">
        {{ time }}
    </td>
</tr>
"""

lnx_template_body = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <style>
        @font-face {
            font-family: Harmony;
            src: url("{{ font }}");
        }

        body {
            margin: 0;
            background: #edf1f5;
            font-family: Harmony, "Microsoft YaHei", sans-serif;
            color: #253044;
        }

        .lnx-report {
            width: 1600px;
            padding: 30px;
            background:
                radial-gradient(circle at 10% 0%, rgba(86, 138, 198, 0.24), transparent 28%),
                linear-gradient(135deg, #f7fbff 0%, #eef3f8 48%, #f8efe4 100%);
            box-sizing: border-box;
        }

        .report-title {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            margin-bottom: 22px;
        }

        .title-main {
            font-size: 40px;
            font-weight: 800;
            letter-spacing: 2px;
            color: #1f2a3d;
        }

        .title-sub {
            margin-top: 8px;
            font-size: 18px;
            color: #6b7280;
        }

        .badge {
            padding: 10px 16px;
            border-radius: 999px;
            background: rgba(31, 42, 61, 0.08);
            font-size: 16px;
            color: #41506a;
        }

        .phase-card {
            margin-top: 22px;
            padding: 20px;
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.86);
            border: 1px solid rgba(120, 134, 156, 0.22);
            box-shadow: 0 18px 40px rgba(31, 42, 61, 0.08);
        }

        .phase-header {
            display: flex;
            justify-content: space-between;
            gap: 14px;
            align-items: center;
            margin-bottom: 14px;
        }

        .phase-name {
            font-size: 28px;
            font-weight: 800;
            color: #26324a;
        }

        .phase-meta {
            font-size: 16px;
            color: #6c7890;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-bottom: 22px;
        }

        .metric {
            padding: 16px 18px;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(44, 79, 122, 0.08), rgba(219, 137, 69, 0.08));
        }

        .metric-label {
            font-size: 16px;
            color: #667085;
            margin-bottom: 8px;
        }

        .metric-value {
            font-size: 27px;
            font-weight: 800;
            color: #1f2a3d;
        }

        .section-title {
            margin: 18px 0 8px;
            font-size: 20px;
            font-weight: 800;
            color: #2f3a50;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            overflow: hidden;
            border-radius: 16px;
            background: #ffffff;
        }

        th {
            padding: 7px 5px;
            background: #e9eef5;
            color: #43516a;
            font-size: 13px;
            text-align: center;
            white-space: nowrap;
        }

        td {
            padding: 7px 5px;
            border-top: 1px solid #edf0f5;
            font-size: 13px;
            vertical-align: middle;
            text-align: center;
            line-height: 1.25;
        }

        .num {
            text-align: center;
            white-space: nowrap;
            font-variant-numeric: tabular-nums;
        }

        .rank {
            width: 30px;
            color: #7a8496;
            text-align: center;
        }

        .role-cell {
            display: flex;
            align-items: center;
            gap: 6px;
            min-width: 0;
            text-align: left;
        }

        .role-cell > div {
            min-width: 0;
            line-height: 1.25;
            overflow-wrap: anywhere;
        }

        .role-cell img {
            width: 22px;
            height: 22px;
            border-radius: 6px;
        }

        .muted {
            color: #7b8494;
            font-size: 13px;
        }

        .two-col {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
        }

        .triple-col {
            display: grid;
            grid-template-columns: minmax(0, 1.12fr) minmax(0, 0.88fr) minmax(0, 0.88fr);
            gap: 12px;
            align-items: start;
        }

        .wave-matrix {
            display: grid;
            grid-template-columns: 86px 1fr;
            gap: 8px;
            align-items: stretch;
        }

        .wave-grid {
            display: grid;
            grid-template-columns: repeat(11, 1fr);
            gap: 8px;
        }

        .wave-label-pill {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px 8px;
            border-radius: 14px;
            background: #e9eef5;
            color: #2f3a50;
            font-size: 15px;
            font-weight: 800;
            text-align: center;
        }

        .wave-pill {
            padding: 10px 8px;
            border-radius: 14px;
            background: #f4f7fb;
            text-align: center;
        }

        .wave-index {
            font-size: 14px;
            color: #6b7280;
        }

        .wave-value {
            margin-top: 4px;
            font-size: 15px;
            font-weight: 800;
            color: #2d3a53;
        }

        .wave-subvalue {
            margin-top: 2px;
            font-size: 13px;
            font-weight: 700;
            color: #6b7280;
        }

        footer {
            margin-top: 24px;
            padding: 16px;
            border-radius: 16px;
            text-align: center;
            background: rgba(31, 42, 61, 0.08);
            color: #6b7280;
            font-size: 18px;
        }
    </style>
</head>
<body>
    <div class="lnx-report">
        <div class="report-title">
            <div>
                <div class="title-main">鲁念雪 JCL 贡献统计</div>
                <div class="title-sub">减伤、治疗、化解按阶段加权统计；r = {{ decay_rate }}</div>
            </div>
            <div class="badge">LNX 分析</div>
        </div>

        {{ sections }}

        <footer>Inkar-Suki：{{ saohua }}</footer>
    </div>
</body>
</html>
"""
