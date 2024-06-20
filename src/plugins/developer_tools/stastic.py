import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io
import numpy as np
import base64

from src.tools.basic import ASSETS

async def generate_bar_chart(data):
    categories = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots(figsize=(16, 10))

    bar_width = 0.6
    bar_positions = np.arange(len(categories))

    ax.bar(bar_positions, values, width=bar_width, color="blue")

    font_path = ASSETS + "/font/custom.ttf"
    prop = fm.FontProperties(fname=font_path)

    plt.rcParams["font.family"] = prop.get_name()

    ax.set_title("Inkar Suki 命令使用统计", fontproperties=prop, fontsize=16)
    ax.set_xlabel("类别", fontproperties=prop, fontsize=12)
    ax.set_ylabel("对数数量", fontproperties=prop, fontsize=12)

    ax.set_xticks(bar_positions)
    ax.set_xticklabels(categories, fontproperties=prop, rotation=90, ha="center")

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    image_bytes = buf.read()
    buf.close()

    return image_bytes

def preprocess_data(data):
    processed_data = {key: np.log10(value) for key, value in data.items()}
    return processed_data