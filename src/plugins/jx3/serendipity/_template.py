poem = "<td class=\"short-column-content\" rowspan=\"114514\"></td>" # 来点诗句

template_serendity = """
<tr>
    <td class="empty-column">
        <img src="{{ peerless_flag }}">
    </td>
    <td class="empty-column">
        <img src="{{ serendipity_icon }}" alt="{{ serendipity_name }}.png">
    </td>
    <td class="short-column">{{ actual_time }}<br>{{ relative_time }}</td>
</tr>"""

template_v3_cell = """
<td class="element-column{% if featured_image_path %} featured-cell featured-{{ category }}{% endif %}"{% if featured_image_path %} rowspan="2"{% endif %}>
    {% if featured_image_path %}
    <div class="element-container featured-card {{ status }}-card">
        <div class="ink-circle">
            <img class="feature-art {{ status }}-color" src="{{ featured_image_path }}" alt="{{ name }}.png">
            <img class="feature-icon" src="{{ serendipity_icon }}" alt="">
            <img class="feature-name" src="{{ featured_name_path }}" alt="{{ name }}">
        </div>
        <div class="status-row featured-status">
            <span class="status-dot"></span>
            <div class="{{ status }}-serendipity">{{ msg }}</div>
        </div>
    </div>
    {% else %}
    <div class="element-container {{ status }}-card">
        <div class="name-banner">
            {% if image_path %}
            <img class="{{ status }}-color" src="{{ image_path }}" alt="{{ name }}.png">
            {% else %}
            <span class="fallback-name">{{ name }}</span>
            {% endif %}
        </div>
        <div class="status-row">
            <span class="status-dot"></span>
            <div class="{{ status }}-serendipity">{{ msg }}</div>
        </div>
    </div>
    {% endif %}
</td>"""

template_v3_row = """<tr>
{{ cells }}
</tr>"""

recent_serendipity_head = """
<tr>
    <th class="short-column">角色</th>
    <th class="short-column">奇遇</th>
    <th class="short-column">时间</th>
</tr>"""

recent_serendipity_row = """
<tr>
    <td class="short-column">{{ role_name }}</td>
    <td class="short-column">
        {% if event_icon %}
        <img src="{{ event_icon }}" alt="{{ event_name }}" style="width: 224px; height: 49px; object-fit: contain;">
        {% else %}
        {{ event_name }}
        {% endif %}
    </td>
    <td class="short-column">{{ time }}<br><span style="color: #7f8c8d; font-size: 14px;">{{ relative_time }}</span></td>
</tr>"""

statistics_serendipity_head = """
<tr>
    <th class="short-column">服务器</th>
    <th class="short-column">角色</th>
    <th class="short-column">时间</th>
</tr>"""

statistics_serendipity_row = """
<tr>
    <td class="short-column"><span class="server-tag">{{ server }}</span></td>
    <td class="short-column">{{ role_name }}</td>
    <td class="short-column">{{ time }}<br><span style="color: #7f8c8d; font-size: 14px;">{{ relative_time }}</span></td>
</tr>"""

collect_serendipity_card = """
<article class="event-card{% if peerless_icon %} has-peerless{% endif %}">
    <div class="ink-circle">
        {% if show_path %}<img class="event-art" src="{{ show_path }}" alt="{{ event_name }}">{% endif %}
        {% if name_path %}<img class="event-name" src="{{ name_path }}" alt="{{ event_name }}">{% else %}<span class="event-name-text">{{ event_name }}</span>{% endif %}
        {% if peerless_icon %}<img class="peerless-badge" src="{{ peerless_icon }}" alt="绝世">{% endif %}
        <span class="event-count">{{ count }} 次</span>
    </div>
    <div class="latest-role">{{ role_name }}</div>
    <div class="latest-time">{{ time }}</div>
    <div class="relative-time">{{ relative_time }}</div>
</article>"""

collect_serendipity_row = """<div class="card-row">{{ cards }}</div>"""
