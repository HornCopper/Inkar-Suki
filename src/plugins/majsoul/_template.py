template_majsoul_record = """
<tr>
    <td>{{ level }}</td>
    <td>{{ num }}</td>
    <td>{{ _1st }} <br>（{{ sc1）}} <br> {{ gr1 }}</td>
    <td>{{ _2nd }} <br>（{{ sc2）}} <br> {{ gr2 }}</td>
    <td>{{ _3rd }} <br>（{{ sc3）}} <br> {{ gr3 }}</td>
    <td>{{ _4th }} <br>（{{ sc4）}} <br> {{ gr4 }}</td>
    <td>{{ time }}</td>
</tr>"""

max_points = {
    "初1": 20,
    "初2": 80,
    "初3": 200,
    "士1": 600,
    "士2": 800,
    "士3": 1000,
    "杰1": 1200,
    "杰2": 1400,
    "杰3": 2000,
    "豪1": 2800,
    "豪2": 3200,
    "豪3": 3600,
    "圣1": 4000,
    "圣2": 6000,
    "圣3": 9000
}

gamemode = {
    "金东": 8,
    "金": 9,
    "玉东": 11,
    "玉": 12,
    "王东": 15,
    "王座": 16,
    "三金东": 21,
    "三金": 22,
    "三玉东": 23,
    "三玉": 24,
    "三王东": 25,
    "三王座": 26,
}

koromo_api_sp = "https://5-data.amae-koromo.com/api/v2/pl4/search_player/{player}?limit=20&tag=all" 

koromo_api_pr = "https://5-data.amae-koromo.com/api/v2/pl4/player_records/{player_id}/{end_timestamp}/{start_timestamp}?limit=5&mode={mode}&descending=true"

koromo_api_ps = "https://5-data.amae-koromo.com/api/v2/pl4/player_stats/{player_id}/{start_timestamp}/{end_timestamp}?mode={mode}"