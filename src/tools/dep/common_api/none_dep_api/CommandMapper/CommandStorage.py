import re
import threading


class CommandMapperStorage:
    pattern = re.compile(r'\$(\d+)')  # 匹配参数占位符，例如 $1、$2 等
    FLAG_Spliter = '-'
    FLAG_Value = f'{FLAG_Spliter}value'
    FLAG_Args = '$'

    cache: dict[int, dict] = {}
    lock = threading.Lock()

    def __init__(self, mapper: dict) -> None:
        self._mapper = mapper

    def generate(self):
        result = {}
        raw_mapper = self._mapper
        path_lib = {}  # 记录选择器的路径以同质化参数
        for m in raw_mapper:
            cmds = m.split(CommandMapperStorage.FLAG_Spliter)
            cur_map = result

            for idx, cmd in enumerate(cmds):
                if next_map := cur_map.get(cmd):
                    cur_map = next_map
                    continue

                # 命令允许参数
                if cmd.startswith(CommandMapperStorage.FLAG_Args):
                    cmd_name = cmd[1:]
                    # 记录该路径参数名称
                    path_lib[cmd_name] = idx
                    cmd = CommandMapperStorage.FLAG_Args

                    if next_map := cur_map.get(cmd):
                        # 参数已存在
                        cur_map = next_map
                        continue

                new_map = {}  # 不存在，则创建新的。
                cur_map[cmd] = new_map  # 存如当前层
                cur_map = new_map

            value = raw_mapper[m]
            # 按参数长度降序以防止歧义
            ordered_path = sorted(list(path_lib), key=lambda x: -len(x))
            for path in ordered_path:
                cmd_idx = path_lib[path]
                value = value.replace(f'{CommandMapperStorage.FLAG_Args}{path}',
                                      f'{CommandMapperStorage.FLAG_Args}{cmd_idx}')
            cur_map[CommandMapperStorage.FLAG_Value] = value
        return result

    @property
    def mapper(self) -> dict[str, dict]:
        with CommandMapperStorage.lock:
            mid = id(self._mapper)
            if prev := CommandMapperStorage.cache.get(mid):
                return prev
            prev = self.generate()
            CommandMapperStorage.cache[mid] = prev
            return prev
