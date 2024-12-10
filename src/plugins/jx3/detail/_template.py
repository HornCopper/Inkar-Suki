template_global_view = """
<tr>
    <td class="short-column">{{ subject }}</td>
    <td class="short-column">
        <div class="progress-bar" style="margin: 0 auto;">
            <div class="progress-{{ progress }}" style="width: {{ width }}%;"></div>
            <span class="progress-text">{{ width }}%</span>
        </div>
    </td>
    <td class="short-column">{{ value }}</td>
</tr>"""

global_view_head = """
<tr>
    <th class="short-column" style="height:20px">名称</th>
    <th class="short-column" style="height:20px">进度</th>
    <th class="short-column" style="height:20px">资历</th>
</tr>"""

dungeon_view_head = """
<tr>
    <th class="short-column" style="height:20px">副本</th>
    <th class="short-column" style="height:20px">难度</th>
    <th class="short-column" style="height:20px">进度</th>
    <th class="short-column" style="height:20px">资历</th>
</tr>"""

dungeon_first = """
<td class="short-column" rowspan="{{ mode_count }}">{{ name }}</td>"""

template_dungeon_view = """
<tr>
    $first
    <td class="short-column">{{ mode }}</td>
    <td class="short-column">
        <div class="progress-bar" style="margin: 0 auto;">
            <div class="progress-{{ progress }}" style="width: {{ width }}%;"></div>
            <span class="progress-text">{{ width }}%</span>
        </div>
    </td>
    <td class="short-column">{{ value }}</td>
</tr>"""