import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io
import numpy as np

from src.tools.basic import ASSETS

async def generate_bar_chart(data):
    data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))

    categories = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots(figsize=(10, 30))
    
    bar_height = 0.6
    spacing_factor = 1.5
    bar_positions = np.arange(len(categories)) * spacing_factor

    bars = ax.barh(bar_positions, values, height=bar_height, color=["blue", "green", "red", "purple"])

    font_path = ASSETS + "/font/custom.ttf"
    prop = fm.FontProperties(fname=font_path)

    plt.rcParams["font.family"] = prop.get_name()

    ax.set_title("Inkar Suki 命令使用统计", fontproperties=prop, fontsize=16)
    ax.set_ylabel("类别", fontproperties=prop, fontsize=12)
    ax.set_xlabel("数量", fontproperties=prop, fontsize=12)

    ax.set_yticks(bar_positions)
    ax.set_yticklabels(categories, fontproperties=prop, ha="right")  # 标签居中对齐

    for bar in bars:
        xval = bar.get_width()
        ax.text(xval + 0.1, bar.get_y() + bar.get_height() / 2, round(xval, 2), 
                ha="left", va="center", fontproperties=prop)

    plt.subplots_adjust(left=0.25)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    image_bytes = buf.read()
    buf.close()

    return image_bytes