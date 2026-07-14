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
