from typing import List
import asyncio
import json
import pathlib2
from src.tools.generate import get_uuid, generate
from src.tools.dep import *
template_root = pathlib2.Path(__file__).parent
template_path = template_root.joinpath('template.html')


def get_template_path(resources_path: str):
    '''
    获取资源目录
    '''
    return template_root.joinpath(resources_path)


def find_str(raw: str, find: str, start: int) -> int:
    try:
        r = raw.index(find, start)
    except Exception as ex:
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
            raise InvalidTagException(f'cant find end pos.')
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
    return f'\n'.join(result)


async def get_render_image(view_file_path: str, data: dict = None, delay: int = 0, target: str = 'section') -> bytes:
    '''
    渲染网页为图片
    @param view_file_path: 页面文件
    @param data: 数据
    @param delay: 延迟截图时间，单位ms
    @param target: 截图目标标签
    '''
    if not data:
        data = {}
    content = get_render_content(view_file_path, data)
    file = pathlib2.Path(CACHE).joinpath(f'tpl_{get_uuid()}.html').as_posix()
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
    return await generate(file, delay=delay, locate=target)


def __init_data(data: dict):
    '''覆盖原始data
    '''
    template = '''const _raw_setup = component.setup
    component.setup = () => {
      const data = {{data}}
      window.params_data = data
      const result = Object.assign({}, _raw_setup())
      const v_result = Object.assign(result, data)
      return v_result
    }
    '''.replace('{{data}}', json.dumps(data))
    return template


def get_render_content(view_file_path: str, data: dict) -> str:
    '''
    渲染页面
    @param view_file_path:模板文件目录
    @param data:将替换setup()中的data字段
    '''
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(view_file_path, 'r', encoding='utf-8') as f:
        view_content = f.read()
    content_template = get_tag_content(view_content, 'template')
    content = content.replace('<template.HERE />', content_template)
    # 注入css
    content_style = get_tag_content(view_content, 'style')
    content = content.replace('.window.style.HERE', content_style)

    # 注入脚本
    content_script = get_tag_content(view_content, 'script')
    content = content.replace('window.component.HERE', content_script)
    content = content.replace('window.component.data.HERE', __init_data(data))

    # 加载所有脚本文件
    script_src = view_content.split('<script src="')
    script_src = script_src[1:]
    script_src = [x.split('"') for x in script_src]
    script_src = [x[0] for x in script_src if len(x) > 1]
    script_src = [f'<script src="{x}" ></script>' for x in script_src]
    content_src = "\n".join(script_src)
    content = content.replace('<script_files />', content_src)

    return content
