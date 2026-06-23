template_body = """
<tr>
    <td class="short-column blacklist-source-column">{{ source }}</td>
    <td class="short-column blacklist-name-column">{{ name }}</td>
    <td class="short-column blacklist-reason-column">{{ reason }}</td>
    <td class="short-column blacklist-time-column">{{ time }}</td>
</tr>"""

table_head = """
<th class="short-column blacklist-source-column">来源</th>
<th class="short-column blacklist-name-column">名称</th>
<th class="short-column blacklist-reason-column">原因</th>
<th class="short-column blacklist-time-column">时间</th>"""

additional_css = """
.container {
    min-width: 1280px;
}

.item-table {
    width: 1280px;
    table-layout: fixed;
}

.item-table th,
.item-table td {
    box-sizing: border-box;
}

.blacklist-source-column {
    width: 190px;
}

.blacklist-name-column {
    width: 250px;
    max-width: 250px;
    white-space: normal !important;
    overflow-wrap: anywhere;
    word-break: break-word;
    line-height: 1.4;
}

.blacklist-reason-column {
    width: 450px;
    max-width: 450px;
    white-space: normal !important;
    overflow-wrap: anywhere;
    word-break: break-word;
    line-height: 1.4;
}

.blacklist-time-column {
    width: 390px;
    white-space: nowrap !important;
}

td.blacklist-name-column,
td.blacklist-reason-column {
    text-align: left;
}
"""
