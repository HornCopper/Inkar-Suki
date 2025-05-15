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

template_shilian_box = """
<div class="box {{ highlight }}">
    {{ items }}
</div>
"""

template_shilian_single = """
<div class="icon-wrapper">
    <img src="{{ icon }}" class="icon">
    <span class="label" style="color: rgb{{ color }}; font-size: 16px">{{ name }}</span>
</div>
"""