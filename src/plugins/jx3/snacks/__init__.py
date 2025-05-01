from pathlib import Path
from jinja2 import Template

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg

from src.const.jx3.kungfu import Kungfu
from src.templates import HTMLSourceCode
from src.utils.generate import generate

from ._template import template_table, table_head

async def generate_snacks_image(season: str = "风语", *, data: dict[str, list[str]] = {}):
    tables = []
    for kungfu in data:
        image = Path(Kungfu(kungfu).icon).as_uri()
        values = [f"{season}·{snack}".replace("（", "<br>（") for snack in data[kungfu]]
        tables.append(
            Template(template_table).render(
                image = image,
                color = Kungfu(kungfu).color,
                values = values
            )
        )
    html = str(
        HTMLSourceCode(
            application_name=" · 小药",
            table_head = table_head,
            table_body = "\n".join(tables)
        )
    )
    return await generate(html, "table", segment=True)
    

school_snacks_matcher = on_command("小药", priority=5, force_whitespace=True)

@school_snacks_matcher.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    data = Kungfu.kungfu_snacks
    image = await generate_snacks_image(data=data)
    await school_snacks_matcher.finish(image)