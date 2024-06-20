import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io
import numpy as np

from src.tools.basic import ASSETS

async def generate_bar_chart(data):
    categories = list(data.keys())
    values = list(data.values())

    plt.figure(figsize=(16, 10))
    plt.bar(categories, values, color=["blue", "green", "red", "purple"])

    font_path = ASSETS + "/font/custom.ttf"
    prop = fm.FontProperties(fname=font_path)

    plt.rcParams["font.family"] = prop.get_name()

    plt.title("Inkar Suki 命令使用统计", fontproperties=prop, fontsize=16)
    plt.xlabel("类别", fontproperties=prop, fontsize=12)
    plt.ylabel("数量", fontproperties=prop, fontsize=12)

    plt.xticks(fontproperties=prop)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)

    image_bytes = buf.read()
    buf.close()

    return image_bytes

def preprocess_data(data):
    processed_data = {key: np.log10(value) for key, value in data.items()}
    return processed_data