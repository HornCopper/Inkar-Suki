template_zone_overview = """
<tr>
    <td class="short-column">{{ name }}</td>
    <td class="short-column"><div class="progress-bar" style="margin: 0 auto;">
        <div class="progress-{{ relate_proportion }}" style="width: {{ proportion }};"></div>
        <span class="progress-text">{{ proportion }}</span>
    </div></td>
    <td class="short-column">{{ value }}</td>
</tr>
"""

template_zone_detail = """
<tr>
    {{ header }}
    <td class="short-column">{{ mode }}</td>
    <td class="short-column">
        <div class="progress-bar" style="margin: 0 auto;">
            <div class="progress" style="width: {{ schedule }};"></div>
            <span class="progress-text">{{ schedule }}</span>
        </div>
    </td>
    <td class="short-column">{{ num }}</td>
</tr>"""

template_zone_detail_header = """
<td class="short-column" rowspan="{{ count }}">{{ name }}</td>
"""

table_zone_overview_header = """
<tr>
    <th class="short-column" style="height:20px">名称</th>
    <th class="short-column" style="height:20px">进度</th>
    <th class="short-column" style="height:20px">资历</th>
</tr>"""

table_zone_detail_header = """
<tr>
    <th class="short-column" style="height:20px">名称</th>
    <th class="short-column" style="height:20px">副本</th>
    <th class="short-column" style="height:20px">进度</th>
    <th class="short-column" style="height:20px">资历</th>
</tr>"""