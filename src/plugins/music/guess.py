from nonebot.log import logger

from src.tools.utils.path import ASSETS

import random
import asyncio
import os
import subprocess

def getRandomMusic():
    """
    随机获取一首歌。
    请将需要随机到的歌曲移动至`src/assets/music`中。
    """
    music_list = os.listdir(ASSETS + "/music/")
    random_music = random.choice(music_list)
    final_path = ASSETS + "/music/" + random_music
    return [random_music, final_path]

async def extract_music(input_file, output_file, time):
    ffmpeg_command = [
        "ffmpeg",
        "-i", input_file,
        "-t", str(time),
        "-c", "copy",
        output_file
    ]
    process = await asyncio.create_subprocess_exec(*ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        logger.info(f"Error occurred: {stderr.decode()}")
    else:
        logger.info(f"Extracted music successfully to {output_file}")
