from .CommandStorage import *
from typing import overload


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
        cur_map = self.mapper
        # print(json.dumps(mapper, indent=4, ensure_ascii=False))
        def extract_result(result: str, idx: int) -> str:
            cmds = result.split(self.FLAG_Spliter)
            results = cmds + raw_commands[idx+1:]  # 映射命令后参数不变动

            results = [
                (
                    raw_commands[int(x[1:])]  # 是参数则填充
                    if x.startswith(CommandMapperStorage.FLAG_Args)
                    else x
                )
                for x in results
            ]
            export = str.join(' ', results)
            if commands == export:
                return commands if isinstance(commands, str) else str.join(' ', commands)
            if max_depth <= 0:
                return export
            return self.convert(results, max_depth-1)

        for cur_idx, cur_cmd in enumerate(raw_commands):
            # 获取当前位是否可为参数
            if args := cur_map.get(self.FLAG_Args):
                # 可为参数则跟进参数，直接短路
                cur_map = args
                continue

            cur_map = cur_map.get(cur_cmd)
            if cur_map is None:
                # 无匹配，直接返回原始传入
                return commands if isinstance(commands, str) else str.join(' ', commands)

            if result := cur_map.get(self.FLAG_Value):
                # 有设置值则
                return extract_result(result, cur_idx)


        if result := cur_map.get(self.FLAG_Value):
            # 有设置值则
            return extract_result(result, cur_idx)
        # 无任何匹配
        return commands
