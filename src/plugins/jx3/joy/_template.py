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
body {
  margin: 0;
  background: transparent;
  font-family: panel-font, sans-serif;
}
.card {
  width: 820px;
  padding: 28px 28px 18px;
  background: #f7f2e8;
  color: #263242;
  border: 1px solid #e2d7c4;
  border-radius: 8px;
  box-shadow: 0 14px 38px rgba(57, 45, 28, .18);
}
.items {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: stretch;
  gap: 18px;
}
.item {
  min-height: 250px;
  padding: 22px;
  background: #fffaf0;
  border: 1px solid #e4d7c2;
  border-radius: 8px;
  text-align: center;
}
.label {
  font-size: 16px;
  color: #667085;
  margin-bottom: 16px;
}
.icon {
  width: 96px;
  height: 96px;
  border-radius: 8px;
  box-shadow: 0 0 0 1px rgba(77, 63, 42, .18);
}
.name {
  height: 56px;
  margin-top: 16px;
  font-size: 20px;
  line-height: 28px;
  color: #1f2937;
}
.price {
  margin-top: 16px;
  font-size: 22px;
  color: #8f5f14;
}
.price img,
.profit img {
  vertical-align: -3px;
  margin: 0 2px;
}
.profit {
  width: 290px;
  margin: 10px auto 0;
  padding: 10px 18px;
  background: #fffaf0;
  border: 1px solid #e4d7c2;
  border-radius: 8px;
  text-align: center;
}
.profit .caption {
  color: #667085;
  font-size: 15px;
  margin-bottom: 4px;
}
.profit .value {
  font-size: 24px;
}
.plus { color: #1f8f55; }
.minus { color: #c24141; }
.neutral { color: #475467; }
footer {
  background: #f0f0f0;
  text-align: center;
  padding: 15px;
  font-size: 20px;
  color: #777;
  margin-top: 16px;
}
.no-price {
  color: #98a2b3;
}
</style>
</head>
<body>
<div class="card">
  <div class="items">
    <div class="item">
      <div class="label">使用的原始图</div>
      <img class="icon" src="{{ box_icon }}">
      <div class="name">{{ box_name }}</div>
      <div class="price">{{ box_price }}</div>
    </div>
    <div class="item">
      <div class="label">开出的图</div>
      <img class="icon" src="{{ opened_icon }}">
      <div class="name">{{ opened_name }}</div>
      <div class="price">{{ opened_price }}</div>
    </div>
  </div>
  <div class="profit">
    <div class="caption">本次盈亏</div>
    <div class="value {{ profit_class }}">{{ profit }}</div>
  </div>
  <footer>{{ appinfo }} | {{ bot_name }}: {{ saohua }}</footer>
</div>
</body>
</html>
"""
