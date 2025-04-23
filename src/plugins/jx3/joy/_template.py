template_loot = """
<tr>
    <th colspan="3" style="text-align: center; color:#000000; background-color: {{ title_color }};">{{ boss_name }}宝箱</th>
    {{ items }}
</tr>
"""

template_item = """
<tr style="background-color: {{ detail_color }};">
    <td><img src="{{ icon }}"></td>
    <td style="color: {{ item_color }}">{{ item_name }}</td>
    <td style="color: rgb(0, 210, 75)">{{ attr }}</td>
</tr>
"""