template_preferences = """
<div class="preference-item">
    <div class="preference-name">{{ name }}</div>
    <div class="preference-values">
        {% for k, f in values.items() %}
        <div class="value-item">
            {% if f %}
                <strong>{{ k }}（当前）</strong>
            {% else %}
                {{ k }}
            {% endif %}
        </div>
        {% endfor %}
    </div>
    <div class="preference-description">
        {% for k, v in preferences.items() %}
            <div><strong>{{ k }}</strong>：{{ v }}{{ "。" if loop.last else "；" }}</div>
        {% endfor %}
    </div>
</div>"""