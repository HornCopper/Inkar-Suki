from typing import List


def find_str(raw: str, find: str, start: int) -> int:
    try:
        r = raw.index(find, start)
    except Exception as _:
        return -1
    return r


class InvalidTagException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def get_tag_content_list(data: str, tag: str) -> List[str]:
    tag_start = f'<{tag}>'
    tag_start2 = f'<{tag} '
    len_start = len(tag_start)
    tag_end = f'</{tag}>'

    stack_tag = 0
    stack_len = 0
    result = []
    pos = 0
    is_partial = False
    while True:
        pos_start = find_str(data, tag_start, pos)
        pos_start2 = find_str(data, tag_start2, pos)
        is_partial = pos_start == - \
            1 or (pos_start > pos_start2 and pos_start2 != -1)
        if is_partial:
            pos_start = pos_start2
        pos_end = find_str(data, tag_end, pos)
        if pos_start == -1 and pos_end == -1:
            break
        if pos_end == -1:
            raise InvalidTagException('cant find end pos.')
        if pos_start > pos_end or pos_start == -1:
            if stack_len == 0:
                raise InvalidTagException(
                    f'start at:{pos_start},but end at {pos_end},which overflow start.')
            stack_len -= 1
            if stack_len == 0:
                result.append(data[stack_tag:pos_end])
            pos = pos_end + 1
            continue
        pos = pos_start + len_start
        if is_partial:
            pos = find_str(data, '>', pos) + 1  # 忽略attr
        if stack_len == 0:
            stack_tag = pos
        stack_len += 1
    return result


def get_tag_content(data: str, tag: str) -> str:
    result = get_tag_content_list(data, tag)
    return str.join('\n', result)
