msg_box = """
<div class="message-box">
    <div class="element">
        <div class="cell"><span>段位</span></div>
        <div class="cell">{{ rank }}</div>
    </div>
    <div class="element">
        <div class="cell"><span>总场次</span></div>
        <div class="cell">{{ count }}</div>
    </div>
    <div class="element">
        <div class="cell"><span>胜利</span></div>
        <div class="cell">{{ win }}</div>
    </div>
    <div class="element">
        <div class="cell"><span>胜率</span></div>
        <div class="cell">{{ percent }}</div>
    </div>
    <div class="element">
        <div class="cell"><span>评分</span></div>
        <div class="cell">{{ score }}</div>
    </div>
    <div class="element">
        <div class="cell"><span>最佳</span></div>
        <div class="cell">{{ best }}</div>
    </div>
    <div class="element">
        <div class="cell"><span>排名（周）</span></div>
        <div class="cell">{{ rank_ }}</div>
    </div>
</div>"""

template_arena_record = """
<tr>
    <td class="short-column"><img src="{{ kungfu }}" width="30px" height="30px"></td>
    <td class="short-column">{{ rank }}段局<br>{{ mode }}</td>
    <td class="short-column">{{ time }}<br>{{ relate }} {{ length }}</td>
    <td class="short-column">{{ score }}<span style="color:{{ color }}">（{{ delta }}）</span></td>
    <td class="short-column"><span style="color: {{ color }}">{{ status }}</span></td>
</tr>"""