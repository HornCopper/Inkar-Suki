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


therapy_panel_template = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
@font-face { font-family: PanelFont; src: url("{{ font }}"); }
body { margin: 0; background: #f5f6fa; font-family: PanelFont, "Microsoft YaHei", sans-serif; color: #333; }
.therapy-panel { width: max-content; min-width: 1366px; background: #fff; display: flex; flex-direction: column; border: 1px solid #ddd; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,.1); overflow: hidden; }
.main-content { display: flex; width: max-content; min-width: 100%; }
.left-panel { width: 410px; flex: 0 0 410px; padding: 24px; box-sizing: border-box; background: #fafafa; border-right: 1px solid #ddd; display: flex; flex-direction: column; gap: 20px; }
.right-panel { flex: 0 0 auto; padding: 24px; box-sizing: border-box; background: #fff; }
.section-title { font-size: 20px; font-weight: bold; color: {{ theme_color }}; margin-bottom: 6px; border-left: 4px solid {{ theme_color }}; padding-left: 8px; }
.card { background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.item { display: flex; justify-content: space-between; gap: 16px; font-size: 18px; border-bottom: 1px solid #f0f0f0; padding-bottom: 4px; }
.item:last-child { border-bottom: none; }
.item span:last-child { text-align: right; color: #2f3a4e; }
.kungfu { display: inline-block; width: 48px; height: 48px; background: url("{{ kungfu_icon }}") no-repeat center/contain; margin-right: 8px; vertical-align: -10px; }
.skills-grid { display: grid; grid-template-columns: repeat(5, {{ skill_card_width }}px); grid-auto-rows: 1fr; gap: 12px; }
.skill-card { width: 100%; min-width: 0; min-height: 138px; height: 100%; padding: 12px; border: 1px solid #eee; border-radius: 8px; background: #fff; box-sizing: border-box; display: flex; flex-direction: column; gap: 8px; }
.skill-head { display: flex; align-items: flex-start; gap: 8px; min-width: 0; }
.skill-icon { width: 38px; height: 38px; border-radius: 6px; background: #eef2f6; overflow: hidden; flex: 0 0 auto; }
.skill-icon img { display: block; width: 100%; height: 100%; object-fit: cover; }
.skill-name { min-width: 0; color: #2b3548; font-size: 16px; line-height: 1.28; font-weight: 800; white-space: nowrap; }
.skill-stats { display: grid; gap: 4px; font-size: 14px; color: #667085; }
.skill-stats div { display: flex; justify-content: space-between; gap: 8px; }
.skill-stats b { color: #2f3a4e; font-weight: 800; }
.bar { height: 8px; margin-top: auto; background: #edf1f5; border-radius: 99px; overflow: hidden; }
.bar div { height: 100%; border-radius: 99px; }
.empty { grid-column: 1 / -1; padding: 36px; text-align: center; color: #667085; font-size: 20px; }
footer { background: #f0f0f0; text-align: center; padding: 15px; font-size: 1.2em; color: #777; }
</style>
</head>
<body>
<div class="therapy-panel">
  <div class="main-content">
    <div class="left-panel">
      <div>
        <div class="section-title">&#22522;&#30784;&#20449;&#24687;</div>
        <div class="card">
          <div class="item"><span>&#35282;&#33394;&#21517;</span><span>{{ role_name }}</span></div>
          <div class="item"><span>&#26381;&#21153;&#22120;</span><span>{{ server_name }}</span></div>
          <div class="item"><span>&#24515;&#27861;</span><span>{{ kungfu_name }}</span></div>
          <div class="item"><span>&#35013;&#20998;</span><span>{{ score }}</span></div>
        </div>
      </div>
      <div>
        <div class="section-title">&#23646;&#24615;</div>
        <div class="card">
          {{ attr_html }}
        </div>
      </div>
    </div>
    <div class="right-panel">
      <div class="section-title">&#25216;&#33021;&#27835;&#30103;</div>
      <div class="skills-grid">{{ skill_rows }}</div>
    </div>
  </div>
  <footer>Inkar Suki: {{ saohua }}</footer>
</div>
</body>
</html>
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
            align-items: center;
            justify-content: space-between;
            gap: 22px;
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

        .report-mark {
            flex: 0 0 auto;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 14px 8px 8px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.64);
            border: 1px solid rgba(120, 174, 190, 0.36);
            box-shadow: 0 12px 24px rgba(65, 92, 122, 0.12);
            color: #41506a;
            font-size: 16px;
            font-weight: 800;
        }

        .report-mark img {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid rgba(205, 245, 235, 0.92);
            box-shadow: 0 5px 14px rgba(85, 131, 156, 0.18);
        }

        .phase-card {
            position: relative;
            margin-top: 22px;
            padding: 20px;
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.86);
            border: 1px solid rgba(120, 134, 156, 0.22);
            box-shadow: 0 18px 40px rgba(31, 42, 61, 0.08);
            overflow: hidden;
        }

        .phase-card > :not(.phase-watermark) {
            position: relative;
            z-index: 1;
        }

        .phase-watermark {
            position: absolute;
            top: 18px;
            right: 22px;
            width: 156px;
            height: 156px;
            object-fit: cover;
            border-radius: 42px;
            opacity: 0.10;
            filter: saturate(0.9) blur(0.2px);
            transform: rotate(7deg);
            pointer-events: none;
            z-index: 0;
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
            font-size: 14px;
            text-align: center;
            white-space: nowrap;
        }

        td {
            padding: 7px 5px;
            border-top: 1px solid #edf0f5;
            font-size: 14px;
            vertical-align: middle;
            text-align: center;
            line-height: 1.25;
        }

        .num {
            text-align: center;
            white-space: nowrap;
            font-variant-numeric: tabular-nums;
        }

        .contribution-bar {
            position: relative;
            overflow: hidden;
            background: transparent;
        }

        .contribution-bar::before {
            content: "";
            position: absolute;
            left: 6px;
            top: 50%;
            width: var(--bar, 0%);
            max-width: calc(100% - 12px);
            height: 62%;
            border-radius: 10px;
            transform: translateY(-50%);
            background: linear-gradient(90deg, rgba(86, 124, 170, 0.32), rgba(151, 174, 203, 0.22));
            box-shadow: 0 4px 12px rgba(86, 124, 170, 0.12);
        }

        .contribution-bar span {
            position: relative;
            z-index: 1;
            font-weight: 800;
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
            grid-template-columns: minmax(0, 1.16fr) minmax(0, 0.92fr) minmax(0, 0.92fr);
            gap: 12px;
            align-items: start;
        }

        .triple-col table {
            table-layout: fixed;
        }

        .triple-col th,
        .triple-col td {
            padding-left: 4px;
            padding-right: 4px;
            font-size: 13px;
        }

        .triple-col .rank {
            width: 28px;
        }

        .triple-col .role-cell {
            gap: 5px;
        }

        .triple-col .role-cell img {
            width: 20px;
            height: 20px;
        }

        .triple-col .role-cell > div {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .contribution-summary-table th:first-child,
        .contribution-summary-table td:first-child,
        .contribution-side-table th:first-child,
        .contribution-side-table td:first-child {
            width: 28px;
        }

        .contribution-summary-table th:nth-child(2),
        .contribution-summary-table td:nth-child(2) {
            width: 170px;
            text-align: left;
        }

        .contribution-summary-table th:nth-child(n + 3),
        .contribution-summary-table td:nth-child(n + 3) {
            width: 82px;
        }

        .contribution-side-table th:nth-child(2),
        .contribution-side-table td:nth-child(2) {
            width: 190px;
            text-align: left;
        }

        .contribution-side-table th:nth-child(3),
        .contribution-side-table td:nth-child(3) {
            width: 86px;
        }

        .detail-row {
            display: grid;
            grid-template-columns: minmax(0, 1fr) 430px;
            gap: 14px;
            align-items: start;
        }

        .buff-detail-table {
            table-layout: fixed;
        }

        .buff-detail-table th:first-child,
        .buff-detail-table td:first-child {
            width: 30px;
        }

        .buff-detail-table th:nth-child(2),
        .buff-detail-table td:nth-child(2) {
            width: 145px;
            text-align: left;
        }

        .buff-detail-table th:nth-child(3),
        .buff-detail-table td:nth-child(3) {
            width: 120px;
        }

        .buff-detail-table th:nth-child(4),
        .buff-detail-table td:nth-child(4) {
            width: 62px;
        }

        .buff-detail-table th:nth-child(5),
        .buff-detail-table td:nth-child(5) {
            width: 84px;
        }

        .buff-detail-table th:nth-child(6),
        .buff-detail-table td:nth-child(6) {
            width: 88px;
        }

        .buff-detail-table .role-cell > div {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .wave-stack {
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

        .wave-card {
            padding: 10px 8px;
            border-radius: 14px;
            background: #f4f7fb;
            text-align: center;
        }

        .wave-index {
            font-size: 14px;
            color: #6b7280;
            font-weight: 800;
        }

        .wave-value {
            margin-top: 5px;
            font-size: 15px;
            font-weight: 800;
            color: #2d3a53;
            white-space: nowrap;
        }

        .wave-subvalue {
            margin-top: 2px;
            font-size: 13px;
            font-weight: 700;
            color: #6b7280;
            white-space: nowrap;
        }

        .pie-panel {
            display: grid;
            gap: 10px;
        }

        .pie-card {
            padding: 12px;
            border-radius: 18px;
            background: linear-gradient(135deg, #f6f9fd, #f1f5fa);
            border: 1px solid #e8edf4;
        }

        .pie-title {
            margin-bottom: 8px;
            font-size: 16px;
            font-weight: 800;
            color: #2f3a50;
        }

        .pie-body {
            display: grid;
        }

        .pie-chart {
            position: relative;
            width: 406px;
            max-width: 100%;
            height: 265px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: visible;
        }

        .rose-chart {
            width: 406px;
            height: 265px;
            max-width: 100%;
            overflow: visible;
            filter: drop-shadow(0 10px 16px rgba(45, 58, 83, 0.14));
        }

        .rose-backdrop {
            fill: #eef3f8;
            stroke: rgba(45, 58, 83, 0.08);
            stroke-width: 1;
        }

        .rose-slice {
            stroke: rgba(247, 250, 253, 0.96);
            stroke-width: 2.5;
        }

        .rose-core {
            fill: #f8fbfe;
            stroke: rgba(45, 58, 83, 0.08);
            stroke-width: 1;
        }

        .rose-guide-shadow {
            fill: none;
            stroke: rgba(255, 255, 255, 0.78);
            stroke-width: 4;
            stroke-linecap: round;
        }

        .rose-guide-line {
            fill: none;
            stroke: #5d6d82;
            stroke-width: 1.35;
            stroke-linecap: round;
            stroke-opacity: 0.62;
        }

        .rose-chart marker path {
            fill: #5d6d82;
            opacity: 0.68;
        }

        .rose-entity-label {
            position: absolute;
            z-index: 2;
            max-width: 128px;
            height: 26px;
            padding: 0 6px;
            border-radius: 999px;
            display: flex;
            align-items: center;
            gap: 3px;
            transform: translate(-50%, -50%);
            background: var(--label-color, rgba(33, 43, 61, 0.72));
            background: linear-gradient(135deg, color-mix(in srgb, var(--label-color, #334158) 76%, #1f2a3d), var(--label-color, #334158));
            border: 1px solid rgba(255, 255, 255, 0.52);
            box-shadow: 0 4px 10px rgba(45, 58, 83, 0.18);
            color: #ffffff;
            line-height: 1;
            backdrop-filter: blur(2px);
        }

        .rose-entity-label img {
            width: 15px;
            height: 15px;
            border-radius: 50%;
            flex: 0 0 auto;
        }

        .rose-label-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            flex: 0 0 auto;
        }

        .rose-entity-name {
            min-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-size: 11px;
            font-weight: 900;
        }

        .rose-entity-label b {
            margin-left: auto;
            font-size: 11px;
            font-weight: 900;
        }

        .pie-name {
            min-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
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
                <div class="title-main">鲁念雪-雷元归枢-JCL贡献统计</div>
                <div class="title-sub">减伤、治疗、化解按阶段加权统计；r = {{ decay_rate }}</div>
            </div>
            <div class="report-mark">
                <img src="{{ lnx_mark }}" alt="LNX">
                <span>LNX 分析</span>
            </div>
        </div>

        {{ sections }}

        <footer>Inkar-Suki：{{ saohua }}</footer>
    </div>
</body>
</html>
"""
