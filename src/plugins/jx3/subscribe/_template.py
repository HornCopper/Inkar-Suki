template_subscribe = """
<div class="el-col">
    <div class="el-box">
        <div class="el-image" style="margin-left: 10px;">
            <img src="{{ image }}" style="object-fit:contain">
        </div>
        <div class="el-text">
            <div class="element-text-up">{{ subject }}</div>
            <div class="element-text-down">{{ description }}</div>
        </div>
    </div>
    <div class="el-status {{ status }}">{{ flag }}</div>
</div>"""