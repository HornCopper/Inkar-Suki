from src.const.path import ASSETS, build_path


template_dilu = """
<tr>
    <td class="short-column">{{ server }}</td>
    <td class="short-column">刷新：{{ flush }}<br>捕获：{{ captured }}<br>竞拍：{{ sell }}</td>
    <td class="short-column">{{ map }}</td>
    <td class="short-column">
        <div style="margin-bottom: 5px;">{{ capturer }}</div>
        <div style="display: inline-flex; align-items: center; gap: 5px; color: #7f8c8d; font-size: 14px; line-height: 18px;">
            {{ ci }}<span>{{ cc }}</span>
        </div>
    </td>
    <td class="short-column">
        <div style="margin-bottom: 5px;">{{ auctioner }}</div>
        <div style="display: inline-flex; align-items: center; gap: 5px; color: #7f8c8d; font-size: 14px; line-height: 18px;">
            {{ bi }}<span>{{ bc }}</span>
        </div>
    </td>
    <td class="short-column">{{ price }}</td>
</tr>
"""

bad = f"<img src=\"{build_path(ASSETS, ['image', 'jx3', 'camp', 'eren.png'])}\" style=\"width: 18px; height: 18px; object-fit: contain;\">"
good = f"<img src=\"{build_path(ASSETS, ['image', 'jx3', 'camp', 'haoqi.png'])}\" style=\"width: 18px; height: 18px; object-fit: contain;\">"

table_dilu_head = """
<tr>
    <th class="short-column">区服</th>
    <th class="short-column">时间</th>
    <th class="short-column">地图</th>
    <th class="short-column">捕捉</th>
    <th class="short-column">拍卖</th>
    <th class="short-column">金额</th>
</tr>"""
