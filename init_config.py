import sys
import os
import re
from sgtpyutils.logger import logger
from sgtpyutils.encode.basexx import base64_decode


def get_from_encoded(raw: str) -> str:
    try:
        return base64_decode(raw).decode('utf-8')
    except:
        return None


class ArgumentInfo:
    __index: int = 0

    def __init__(self, name: str, default_value: str = None, initial_value: str = None, enable: bool = True, desc: str = None) -> None:
        self.index = ArgumentInfo.__index
        ArgumentInfo.__index += 1

        self.name = name
        self.initial_value = initial_value
        self.default_value = default_value
        self.enable = enable
        self.desc = desc

    @property
    def value(self) -> str:
        return self.initial_value if self.initial_value is not None else self.default_value

    def replace_from_template(self, template: str) -> str:
        """
        将template中参数替换为实际值
        """
        if not self.enable:
            return template
        # 以空格或\t开头的变量赋值内容
        pattern = re.compile(f'[ |\t]({self.name})[ ]*=[ ]*"(\w*)"')
        result = pattern.search(template)
        if result is None:
            logger.warn(f'argument "{self.name}" not found in template.')
            return template  # 失配 警告并返回
        pos_span = result.span()
        pos_start = pos_span[0] + 1  # 取消第一个空格
        pos_end = pos_span[1]
        target_str = template[pos_start:pos_end]
        new_value = self.value if self.value is not None else "None"
        evaluate_str = f"{self.name} = {new_value}"
        logger.info(f'replace "{target_str}" to "******"')
        return f'{template[:pos_start]}{evaluate_str}{template[pos_end:]}'

    @value.setter
    def value(self, val: str):
        self.initial_value = val

    def __repr__(self) -> str:
        return f'{self.name}:{self.value}'


def get_config_path() -> tuple[str, str]:
    target_path = f'src{os.sep}tools{os.sep}'
    target_src_config = f'{target_path}config.sample.py'
    target_config = f'{target_path}config.py'
    return (target_src_config, target_config)


DEFAULT_expected_args: list[ArgumentInfo] = [
    ArgumentInfo("runner", enable=False, desc="程序启动路径"),
    ArgumentInfo("proxy", desc="全局使用的代理"),
    ArgumentInfo("jx3_token", desc="推栏token"),
    ArgumentInfo("jx3api_link", desc="jx3api的api地址"),
    ArgumentInfo("jx3api_globaltoken", desc="jx3api的token"),
    ArgumentInfo("jx3api_wslink", desc="jx3api的ws地址"),
    ArgumentInfo("jx3api_wstoken", desc="jx3api的wstoken"),
    ArgumentInfo("sfapi_wslink", desc="sfapi的ws地址"),
    ArgumentInfo("sfapi_wstoken", desc="sfapi的wstoken"),
]


def init_arguments(args: list[str], template: list[ArgumentInfo] = None) -> list[ArgumentInfo]:
    if template is None:
        template = DEFAULT_expected_args
    for index, arg in enumerate(args):
        template[index].value = get_from_encoded(arg)
    return template


def replace_arguments(data: str, arguments: list[ArgumentInfo]) -> str:
    for arg in arguments:
        data = arg.replace_from_template(data)
    return data


def export_args_to_config(arguments: list[ArgumentInfo]):
    target_src_config, target_config = get_config_path()
    with open(target_src_config, 'r', encoding='utf-8') as f:
        data = f.read()
        data = replace_arguments(data, arguments)

    with open(target_config, 'w', encoding='utf-8') as f:
        f.write(data)


def get_user_input() -> list[str]:
    argv = sys.argv
    expected_args_count = len(DEFAULT_expected_args)
    if len(argv) < expected_args_count:
        params = [None] * expected_args_count
    else:
        params = sys.argv
    return params


if __name__ == '__main__':
    params = get_user_input()
    arguments = init_arguments(params)
    export_args_to_config(arguments)
