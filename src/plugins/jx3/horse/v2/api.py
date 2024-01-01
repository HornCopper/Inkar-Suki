from src.tools.dep import *
from ..api_lib import *
data_horse_reporter: dict[str, HorseRecords] = {}  # 记录历史


async def get_horse_reporter_data(server: str, start: int = 0, end: int = 1):
    records = []
    for i in range(start, end):
        final_url = f"https://next2.jx3box.com/api/game/reporter/horse?pageIndex={i+1}&pageSize=50&type=horse&server={server}"
        data = await get_api(final_url)
        tmp_records = data.get('data').get('list') or []
        records += tmp_records
    return records


async def get_horse_reporter_raw(server: str) -> list[HorseEventRecord]:
    records = await get_horse_reporter_data(server)
    new_records = HorseRecords(server, records)
    prev_records = data_horse_reporter.get(server)
    if not prev_records:
        # 首次加载时多加载2页的
        records = await get_horse_reporter_data(server, 1, 5)
        prev_records = HorseRecords(server, records)
    data_horse_reporter[server] = new_records.merge_records(prev_records)
    valids = data_horse_reporter[server].valid_records
    return valids


def get_groups_by_valids(valids: list[HorseEventRecord]):
    # 按地图-马名查时间戳
    records_dict: dict[str, list[HorseEventRecord]] = {}
    for x in valids:
        key = f'{x.map_id}{x.horses_id}'
        if not records_dict.get(key):
            records_dict[key] = []
        records_dict[key].append(x)

    # 分组成不同组，120秒以内差距的视为同一个组
    groups: list[list[HorseEventRecord]] = []
    for x in records_dict:
        items = records_dict[x]
        current_group = []
        cur_group_time = 0
        for cur in items:
            if abs(cur.timestamp.timestamp() - cur_group_time) < 600:
                current_group.append(cur)
                continue  # 同类则加入
            # 否则创建新分组
            if current_group:
                groups.append(current_group)
            current_group = [cur]
            cur_group_time = cur.timestamp.timestamp()
        if current_group:
            groups.append(current_group)  # 将最后一个分组加入
    return groups


def get_horse_list_by_valids(valids: list[HorseEventRecord]):
    horse_data = extensions.flat([x.horses for x in valids])
    horse_data = extensions.distinct(horse_data, lambda x: x.key)
    return horse_data


def handle_horse_to_export(valids: list[HorseEventRecord]) -> tuple[list[HorseRecord], list[MapDataWithHorse], list[HorseInfo]]:
    map_data = extensions.distinct(valids, lambda x: x.map_id)
    map_data = [MapDataWithHorse(x.map_horse_data, x.map_data) for x in map_data]

    groups = get_groups_by_valids(valids)
    valids_records: list[HorseEventRecord] = []
    for group in groups:
        avg = extensions.reduce(group, lambda prev, x: prev + x.timestamp.timestamp(), 0)
        avg = avg / len(group)
        # 修改分组的实际值
        group[0].timestamp = DateTime(avg)
        valids_records.append(group[0])

    horse_data = get_horse_list_by_valids(valids)
    return valids_records, map_data, horse_data


async def get_horse_reporter(server: str) -> tuple[list[HorseRecord], list[MapDataWithHorse], list[HorseInfo]]:
    '''获取指定服务器当前马场状态'''
    if not server:
        return PROMPT_ServerNotExist
    valids = await get_horse_reporter_raw(server)
    return handle_horse_to_export(valids)
