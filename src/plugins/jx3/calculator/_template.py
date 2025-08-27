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

template_rdps = """
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