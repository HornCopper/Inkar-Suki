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
.skill-card { width: 100%; min-width: 0; min-height: 158px; height: 100%; padding: 12px; border: 1px solid #eee; border-radius: 8px; background: #fff; box-sizing: border-box; display: flex; flex-direction: column; gap: 8px; }
.skill-head { display: flex; align-items: flex-start; gap: 8px; min-width: 0; }
.skill-icon { width: 38px; height: 38px; border-radius: 6px; background: #eef2f6; overflow: hidden; flex: 0 0 auto; }
.skill-icon img { display: block; width: 100%; height: 100%; object-fit: cover; }
.skill-name { min-width: 0; color: #2b3548; font-size: 16px; line-height: 1.28; font-weight: 800; white-space: nowrap; }
.skill-coefficient { text-align: center; color: #667085; font-size: 14px; line-height: 1.2; font-weight: 700; }
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
equipment_rating_help_template = r"""

<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<script>
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]]
  },
  svg: { fontCache: "global" }
};
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
<style>
* { box-sizing: border-box; }
body {
  margin: 0;
  width: 980px;
  background: #f3f6f9;
  color: #202630;
  font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
}
.guide {
  width: 980px;
  padding: 36px;
  background: #f3f6f9;
}
.hero {
  padding: 30px 34px;
  border-radius: 8px;
  background: #243149;
  color: #fff;
}
.eyebrow {
  font-size: 18px;
  line-height: 1.25;
  color: #b9c7dc;
  font-weight: 800;
}
.title {
  margin-top: 8px;
  font-size: 34px;
  line-height: 1.2;
  font-weight: 900;
}
.subtitle {
  margin-top: 12px;
  max-width: 820px;
  font-size: 18px;
  line-height: 1.65;
  color: #d9e2ee;
}
.section {
  margin-top: 18px;
  padding: 24px 26px;
  border: 1px solid #e0e5ed;
  border-radius: 8px;
  background: #fff;
}
.section-title {
  margin-bottom: 14px;
  font-size: 24px;
  line-height: 1.25;
  font-weight: 900;
  color: #18202c;
}
.steps {
  display: grid;
  gap: 11px;
}
.step {
  display: grid;
  grid-template-columns: 34px 1fr;
  gap: 12px;
  align-items: start;
  font-size: 18px;
  line-height: 1.62;
  color: #333b4d;
}
.num {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2f6bff;
  color: #fff;
  font-size: 16px;
  font-weight: 900;
}
.command {
  display: inline-block;
  padding: 2px 7px;
  border-radius: 5px;
  background: #edf2ff;
  color: #2354d6;
  font-weight: 900;
}
.examples {
  margin-top: 9px;
  display: grid;
  gap: 7px;
  font-size: 16px;
  line-height: 1.45;
  color: #5a6473;
}
.formula-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.formula-block {
  min-width: 0;
  padding: 18px;
  border: 1px solid #dde5ef;
  border-radius: 8px;
  background: #f8fafc;
}
.formula-title {
  font-size: 18px;
  font-weight: 900;
  color: #253044;
}
.formula {
  margin: 12px 0;
  min-height: 68px;
  overflow: hidden;
  color: #141a24;
}
.formula-note {
  font-size: 15px;
  line-height: 1.55;
  color: #5b6574;
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
}
.chip {
  padding: 8px 12px;
  border-radius: 999px;
  background: #f5f7fb;
  border: 1px solid #dfe5ee;
  color: #303848;
  font-size: 16px;
  font-weight: 900;
}
.notice {
  padding: 18px 20px;
  border-left: 5px solid #ff8a00;
  background: #fff7e8;
  color: #563813;
  font-size: 18px;
  line-height: 1.65;
  font-weight: 800;
}
.footer {
  margin-top: 18px;
  color: #7a8392;
  font-size: 14px;
  text-align: right;
}
</style>
</head>
<body>
<div class="guide">
  <div class="hero">
    <div class="eyebrow">装备评级 help</div>
    <div class="title">评级给出的评分只能够衡量当前配装距离毕业的程度</div>
    <div class="subtitle">输出与防御心法会在同一条评级 JCL、同一套默认评级增益下比较当前部位、空槽样本和候选装备；奶妈心法使用承压模型，以目标破产概率下的最大每秒承伤作为评分指标。</div>
  </div>

  <div class="section">
    <div class="section-title">使用步骤</div>
    <div class="steps">
      <div class="step"><div class="num">1</div><div>先提交属性：<span class="command">提交属性 &lt;服务器&gt; &lt;角色名&gt; &lt;心法&gt; &lt;茗伊装备导出码&gt;</span></div></div>
      <div class="step"><div class="num">2</div><div>再执行评级：<span class="command">装备评级 &lt;服务器&gt; &lt;角色名/ID&gt; [&lt;心法&gt;] [评级列表]</span> 或 <span class="command">装备评级 &lt;魔盒配装ID&gt; [评级列表]</span>
        <div class="examples">
          <div>角色名：<span class="command">装备评级 剑胆琴心 倦收天</span></div>
          <div>评级列表：<span class="command">装备评级 剑胆琴心 倦收天 评级列表</span></div>
          <div>魔盒配装：<span class="command">装备评级 123456 评级列表</span></div>
        </div>
      </div></div>
      <div class="step"><div class="num">3</div><div>查看支持心法：<span class="command">装备评级支持</span> 或 <span class="command">装备评级支持 &lt;心法名&gt;</span></div></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">评级依据</div>
    <div class="steps">
      <div class="step"><div class="num">A</div><div>每个部位会计算三类样本：当前装备、去掉该部位后的空槽样本、同部位候选装备。</div></div>
      <div class="step"><div class="num">B</div><div>所有样本使用同一条评级 JCL 和默认评级增益，避免把循环和增益差异混进装备评分。</div></div>
      <div class="step"><div class="num">C</div><div>“最优候选”来自当前候选池中评级指标最高的该部位装备；输出与防御心法看修正 DPS，奶妈心法看承压能力。</div></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">奶妈承压评级依据</div>
    <div class="steps">
      <div class="step"><div class="num">H</div><div>直接使用装备面板的治疗量、会心、会效和加速。不考虑装备特效，心法特性，纯静态面板计算。</div></div>
      <div class="step"><div class="num">T</div><div>高压窗口 \(T=10\) 秒，血量上限 \(U=3200000\)，目标破产概率 \(q=5\%\)。伤害从 \(t=0\) 开始，到 \(t=10\) 结束，共结算 11 次。</div></div>
      <div class="step"><div class="num">G</div><div>治疗间隔 \(\Delta=1.5/(1+a_{\mathrm{eff}}/210078)\)，其中 \(a_{\mathrm{eff}}=\min(a,42057)\)。每个治疗时间点按 3 次独立治疗计算，会心按面板概率分布。</div></div>
    </div>
    <div class="formula-grid" style="margin-top: 16px;">
      <div class="formula-block">
        <div class="formula-title">血量递推</div>
        <div class="formula">\[
R_0 = U - d
\]
\[
R_{i+1} = \min(U, R_i + H_i) - d
\]</div>
        <div class="formula-note">若任意结算后 \(R_i < 0\)，则视为破产。治疗 \(H_i\) 统计区间 \([i,i+1)\) 内发生的所有治疗，并先受血量上限截断。</div>
      </div>
      <div class="formula-block">
        <div class="formula-title">承压能力</div>
        <div class="formula">\[
\tau = \inf\{i : R_i < 0\}
\]
\[
d^* = \max\{d: \Pr(\tau \le T) \le q\}
\]</div>
        <div class="formula-note">\(\tau\) 是首次破产的整数伤害结算点。承压能力 \(d^*\)为每秒承伤。单件评分固定当前推荐的小药、熔锭和阵眼配置后，比较当前、空槽和候选装备的 \(d^*\)。</div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">计算公式</div>
    <div class="formula-grid">
      <div class="formula-block">
        <div class="formula-title">单件评分</div>
        <div class="formula">\[
S_i = \operatorname{clip}_{0}^{100}\left(
\frac{D_{\mathrm{current}} - D_{\mathrm{empty}, i}}
{D_{\mathrm{best}, i} - D_{\mathrm{empty}, i}} \times 100
\right)
\]</div>
        <div class="formula-note">空槽 DPS 是该部位被移除后的基线；分数越高，代表该部位越接近当前候选池中的最优替换。</div>
      </div>
      <div class="formula-block">
        <div class="formula-title">配装总评</div>
        <div class="formula">\[
S_{\mathrm{total}} =
\frac{\sum_i S_i W_i}{\sum_i W_i}
\]</div>
        <div class="formula-note">\(W_i\) 是当前部位装分。总评按当前各部位装分加权平均，显示时保留 1 位小数。</div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">加速惩罚与补偿</div>
    <div class="formula-grid">
      <div class="formula-block">
        <div class="formula-title">修正系数</div>
        <div class="formula">\[
\Delta H = H_{\mathrm{required}} - H_{\mathrm{actual}}
\]
\[
C =
\begin{cases}
\max\left(0, 1 - \Delta H \times \frac{0.01}{3279}\right), & \Delta H > 0 \\
1 + (-\Delta H) \times \frac{0.006}{3279}, & \Delta H < 0 \\
1, & \Delta H = 0
\end{cases}
\]</div>
        <div class="formula-note">缺加速按 1% / 3279 点折损；溢出加速按 0.6% / 3279 点补偿。</div>
      </div>
      <div class="formula-block">
        <div class="formula-title">修正后 DPS</div>
        <div class="formula">\[
D_{\mathrm{adjusted}} = \left\lfloor D_{\mathrm{raw}} \times C \right\rfloor
\]</div>
        <div class="formula-note">单件评分中的 DPS 使用修正后 DPS。当前装备、空槽样本、候选装备都会先应用同一套加速修正规则。</div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">等级阈值</div>
    <div class="chips">
      <div class="chip">ACE ≥ 95</div>
      <div class="chip">S+ ≥ 90</div>
      <div class="chip">S ≥ 85</div>
      <div class="chip">A ≥ 80</div>
      <div class="chip">B ≥ 70</div>
      <div class="chip">C ≥ 60</div>
      <div class="chip">D ＜ 60</div>
    </div>
  </div>

  <div class="section">
    <div class="notice">该评级与实际 DPS 无单调性相关：高分不等于实际 DPS 必然更高，低分也不等于实际 DPS 必然更低。它只表示当前配装距离该心法、该评级循环、该候选池下毕业配装的接近程度。</div>
  </div>

  <div class="footer">命令：装备评级 help</div>
</div>
</body>
</html>
"""
custom_loop_help_template = r"""

<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
body { margin: 0; background: #edf1f7; font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif; color: #202638; }
.guide { width: 920px; box-sizing: border-box; padding: 34px; background: #f7f9fc; }
.header { padding: 28px 30px; background: #243149; color: #fff; border-radius: 8px; }
.eyebrow { font-size: 18px; color: #b9c7dc; font-weight: 700; }
.title { margin-top: 8px; font-size: 34px; line-height: 1.22; font-weight: 900; }
.subtitle { margin-top: 12px; font-size: 18px; color: #d8e0ed; line-height: 1.6; }
.section { margin-top: 18px; padding: 24px 26px; background: #fff; border: 1px solid #e0e5ef; border-radius: 8px; }
.section-title { font-size: 24px; font-weight: 900; margin-bottom: 18px; color: #1f2937; }
.section-subtitle { margin-top: -8px; margin-bottom: 15px; color: #5d687a; font-size: 17px; line-height: 1.55; }
.image-frame { overflow: hidden; border-radius: 8px; border: 1px solid #d8e0ec; background: #111827; }
.guide-image { display: block; width: 100%; height: auto; }
.caption { margin-top: 10px; color: #5f6878; font-size: 16px; line-height: 1.55; }
.steps { display: grid; gap: 12px; }
.step { display: grid; grid-template-columns: 42px 1fr; gap: 14px; align-items: start; }
.num { width: 42px; height: 42px; border-radius: 50%; background: #2f6bff; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 19px; font-weight: 900; }
.text { min-height: 42px; display: flex; align-items: center; font-size: 19px; line-height: 1.62; color: #333b4d; }
.code { margin: 10px 0 4px; padding: 13px 15px; border-radius: 6px; background: #f1f5fb; border: 1px solid #d9e2ef; font-size: 20px; font-weight: 800; color: #1d2b44; }
.example { display: inline-block; margin: 6px 10px 0 0; padding: 9px 12px; background: #fff8e6; border: 1px solid #f2d17a; border-radius: 6px; color: #62430b; font-size: 17px; font-weight: 700; }
.note { margin-top: 16px; padding: 14px 16px; background: #edf7ef; border: 1px solid #b7dfbf; border-radius: 6px; color: #275431; font-size: 18px; line-height: 1.6; font-weight: 700; }
.usage { display: grid; gap: 10px; }
.usage-item { padding: 13px 15px; background: #f7f9fc; border: 1px solid #e0e5ef; border-radius: 6px; font-size: 18px; line-height: 1.6; color: #343d50; }
.command { color: #1f57d6; font-weight: 900; }
.footer { margin-top: 16px; color: #697386; font-size: 15px; text-align: right; }
</style>
</head>
<body>
<div class="guide">
  <div class="header">
    <div class="eyebrow">自定义循环 help</div>
    <div class="title">如何制作一个专属于自己的 JCL 计算器循环</div>
    <div class="subtitle">按要求录制木桩 JCL，上传群文件后即可作为自己的计算器循环使用。</div>
  </div>
  <div class="section">
    <div class="section-title">制作 JCL</div>
    <div class="steps">
      <div class="step"><div class="num">1</div><div class="text">先按照图片这样勾选设置。</div></div>
      <div class="step"><div class="num">2</div><div class="text">去木桩面前。</div></div>
      <div class="step"><div class="num">3</div><div class="text">开始打。</div></div>
      <div class="step"><div class="num">4</div><div class="text">打到你认为 OK 的时间，点伤害统计清空（用来验证 DPS 是否正确），随后停手 F1 选中自己。</div></div>
      <div class="step"><div class="num">5</div><div class="text">点 JCL 文件位置，找到你刚刚打的木桩 JCL 文件。</div></div>
      <div class="step"><div class="num">6</div><div class="text">按下面格式命名：</div></div>
    </div>
    <div class="code">CAL-心法名-加速阈值-紫武/橙武-循环名.jcl</div>
    <div class="example">CAL-隐龙诀-30158-紫武-测试1.jcl</div>
    <div class="example">CAL-莫问-19285-橙武-测试2.jcl</div>
    <div class="steps" style="margin-top: 16px;">
      <div class="step"><div class="num">7</div><div class="text">上传群文件。</div></div>
    </div>
    <div class="note">至此，JCL 已经导入成功，接下来是计算。</div>
  </div>
  <div class="section">
    <div class="section-title">JCL 导出方法</div>
    <div class="section-subtitle">打开插件集的角色统计界面，切到装备统计页，点击右上角导出。弹出的文本内容用于确认当前装备数据；JCL 文件本体仍按上面的步骤从 JCL 文件位置找到并上传。</div>
    <div class="image-frame"><img class="guide-image" src="__JCL_EXPORT_IMAGE__"></div>
    <div class="caption">图中红框位置：装备统计页签与导出按钮。</div>
  </div>
  <div class="section">
    <div class="section-title">使用自定义循环</div>
    <div class="usage">
      <div class="usage-item">1. 发送 <span class="command">偏好 计算器来源 自定义</span> 可以使用上传的 JCL。</div>
      <div class="usage-item">2. 发送 <span class="command">偏好 计算器来源 公用</span> 可以恢复使用公用循环库。</div>
      <div class="usage-item">3. 按原本的计算器命令正常使用即可，包括 T计算器、DPS计算器、装备对比等均可。</div>
    </div>
  </div>
  <div class="section">
    <div class="section-title">提交公有循环</div>
    <div class="usage">
      <div class="usage-item">1. 发送 <span class="command">提交公有循环</span>，机器人会返回你上传过的自定义循环列表；也可以发送 <span class="command">提交公有循环 心法名</span> 只看指定心法。</div>
      <div class="usage-item">2. 发送要提交的编号后，循环会进入审批群待审；审批通过后会移动到公用循环库。</div>
      <div class="usage-item">3. 示例：<span class="command">提交公有循环 莫问</span>，列表返回后发送 <span class="command">1</span>。</div>
    </div>
  </div>
  <div class="section">
    <div class="section-title">变更循环名字</div>
    <div class="usage">
      <div class="usage-item">1. 发送 <span class="command">循环改名 心法名</span>，机器人会列出你提供的公有循环和对应私有循环。</div>
      <div class="usage-item">2. 发送要改名的编号后，再发送新的循环名；只会变更文件名里的循环名部分。</div>
      <div class="usage-item">3. 拥有改名权限的用户可发送 <span class="command">循环改名 QQ号 心法名</span> 变更指定用户提供的循环。</div>
    </div>
  </div>
  <div class="section">
    <div class="section-title">删除自定义循环</div>
    <div class="usage">
      <div class="usage-item">1. 发送 <span class="command">删除循环 心法名</span>，机器人会返回该心法循环列表；再发送编号删除单个或多个循环。</div>
      <div class="usage-item">2. 发送 <span class="command">删除循环all 心法名</span>，删除该心法下你上传的全部自定义循环。</div>
      <div class="usage-item">3. 示例：<span class="command">删除循环 莫问</span>，列表返回后发送 <span class="command">1,2</span>；或发送 <span class="command">删除循环all 莫问</span>。</div>
    </div>
  </div>
  <div class="footer">命令：自定义循环 help</div>
</div>
</body>
</html>
"""
equipment_rating_result_template = r"""

<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
* {
    box-sizing: border-box;
}
body {
    margin: 0;
    width: 1600px;
    background: #f5f6fa;
    color: #333;
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
}
.container {
    --theme-color: #3f7fbf;
    width: 1560px;
    margin: 20px;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
.header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
    padding: 24px;
    background: #fafafa;
    border-bottom: 1px solid #ddd;
}
.title {
    font-size: 32px;
    font-weight: 800;
    line-height: 1.2;
    color: var(--theme-color);
    border-left: 5px solid var(--theme-color);
    padding-left: 12px;
}
.subtitle {
    margin-top: 8px;
    font-size: 18px;
    color: #555;
    padding-left: 17px;
}
.legend {
    max-width: 560px;
    text-align: right;
    font-size: 17px;
    line-height: 1.55;
    color: #777;
}
.rating-total {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 16px;
    margin-bottom: 8px;
}
.rating-total img {
    width: 58px;
    height: 58px;
    object-fit: contain;
}
.total-score {
    font-size: 28px;
    line-height: 1.1;
    font-weight: 800;
    color: var(--theme-color);
}
.total-meta {
    margin-top: 4px;
    font-size: 15px;
    color: #777;
}
table {
    width: calc(100% - 48px);
    margin: 24px;
    border-collapse: collapse;
    table-layout: fixed;
    overflow: hidden;
    border-radius: 8px;
    background: #fff;
    border: 1px solid #eee;
}
thead {
    background: var(--theme-color);
    color: #fff;
}
th {
    padding: 13px 12px;
    font-size: 16px;
    font-weight: 700;
    text-align: left;
    white-space: nowrap;
}
td {
    padding: 12px;
    font-size: 17px;
    line-height: 1.35;
    border-bottom: 1px solid #f0f0f0;
    vertical-align: middle;
}
tbody tr:nth-child(even) {
    background: #fafafa;
}
tbody tr:last-child td {
    border-bottom: 0;
}
.slot {
    font-weight: 800;
    color: var(--theme-color);
}
.grade-stack {
    position: relative;
    width: 64px;
    height: 64px;
    margin: 0 auto;
}
.grade-icon {
    position: absolute;
    top: 0;
    left: 0;
    width: 64px;
    height: 64px;
    object-fit: contain;
}
.rank,
.percent,
.dps,
.diff {
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
}
.percent {
    font-weight: 800;
    color: var(--theme-color);
}
.dps {
    color: #333;
}
.equip {
    word-break: break-all;
    color: #444;
}
.equip-name {
    display: flex;
    align-items: baseline;
    gap: 7px;
    font-weight: 800;
    color: #333;
}
.quality {
    display: inline-block;
    min-width: 48px;
    padding: 2px 6px;
    border-radius: 6px;
    background: #f0f0f0;
    color: var(--theme-color);
    font-size: 14px;
    line-height: 1.3;
    text-align: center;
}
.attr {
    margin-top: 5px;
    font-size: 14px;
    line-height: 1.35;
    color: #777;
}
.diff {
    font-weight: 800;
}
.plus {
    color: var(--theme-color);
}
.best {
    color: var(--theme-color);
}
.minus {
    color: #777;
}
.note {
    font-size: 14px;
    color: #777;
}
.footer {
    margin-top: 0;
    padding: 15px 24px;
    background: #f0f0f0;
    border-top: 1px solid #ddd;
    text-align: center;
    font-size: 16px;
    color: #777;
}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <div>
            <div class="title">{{ value_0 }}</div>
            {{ value_1 }}
        </div>
        <div class="legend">
            <div class="rating-total">
                <img src="{{ value_2 }}" alt="{{ value_3 }}">
                <div>
                    <div class="total-score">{{ value_4 }} 分</div>
                    <div class="total-meta">{{ value_5 }} {{ value_6 }} · 有效部位 {{ value_7 }}/{{ value_8 }}</div>
                </div>
            </div>
            <div>{{ value_9 }}</div>
        </div>
    </div>
    <table>
        <thead>
            <tr>
                <th style="width: 72px;">部位</th>
                <th style="width: 86px;">评级</th>
                <th style="width: 92px;">排名</th>
                <th style="width: 90px;">评分</th>
                <th style="width: 90px;">最优强度</th>
                <th style="width: 122px;">当前{{ value_10 }}</th>
                <th>当前装备</th>
                <th style="width: 122px;">最优{{ value_11 }}</th>
                <th>最优装备</th>
                <th style="width: 116px;">差值</th>
                <th style="width: 172px;">备注</th>
            </tr>
        </thead>
        <tbody>
            {{ value_12 }}
        </tbody>
    </table>
    <div class="footer">单件评分、总评分和评级均来自装备评级接口。</div>
</div>
</body>
</html>
"""
calculator_timeline_template = r"""

<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
body { margin: 0; background: #edf1f7; font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif; color: #1f2430; }
body.kline-page { background: #05070b; color: #e5e7eb; }
.canvas { width: 1040px; padding: 34px; background: #f7f9fc; }
.canvas.kline-mode { background: #05070b; padding: 28px; }
.header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 22px; }
.title { font-size: 34px; font-weight: 800; }
.subtitle { margin-top: 8px; color: #697386; font-size: 18px; }
.badge { color: #fff; background: #263247; border-radius: 6px; padding: 8px 12px; font-weight: 700; }
.panel { background: #fff; border: 1px solid #e2e6ef; border-radius: 8px; padding: 22px; margin-bottom: 18px; }
.legend { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 16px; }
.legend-item { font-size: 16px; color: #4d5668; }
.legend-item i { display: inline-block; width: 18px; height: 5px; border-radius: 5px; margin-right: 7px; vertical-align: middle; }
.stats { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.stat-card { border-left: 5px solid #2F6BFF; background: #fafbfe; border-radius: 6px; padding: 14px; }
.stat-title { font-size: 18px; font-weight: 800; }
.stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 12px; margin-top: 10px; color: #566074; font-size: 14px; }
.stat-grid b { color: #1f2430; }
.kline-mode .header { margin-bottom: 18px; padding-bottom: 18px; border-bottom: 1px solid #172033; }
.kline-mode .title { color: #f8fafc; font-size: 30px; letter-spacing: 0; }
.kline-mode .subtitle { color: #94a3b8; font-size: 15px; }
.kline-mode .badge { background: #0b111b; border: 1px solid #243244; color: #cbd5e1; border-radius: 4px; }
.kline-mode .panel { background: #080d14; border-color: #1b2533; border-radius: 4px; }
.kline-mode .legend { margin-bottom: 14px; }
.kline-mode .legend-item { color: #cbd5e1; }
.kline-mode .stat-card { background: #0b111b; border: 1px solid #1e293b; border-left: 4px solid #2F6BFF; border-radius: 4px; }
.kline-mode .stat-title { color: #e5e7eb; }
.kline-mode .stat-grid { color: #8492a6; }
.kline-mode .stat-grid b { color: #f8fafc; }
.chart-title { font-size: 21px; font-weight: 800; margin-bottom: 8px; }
.chart { width: 100%; height: 350px; overflow: visible; }
.axis-label { fill: #858da0; font-size: 13px; }
.peak-label { font-size: 14px; font-weight: 700; }
.buff-frame { fill-opacity: 0.1; stroke-opacity: 0.42; stroke-width: 1.4; }
.buff-frame-label { font-size: 12px; font-weight: 800; opacity: 0.86; }
.kline-panel { background: #070A0F; border-color: #172033; }
.kline-mode .kline-panel { background: #05080d; padding: 20px 22px 18px; }
.kline-heading { color: #E5E7EB; margin-bottom: 4px; }
.kline-subtitle { color: #8B95A7; font-size: 14px; margin-bottom: 8px; }
.kline-chart { width: 100%; height: 456px; overflow: visible; }
.kline-grid { stroke: #1C2430; stroke-width: 1; }
.kline-axis { stroke: #334155; stroke-width: 1.2; }
.kline-zero-axis { stroke: #64748B; stroke-width: 1.2; stroke-dasharray: 6 5; }
.kline-axis-label { fill: #8B95A7; font-size: 13px; }
.kline-ma-line { stroke-width: 2.2; stroke-linejoin: round; stroke-linecap: round; }
.kline-ma-line.ma5 { stroke: #FACC15; }
.kline-ma-line.ma10 { stroke: #38BDF8; }
.kline-ma-line.ma20 { stroke: #C084FC; }
.kline-ma-label { font-size: 13px; font-weight: 900; }
.kline-ma-label.ma5 { fill: #FACC15; }
.kline-ma-label.ma10 { fill: #38BDF8; }
.kline-ma-label.ma20 { fill: #C084FC; }
.kline-panel .buff-frame { fill-opacity: 0.08; stroke-opacity: 0.28; }
.kline-panel .buff-frame-label { font-size: 12px; font-weight: 800; opacity: 0.82; }
</style>
</head>
<body class="{{ value_0 }}">
<div class="{{ value_1 }}">
  <div class="header">
    <div>
      <div class="title">{{ value_2 }}</div>
      <div class="subtitle">{{ value_3 }}</div>
    </div>
    <div class="badge">{{ value_4 }}</div>
  </div>
  <div class="panel">
    <div class="legend">{{ value_5 }}</div>
    <div class="stats">{{ value_6 }}</div>
  </div>
  {{ value_7 }}
  {{ value_8 }}
  {{ value_9 }}
</div>
</body>
</html>
"""
