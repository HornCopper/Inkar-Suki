template_equip = """
<div class="equipment-item">
    <div class="image-container" style="position: relative;">
        {{ peerless }}
        <img src="{{ icon }}" class="bottom-image">
        <img src="{{ box }}" class="top-image">
    </div>
    <div class="equipment-details">
        <div style="color: rgb{{ color }}">{{ name }}（{{ quality }}）</div>
        <div class="attributes">{{ attr }}</div>
        <div class="source">{{ source }}</div>
        <div class="source" style="color: rgb(255, 165, 0);font-size:14px">{{ effect }}</div>
    </div>
    <div class="equipment-icons-wrapper">
        <p>{{ strength }}</p>
        <div class="equipment-enchant-wrapper">
            {% for enchant in enchants %}
                {{ enchant }}{% if not loop.last %}{% endif %}
            {% endfor %}
        </div>
        <div class="equipment-enchant-wrapper">
            {% for attr, icon in fivestones.items() %}
            <img src="{{ icon }}" style="width: 20px; height: 20px;margin-right: 3px;margin-left: 5px">
            <span>{{ attr }}</span>
            {% endfor %}
        </div>
    </div>
</div>
"""

template_talent = """
<div class="talent">
    <img src="{{ icon }}">
    <span style="font-size: 18px">{{ name }}</span>
</div>
"""

template_enchant = """
<span class="equipment-enchant">
    <img src="{{ icon }}" style="width: 20px; height: 20px;margin-right: 3px;margin-left: 5px">
    <span>{{ name }}</span>
</span>
"""

template_other = """
<div style="display: flex;align-items: flex-end;gap: 5px;">
    <img src="{{ icon }}"
        style="width: 50px; height: 50px;">
    <div style="display: grid;">{{ kungfu }}·{{ tag }}（{{ score }}）<br>
        <p style="font-size: 13px;">标签：{{ msg }}
    </div>
</div>"""