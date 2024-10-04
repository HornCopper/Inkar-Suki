from nonebot import on_message
from nonebot.message import run_preprocessor, run_postprocessor

message_universal = on_message(priority=0, block=False)

pre_process = run_preprocessor

post_process = run_postprocessor