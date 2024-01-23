from .CommandStorage import *
from typing import overload
from sgtpyutils.logger import logger


class CommandMapper(CommandMapperStorage):
    '''
    实现命令行映射功能
    (1) 创建映射后，改变用户输入的命令行为。
    例如：
    映射  查询  查询天气
    查询 北京 == 查询天气 北京

    映射 看一看 查询
    看一看 北京 == 查询天气 北京

    (2) 映射支持映射参数
    例如：
    映射 查询 查询天气-明天
    查询 北京 == 查询天气 明天 北京

    (3) 映射支持任意位置的参数
    例如
    映射 查询-明天-$1 查询-$1-明天
    查询 明天 北京 == 查询 北京 明天

    映射 打招呼-$1-小狗 打招呼-小狗-$1
    打招呼 你好 小狗 == 打招呼 小狗 你好
    打招呼 你好 小狗 2024-01-22 == 打招呼 小狗 你好 2024-01-22
    '''

    def __init__(self, mapper: dict):
        super().__init__(mapper)

    @overload
    def convert(self, commands: str) -> str:
        ...

    @overload
    def convert(self, commands: list[str]) -> str:
        ...

    def convert(self, commands: list[str], max_depth: int = 10) -> str:
        raw_commands = commands if isinstance(commands, list) else commands.split(' ')
        # print(json.dumps(mapper, indent=4, ensure_ascii=False))

        def get_single_arg(x: str):
            if not x.startswith(CommandMapperStorage.FLAG_Args):
                return x
            total_commands = len(raw_commands)
            require_idx = int(x[1:])
            # 不对，这里的2是因为在Storage中初始化的锅 # require_idx -= 1 # 应排除命令本身的1个身位
            if require_idx >= total_commands:
                logger.warning(f'require args{require_idx},but only {total_commands} args available')
                return ''
            return raw_commands[require_idx]

        def extract_result(result: str, idx: int) -> str:
            logger.debug(f'cmd-mapper extract_result[{idx}] :{result}')
            cmds = result.split(self.FLAG_Spliter)
            results = cmds + raw_commands[idx+1:]  # 映射命令后参数不变动

            results = [get_single_arg(x) for x in results]
            results = [x for x in results if x]
            export = str.join(' ', results)
            if commands == export:
                return commands if isinstance(commands, str) else str.join(' ', commands)
            if max_depth <= 0:
                return export
            return self.convert(results, max_depth-1)

        cur_idx = -1
        cur_map = self.mapper
        while True:
            cur_idx += 1
            cur_cmd = raw_commands[cur_idx] if len(raw_commands) > cur_idx else ''
            # 获取当前位是否可为参数
            if args := cur_map.get(self.FLAG_Args):
                # 可为参数则跟进参数，直接短路
                cur_map = args
                continue

            if next_val := cur_map.get(cur_cmd):
                cur_map = next_val
            elif result := cur_map.get(self.FLAG_Value):
                # 已无法继续向下匹配，则将当前作为其他参数注入，idx-1
                return extract_result(result, cur_idx-1)
            else:
                # 无匹配，直接返回原始传入
                return commands if isinstance(commands, str) else str.join(' ', commands)
