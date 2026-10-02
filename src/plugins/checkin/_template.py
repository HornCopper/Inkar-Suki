table_head = """
<tr>
    <th class="short-column">排行</th>
    <th class="short-column">头像</th>
    <th class="short-column">QQ号</th>
    <th class="short-column">金币</th>
    <th class="short-column">累计签到</th>
</tr>"""

template_body = """
<tr>
    <td class="short-column">{{ rank }}</td>
    <td class="short-column"><img src="{{ avatar }}" alt="icon" width="30" height="30"></td>
    <td class="short-column">{{ user_id }}</td>
    <td class="short-column">{{ coins }}</td>
    <td class="short-column">{{ count }}</td>
</tr>
"""


backpack_table_head = """
<th>奖品</th>
<th>记录编号</th>
<th>投放人</th>
<th>获得时间</th>
<th>兑付状态</th>
"""

backpack_row = """
<tr>
    <td class="backpack-prize">
        <span class="backpack-prize-name">{{ prize_name }}</span>
        <span class="backpack-quantity">×1</span>
    </td>
    <td class="backpack-record">#{{ award_id }}</td>
    <td class="backpack-provider">{{ provider_id }}</td>
    <td class="backpack-date">{{ awarded_at }}</td>
    <td>
        <span class="backpack-status {{ 'backpack-delivered' if delivered_at else 'backpack-pending' }}">
            {{ '已兑付' if delivered_at else '待兑付' }}
        </span>
        {% if delivered_at %}<div class="backpack-delivery-date">{{ delivered_at }}</div>{% endif %}
    </td>
</tr>
"""

pending_prize_table_head = """
<th>奖品</th>
<th>记录编号</th>
<th>获奖用户</th>
<th>投放人</th>
<th>获得时间</th>
"""

pending_prize_row = """
<tr>
    <td class="backpack-prize">
        <span class="backpack-prize-name">{{ prize_name }}</span>
        <span class="backpack-quantity">×1</span>
    </td>
    <td class="backpack-record">#{{ award_id }}</td>
    <td>{{ user_id }}</td>
    <td class="backpack-provider">{{ provider_id }}</td>
    <td class="backpack-date">{{ awarded_at }}</td>
</tr>
"""

backpack_css = """
.container { min-width: 1040px; max-width: 1240px; }
.item-table { width: 100%; min-width: 1040px; }
.item-table th { font-size: 20px; padding: 16px 18px; }
.item-table td { padding: 20px 18px; font-size: 20px; }
.item-table .backpack-prize { width: 320px; text-align: left; white-space: normal; }
.backpack-prize-name { font-weight: 600; overflow-wrap: anywhere; }
.backpack-quantity {
    display: inline-block; margin-left: 8px; padding: 2px 8px; border-radius: 4px;
    font-size: 16px; background: var(--inkar-accent-surface, #e8f4ff);
    color: var(--inkar-accent-ink, #2c7be5); white-space: nowrap;
}
.backpack-record { color: var(--inkar-secondary-text, #666); }
.backpack-status { display: inline-block; padding: 6px 12px; border-radius: 4px; font-size: 18px; }
.backpack-pending { background: #fff5df; color: #96601b; }
.backpack-delivered { background: #e8f5ed; color: #267449; }
.backpack-delivery-date { margin-top: 8px; font-size: 14px; color: var(--inkar-secondary-text, #666); }
.item-table .backpack-empty { padding: 80px 24px; color: var(--inkar-secondary-text, #666); }
.backpack-empty-title { margin: 0 0 12px; font-size: 26px; color: var(--inkar-text, #2c3e50); }
.backpack-empty-hint { margin: 0; font-size: 20px; }
"""
