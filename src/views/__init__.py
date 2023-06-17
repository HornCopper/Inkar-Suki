import asyncio
import json
import pathlib2
import nonebot
from src.tools.generate import get_uuid, generate
TOOLS = nonebot.get_driver().config.tools_path
CACHE = pathlib2.Path(TOOLS).parent.joinpath('cache')
template_path = pathlib2.Path(__file__).parent.joinpath('template.html')


def get_tag_content(data: str, tag: str) -> str:
    tag_start = f'<{tag}>'
    tag_end = f'</{tag}>'
    tags = data.split(tag_start)
    result = []
    for t in tags[1:]:
        x = t.split(tag_end)
        result.append(x[0])
    return '\n'.join(result)


def get_render_image(view_file_path: str, data: dict = None, delay: int = 0, target: str = 'section') -> bytes:
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
    return asyncio.run(generate(file, delay=delay, locate=target))


def __init_data(data: dict):
    '''覆盖原始data
    '''
    template = '''const _raw_setup = component.setup
    component.setup = () => {
      const data = {{data}}
      const result = Object.assign({}, _raw_setup())
      v_result = Object.assign(result, data)
      return v_result
    }
    Vue.createApp(component).mount('#app')'''.replace('{{data}}', json.dumps(data))
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
    content = content.replace('<template />', content_template)

    # 注入脚本
    content_script = get_tag_content(view_content, 'script')
    content_script += __init_data(data)
    content = content.replace('<component />', content_script)

    # 加载所有脚本文件
    script_src = view_content.split('<script src="')
    script_src = [x for index, x in enumerate(script_src) if index % 2]
    script_src = [x.split('"') for x in script_src]
    script_src = [x[0] for x in script_src if len(x) > 1]
    script_src = [f'<script src="{x}" ></script>' for x in script_src]
    content_src = "\n".join(script_src)
    content = content.replace('<script_files />', content_src)

    return content
