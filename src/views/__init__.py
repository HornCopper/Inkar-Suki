from src.tools.dep.common_api.none_dep_api.HtmlTagHandler import *
from typing import List
import pathlib2
import json
import time
from src.tools.generate import *
template_root = pathlib2.Path(__file__).parent
template_path = template_root.joinpath('template.html')


def get_template_path(resources_path: str):
    '''
    获取资源目录
    '''
    return template_root.joinpath(resources_path)


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

    filename = PlaywrightRunner.with_timestamp(view_file_path)
    file = pathlib2.Path(bot_path.CACHE).joinpath(f'tpl_{filename}.html').as_posix()
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
    content_style = f'<style lang="scss">{content_style}</style>'
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
