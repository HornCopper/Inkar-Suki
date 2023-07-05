from src.tools.dep import *
from .SubscribeRegister import *
# 订阅 主题 订阅等级


__subjects: list[SubscribeSubject] = []
VALID_Subjects: dict[str, SubscribeSubject] = {}

load_subjects(__subjects, VALID_Subjects)
