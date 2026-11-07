template_assistance_unit = """
<div class="cell" style="background-color: {{ color }};">
    <div class="player">
        <div class="avatar-wrap">
            <img class="member-avatar{% if not avatar %} profession-avatar{% endif %}" src="{{ avatar or icon }}">
            {% if avatar %}<img class="job-icon" src="{{ icon }}">{% endif %}
        </div>
        <div class="member-identity">
            <div class="member-role">{{ name }}</div>
            <div class="member-name">{{ qq }}</div>
            <span class="member-time">{{ time }}</span>
        </div>
    </div>
</div>
"""
