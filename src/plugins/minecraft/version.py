from src.utils.network import Request

import re

async def get_be_version():  # Minecraft 基岩版 最新版本获取，数据来源@Mojira
    data = (await Request("https://bugs.mojang.com/rest/api/2/project/10200/versions").get()).json()
    beta = []
    preview = []
    release = []
    for v in data:
        if not v["archived"]:
            if re.match(r".*Beta$", v["name"]):
                beta.append(v["name"])
            elif re.match(r".*Preview$", v["name"]):
                preview.append(v["name"])
            else:
                if v["name"] != "Future Release":
                    release.append(v["name"])
    fix = " | "
    msg = f"Beta: {fix.join(beta)}\nPreview: {fix.join(preview)}\nRelease: {fix.join(release)}"
    return f"目前最新版本为：{msg}（数据来自Mojira，商店尚未更新属正常情况）"


async def get_je_version():  # Minecraft Java版最新版本获取
    data = (await Request("https://piston-meta.mojang.com/mc/game/version_manifest.json").get()).json()
    release = data["latest"]["release"]
    snapshot = data["latest"]["snapshot"]
    msg = f"最新版：{release}，最新快照：{snapshot}"
    mojira = (await Request("https://bugs.mojang.com/rest/api/2/project/10400/versions").get()).json()
    releases = []
    prefix = " | "
    for v in mojira:
        if not v["archived"]:
            releases.append(v["name"])
    msg_ = prefix.join(releases)
    return f"启动器内最新版本为：{msg}，Mojira上所记录最新版本为：{msg_}\n（Mojira版本号可能比启动器内稍早，请以启动器为准）"
