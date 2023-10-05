from playwright.async_api import async_playwright

from src.tools.dep import *
from src.plugins.jx3.recruit.api import VIEWS

def javascript(server, name):
    js = """
    // OA神的JavaScript代码 XD
    async () =>{
        let a = await window.grecaptcha.execute(window.xconfig.extend.reCaptchaToken)
        let b = await fetch('https://www.jx3pet.com/api/firework?server=$server&name=$name&response=' + a)
        return b.json()}    
    """
    return js.replace("$server", server).replace("$name", name)

async def get_firework_data(server, name):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless = True, slow_mo = 900)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.jx3pet.com/firework")
        info = await page.evaluate(javascript(server, name))
        return info

template = """
<tr>
    <td class="short-column">$count</td>
    <td class="short-column">$map</td>
    <td class="short-column">$sed</td>
    <td class="short-column">$rec</td>
    <td class="short-column">$time</td>
    <td class="short-column">$firework</td>
</tr>
"""

async def get_firework_image(server, name, group):
    server = server_mapping(server, group)
    if not server:
        return [PROMPT_ServerNotExist]
    data = await get_firework_data(server, name)
    tablecontent = []
    data = data["data"]
    for i in range(len(data)):
        tablecontent.append(template.replace("$count", str(i)).replace("$map", data[i]["map_name"]).replace("$sed", data[i]["sender"]).replace("$rec", data[i]["recipient"]).replace("$time", convert_time(data[i]["time"])).replace("$firework", data[i]["name"]))
    tablecontents = "\n".join(tablecontent)
    html = read(VIEWS + "/jx3/firework/firework.html")
    saohua = await get_api(f"https://www.jx3api.com/data/saohua/random?token={token}")
    saohua = saohua["data"]["text"]
    appinfo_time = time.strftime("%H:%M:%S",time.localtime(time.time()))
    appinfo = f"烟花记录 · {server} · {name} · 当前时间：{appinfo_time}"
    font = ASSETS + "/font/custom.ttf"
    html = html.replace("$customfont", font).replace("$appinfo", appinfo).replace("$tablecontent", tablecontents).replace("$randomsaohua", saohua)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()