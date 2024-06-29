from src.tools.basic import *

from pypub import AudioSegment

import aiofiles

def getRandomMusic():
    """
    随机获取一首歌。
    请将需要随机到的歌曲移动至`src/assets/music`中。
    """
    music_list = os.listdir(ASSETS + "/music")
    random_music = random.choice(music_list)
    final_path = ASSETS + "/music/" + random_music
    return random_music, final_path

async def extract_music(input_file, output_file, time):
    audio = AudioSegment.from_mp3(input_file)
    first_three_seconds = audio[:time*1000]
    async with aiofiles.open(output_file, "wb") as f:
        first_three_seconds.export(f, format="mp3")

