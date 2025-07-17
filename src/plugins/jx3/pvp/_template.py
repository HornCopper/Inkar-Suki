msg_box = """
<div class="general-summary">
    <div class="summary-card">
        <h3>段位</h3>
        <div class="summary-value">{{ rank }}</div>
    </div>
    <div class="summary-card">
        <h3>总场次</h3>
        <div class="summary-value">{{ count }}</div>
    </div>
    <div class="summary-card">
        <h3>胜利场次</h3>
        <div class="summary-value">{{ win }}</div>
    </div>
    <div class="summary-card">
        <h3>胜率</h3>
        <div class="summary-value">{{ percent }}</div>
    </div>
    <div class="summary-card">
        <h3>评分</h3>
        <div class="summary-value">{{ score }}</div>
    </div>
    <div class="summary-card">
        <h3>最佳</h3>
        <div class="summary-value">{{ best }}</div>
    </div>
    <div class="summary-card">
        <h3>周排名</h3>
        <div class="summary-value">{{ rank_ }}</div>
    </div>
</div>
"""

template_arena_record = """
<tr>
    <td>
        <img src="{{ kungfu }}"
            width="30" height="30">
    </td>
    <td>{{ rank }}段局 {{ mode }}</td>
    <td class="time-cell">{{ time }}<br>{{ relate }} {{ length }}</td>
    <td>
        {{ score }}
        <span
            style="display: inline-block;padding: 2px 8px;border-radius: 12px;background: {{ color }};color: #FFFFFF;font-size: 24px;">
            {{ delta }}
        </span>
    </td>
    <td>
        <span class="result-{{ status }}">{{ result }}</span>
        <span
            style="display: inline-block;padding: 2px 8px;border-radius: 12px;background: {{ mvp_color }};color: #000000;font-size: 24px;">
            MVP
        </span>
    </td>
</tr>
"""