template_weather = """
<div class="forecast-item">
    <span>{{ date }}</span>
    <span>
        <i class="qi-{{ day_icon }}-fill" style="margin-right: 5px;"></i>{{ day_weather }} / <i class="qi-{{ night_icon }}-fill" style="margin-right: 5px;"></i>{{ night_weather }}
    </span>
    <span>{{ temp }}</span>
</div>
"""