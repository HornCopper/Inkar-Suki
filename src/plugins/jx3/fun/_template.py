template_loot = """
<tr class="boss-row{% if highlight %} boss-row--rare{% endif %}">
    <th colspan="3"><span class="boss-mark">◆</span>{{ boss_name }}宝箱</th>
</tr>
{{ items }}
"""

template_item = """
<tr class="loot-row{% if highlight %} loot-row--rare{% endif %}">
    <td class="icon-cell"><span class="icon-frame"><img src="{{ icon }}">{% if count > 1 %}<span class="item-count">{{ count }}</span>{% endif %}</span></td>
    <td class="item-name" style="color: {{ item_color }}">{{ item_name }}</td>
    <td class="item-attr">{% if attr %}{{ attr }}{% endif %}</td>
</tr>
"""

template_loot_horizontal = """
<section class="boss-block{% if highlight %} boss-block--rare{% endif %}">
    <header class="boss-header"><span class="boss-mark">◆</span>{{ boss_name }}宝箱</header>
    <div class="loot-strip">{{ items }}</div>
</section>
"""

template_item_horizontal = """
<article class="loot-card{% if highlight %} loot-card--rare{% endif %}">
    <span class="icon-frame"><img src="{{ icon }}">{% if count > 1 %}<span class="item-count">{{ count }}</span>{% endif %}</span>
    <div class="item-name" style="color: {{ item_color }}">{{ item_name }}</div>
    {% if attr %}<div class="item-attr">{{ attr }}</div>{% endif %}
</article>
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

table_random_5gimage_record_head = """
<th>时间</th>
<th>服务器</th>
<th>使用的原始图</th>
<th>开出的图</th>
<th>原图价格</th>
<th>开出价格</th>
<th>盈亏</th>
"""

table_random_5gimage_rank_head = """
<th>排行</th>
<th>头像</th>
<th>昵称</th>
<th>开图次数</th>
<th>累计盈亏</th>
<th>平均盈亏</th>
"""

template_random_5gimage_record = """
<tr>
  <td>{{ time }}</td>
  <td>{{ server }}</td>
  <td>{{ box_name }}</td>
  <td>{{ result_name }}</td>
  <td>{{ box_price }}</td>
  <td>{{ result_price }}</td>
  <td class="{{ profit_class }}">{{ profit }}</td>
</tr>
"""

template_random_5gimage_rank = """
<tr>
  <td>{{ rank }}</td>
  <td><img class="rank-avatar" src="{{ avatar }}" alt="avatar"></td>
  <td>{{ nickname }}</td>
  <td>{{ count }}</td>
  <td class="{{ total_class }}">{{ total_profit }}</td>
  <td class="{{ avg_class }}">{{ avg_profit }}</td>
</tr>
"""

template_random_5gimage = """
<html>
<head>
<meta charset="utf-8">
<style>
@font-face {
  font-family: panel-font;
  src: url("{{ font }}");
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: #fff;
  font-family: panel-font, sans-serif;
}
html body .style2-report.random-image-card {
  width: 820px;
  background: #fff !important;
  color: #2c3e50;
  font-family: panel-font, sans-serif;
  border: 1px solid #e7ebef;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, .05);
}
.items {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: stretch;
  gap: 16px;
}
.item {
  min-height: 264px;
  padding: 18px;
  background: #fff;
  border: 1px solid #e7ebef;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.label {
  width: 100%;
  font-size: 15px;
  color: #667085;
  text-align: left;
  margin-bottom: 14px;
}
.icon {
  width: 96px;
  height: 96px;
  object-fit: contain;
  border: 1px solid #e7ebef;
  border-radius: 4px;
  background: #f8f9fa;
}
.name {
  min-height: 50px;
  margin-top: 14px;
  font-size: 20px;
  line-height: 1.35;
  font-weight: 700;
  overflow-wrap: anywhere;
}
.price-block {
  width: 100%;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid #e7ebef;
}
.price-label { color: #667085; font-size: 13px; }
.price {
  margin-top: 4px;
  font-size: 20px;
  color: #2c3e50;
}
.price img,
.profit img {
  vertical-align: -3px;
  margin: 0 2px;
}
.profit {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 16px;
  padding: 14px 18px;
  background: #f8f9fa;
  border: 1px solid #e7ebef;
  border-radius: 4px;
}
.profit.plus {
  background: #eef8f1;
  border-color: #cbe9d6;
}
.profit.minus {
  background: #fff3f2;
  border-color: #f2d0cd;
}
.profit .caption {
  color: #667085;
  font-size: 16px;
}
.profit .value {
  font-size: 24px;
  font-weight: 700;
}
.plus { color: #167c4a; }
.minus { color: #ad3737; }
.neutral { color: #475467; }
html body .style2-report.random-image-card .report-footer {
  margin-top: 16px;
  padding: 10px 12px;
  font-size: 16px !important;
  line-height: 1.4;
}
.no-price {
  color: #667085;
}
</style>
</head>
<body>
<main class="card style2-report random-image-card">
  <div class="report-header">
    <h1 class="report-title">随机武技图</h1>
    <p class="report-subtitle">{{ server }} · 武技殊影图·{{ box_name }}</p>
  </div>
  <div class="items">
    <div class="item">
      <div class="label">使用的原始图</div>
      <img class="icon" src="{{ box_icon }}" alt="武技殊影图·{{ box_name }}">
      <div class="name">{{ box_name }}</div>
      <div class="price-block"><div class="price-label">参考价</div><div class="price">{{ box_price }}</div></div>
    </div>
    <div class="item">
      <div class="label">开出的图</div>
      <img class="icon" src="{{ opened_icon }}" alt="{{ opened_name }}">
      <div class="name">{{ opened_name }}</div>
      <div class="price-block"><div class="price-label">参考价</div><div class="price">{{ opened_price }}</div></div>
    </div>
  </div>
  <div class="profit {{ profit_class }}">
    <div class="caption">本次盈亏</div>
    <div class="value {{ profit_class }}">{{ profit }}</div>
  </div>
  <footer class="report-footer">{{ bot_name }}: {{ saohua }}</footer>
</main>
</body>
</html>
"""
