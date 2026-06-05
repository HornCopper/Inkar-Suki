from pathlib import Path
from typing import Any
import ast
import html

from nonebot import on_regex, on_command
from nonebot.params import CommandArg, RawCommand
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    GroupMessageEvent,
    MessageSegment as ms
)

from src.config import Config
from src.const.path import (
    ASSETS,
    PLUGINS,
    build_path
)
from src.utils.network import Request
from src.utils.generate import generate
from src.utils.analyze import check_number
from src.utils.time import Time
from src.utils.database import cache_db
from src.utils.database.classes import BanRecord
from src.utils.database.operation import get_group_settings

import random
import os

from ._message import answers as a

What2EatMatcher = on_regex(r"^(/)?[今|明|后]?[天|日]?(早|中|晚)?(上|午|餐|饭|夜宵|宵夜)?吃(什么|啥|点啥)$", priority=5)
What2DrinkMatcher = on_regex(r"^(/)?[今|明|后]?[天|日]?(早|中|晚)?(上|午|餐|饭|夜宵|宵夜)?喝(什么|啥|点啥)$", priority=5)

HELP_COMMAND_KEYWORDS = ("help", "帮助", "支持", "文档", "使用说明", "功能")
HELP_ARGUMENT_KEYWORDS = ("help", "帮助", "参数", "示例")


def _literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _literal_strings(node: ast.AST) -> list[str]:
    value = _literal_string(node)
    if value is not None:
        return [value]
    if isinstance(node, (ast.Set, ast.List, ast.Tuple)):
        results: list[str] = []
        for element in node.elts:
            results.extend(_literal_strings(element))
        return results
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_prefixed_command_aliases"
        and node.args
    ):
        value = _literal_string(node.args[0])
        return [value] if value is not None else []
    return []


def _is_on_command_call(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "on_command"


def _decorator_matcher_name(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
        return None
    if node.func.attr not in {"handle", "got"}:
        return None
    value = node.func.value
    return value.id if isinstance(value, ast.Name) else None


def _called_function_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
            names.add(child.func.id)
    return names


def _node_string_values(node: ast.AST) -> set[str]:
    values: set[str] = set()
    for child in ast.walk(node):
        value = _literal_string(child)
        if value is not None:
            values.add(value)
    return values


def _node_names(node: ast.AST) -> set[str]:
    return {child.id for child in ast.walk(node) if isinstance(child, ast.Name)}


def _has_help_argument_trigger(node: ast.AST) -> bool:
    values = _node_string_values(node)
    lower_values = {value.lower() for value in values}
    if "help" in lower_values and any(keyword in values for keyword in HELP_ARGUMENT_KEYWORDS[1:]):
        return True
    return any(name.endswith("HELP_TEXT") for name in _node_names(node))


def _extract_command_matchers(tree: ast.AST) -> dict[str, dict[str, Any]]:
    matchers: dict[str, dict[str, Any]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not _is_on_command_call(node.value):
            continue
        matcher_names = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if not matcher_names:
            continue
        command = _literal_string(node.value.args[0]) if node.value.args else None
        if command is None:
            continue
        aliases: list[str] = []
        for keyword in node.value.keywords:
            if keyword.arg == "aliases":
                aliases = _literal_strings(keyword.value)
                break
        for matcher_name in matcher_names:
            matchers[matcher_name] = {"command": command, "aliases": aliases}
    return matchers


def _extract_help_matcher_names(tree: ast.AST) -> set[str]:
    functions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    helper_by_name = {
        node.name: node
        for node in functions
        if node.name != "_"
    }
    help_helpers = {
        name
        for name, node in helper_by_name.items()
        if _has_help_argument_trigger(node)
    }
    help_matchers: set[str] = set()
    for function in functions:
        matcher_names = [
            matcher_name
            for decorator in function.decorator_list
            if (matcher_name := _decorator_matcher_name(decorator)) is not None
        ]
        if not matcher_names:
            continue
        has_help = _has_help_argument_trigger(function)
        if not has_help:
            has_help = bool(_called_function_names(function) & help_helpers)
        if has_help:
            help_matchers.update(matcher_names)
    return help_matchers


def _is_internal_command(command: str) -> bool:
    return command.startswith("jx3_") or bool(command) and command.replace("_", "").isascii() and command.islower()


def _display_command(command: str, aliases: list[str]) -> str:
    if command == "inkar":
        return command
    for candidate in aliases:
        if not _is_internal_command(candidate):
            return candidate
    return command


def _help_category(path: Path, entry_type: str) -> str:
    if any(part == "jx3" for part in path.parts):
        return "剑三功能"
    if entry_type == "argument":
        return "参数帮助"
    if any(part == "fun" for part in path.parts):
        return "通用帮助"
    return "其他帮助"


def _collect_inkar_help_entries() -> list[dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for source_path in Path(PLUGINS).rglob("*.py"):
        try:
            source = source_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception:
            continue
        matchers = _extract_command_matchers(tree)
        help_matchers = _extract_help_matcher_names(tree)
        for matcher_name, matcher_data in matchers.items():
            command = matcher_data["command"]
            aliases = matcher_data["aliases"]
            visible_commands = [command, *aliases]
            keyword_commands = [
                item for item in visible_commands if item != command or not _is_internal_command(item)
            ]
            is_help_command = any(
                any(keyword.lower() in item.lower() for keyword in HELP_COMMAND_KEYWORDS)
                for item in keyword_commands
            )
            is_argument_help = matcher_name in help_matchers and not is_help_command
            if not is_help_command and not is_argument_help:
                continue
            display = _display_command(command, aliases)
            if is_argument_help:
                display = f"{display} help"
            alias_text = " / ".join(
                item for item in visible_commands if item != command or not _is_internal_command(item)
            )
            key = display.lower()
            entries[key] = {
                "command": display,
                "aliases": alias_text or display,
                "category": _help_category(source_path.relative_to(PLUGINS), "argument" if is_argument_help else "command"),
            }
    return sorted(entries.values(), key=lambda item: (item["category"], item["command"]))


async def _render_inkar_help_image():
    entries = _collect_inkar_help_entries()
    category_order = ["通用帮助", "剑三功能", "参数帮助", "其他帮助"]
    grouped_entries = {
        category: [entry for entry in entries if entry["category"] == category]
        for category in category_order
    }
    cards = []
    for category in category_order:
        items = grouped_entries.get(category) or []
        if not items:
            continue
        item_html = []
        for entry in items:
            item_html.append(
                '<div class="help-item">'
                f'<div class="cmd">{html.escape(entry["command"])}</div>'
                f'<div class="aliases">{html.escape(entry["aliases"])}</div>'
                '</div>'
            )
        cards.append(
            '<section class="section">'
            f'<div class="section-title">{html.escape(category)} <span>{len(items)}</span></div>'
            f'<div class="grid">{"".join(item_html)}</div>'
            '</section>'
        )
    html_source = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ margin: 0; background: #edf1f7; font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif; color: #202638; }}
.page {{ width: 980px; box-sizing: border-box; padding: 34px; background: #f7f9fc; }}
.header {{ padding: 30px 32px; background: #243149; color: #fff; border-radius: 8px; }}
.eyebrow {{ color: #b9c7dc; font-size: 18px; font-weight: 800; }}
.title {{ margin-top: 8px; font-size: 38px; line-height: 1.2; font-weight: 900; }}
.subtitle {{ margin-top: 12px; color: #d8e0ed; font-size: 18px; line-height: 1.6; }}
.section {{ margin-top: 18px; background: #fff; border: 1px solid #e0e5ef; border-radius: 8px; padding: 22px; }}
.section-title {{ display: flex; justify-content: space-between; align-items: center; font-size: 24px; font-weight: 900; color: #1f2937; margin-bottom: 14px; }}
.section-title span {{ color: #647084; font-size: 16px; font-weight: 800; }}
.grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }}
.help-item {{ border: 1px solid #dde5f1; border-radius: 8px; background: #f8fafd; padding: 14px; min-height: 92px; }}
.cmd {{ color: #1f57d6; font-size: 20px; font-weight: 900; line-height: 1.35; }}
.aliases {{ margin-top: 8px; color: #344054; font-size: 15px; line-height: 1.5; word-break: break-word; }}
.note {{ margin-top: 18px; color: #687386; font-size: 15px; line-height: 1.55; text-align: right; }}
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <div class="eyebrow">inkar help</div>
    <div class="title">音卡帮助指令索引</div>
    <div class="subtitle">汇总音卡当前可用的帮助、支持和参数说明入口。</div>
  </div>
  {"".join(cards) if cards else '<section class="section">暂无可展示的 help 指令。</section>'}
  <div class="note">触发方式：inkar help</div>
</div>
</body>
</html>
"""
    return await generate(
        html_source,
        ".page",
        False,
        segment=True,
        viewport={"width": 1040, "height": 1800},
    )

@What2DrinkMatcher.handle()
async def _(event: MessageEvent):
    image_name = random.choice(os.listdir(
        build_path(
            ASSETS,
            [
                "image",
                "what2eat",
                "drink"
            ]
        )
    ))
    image_path = Path( 
        build_path(
            ASSETS,
            [
                "image",
                "what2eat",
                "drink"
            ],
            end_with_slash=True
        ) + image_name
    )
    msg = (f"{Config.bot_basic.bot_name}建议你喝: \n⭐{image_path.stem}⭐\n" + ms.image(Request(image_path.as_uri()).local_content))
    await What2DrinkMatcher.send("正在为你找好喝的……")
    await What2DrinkMatcher.send(msg, at_sender=True)

@What2EatMatcher.handle()
async def _(event: MessageEvent):
    image_name = random.choice(os.listdir(
        build_path(
            ASSETS,
            [
                "image",
                "what2eat",
                "eat"
            ]
        )
    ))
    image_path = Path( 
        build_path(
            ASSETS,
            [
                "image",
                "what2eat",
                "eat"
            ],
            end_with_slash=True
        ) + image_name
    )
    msg = (f"{Config.bot_basic.bot_name}建议你吃: \n⭐{image_path.stem}⭐\n" + ms.image(Request(image_path.as_uri()).local_content))
    await What2EatMatcher.send("正在为你找好吃的……")
    await What2EatMatcher.send(msg, at_sender=True)

BMIMatcher = on_command("bmi", aliases={"BMI", "身体质量指数"}, force_whitespace=True, priority=5)

@BMIMatcher.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await BMIMatcher.finish("唔……参数数量不正确哦，请参考以下格式，注意两个参数都是纯数字哦~\nBMI 身高(米) 体重(千克)")
    for i in arg:
        if not check_number(i):
            await BMIMatcher.finish("唔……请参考以下格式，注意两个参数都是纯数字哦~\nBMI 身高(米) 体重(千克)")
    height = float(arg[0])
    weight = float(arg[1])
    bmi_value = weight / (height*height)
    final_result = round(bmi_value, 1)
    if final_result <= 18.4:
        msg = f"您的BMI计算结果是：{final_result}，属于偏瘦（0~18.4）哦~"
    elif 18.5 <= final_result <= 23.9:
        msg = f"您的BMI计算结果是：{final_result}，属于正常（18.5~23.9）哦~"
    elif 24.0 <= final_result <= 27.9:
        msg = f"您的BMI计算结果是：{final_result}，属于偏胖（24.0~27.9）哦~"
    elif final_result >= 28.0:
        msg = f"您的BMI计算结果是：{final_result}，属于肥胖（28.0+）哦~\n音卡建议您少吃高热量食物，多多运动保持健康身体哦！"
    await BMIMatcher.finish(msg)

HelpMatcher = on_command("help", aliases={"帮助", "功能", "查看", "文档", "使用说明"}, force_whitespace=True, priority=5)
InkarHelpMatcher = on_command("inkar", aliases={"Inkar", "INKAR", "音卡"}, force_whitespace=True, priority=5)

@HelpMatcher.handle()
async def help_(args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    await HelpMatcher.finish("Inkar Suki · 音卡使用文档：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/usage")


@InkarHelpMatcher.handle()
async def _(args: Message = CommandArg()):
    query = args.extract_plain_text().strip().lower()
    if query not in {"help", "帮助"}:
        await InkarHelpMatcher.finish("参考格式：inkar help")
    await InkarHelpMatcher.finish(await _render_inkar_help_image())


RandomDogImageMatcher = on_command("随机狗图", aliases={"随机lwx"}, priority=5)

@RandomDogImageMatcher.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    rdint = random.randint(1, 100)
    if event.user_id in [1649157526, 1925648680]:
        if rdint >= 31:
            img = Request(
                Path(
                    build_path(
                        ASSETS,
                        [
                            "image",
                            "lwx"
                        ]
                        ,
                        end_with_slash=True
                    ) + str(random.randint(1,4)) + ".jpg"
                ).as_uri()
            ).local_content
            await RandomDogImageMatcher.finish(ms.image(img))
    if rdint <= 10:
        img = Request(
            Path(
                build_path(
                    ASSETS,
                    [
                        "image",
                        "lwx"
                    ]
                    ,
                    end_with_slash=True
                ) + str(random.randint(1,4)) + ".jpg"
            ).as_uri()
        ).local_content
        await RandomDogImageMatcher.finish(ms.image(img))
    data = (await Request("https://api.thedogapi.com/v1/images/search?size=full").get()).json()
    image = (await Request(data[0]["url"]).get()).content
    await RandomDogImageMatcher.finish(ms.image(image))

RandomDragonImageMatcher = on_command("随机龙图", priority=5)

@RandomDragonImageMatcher.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    batch_choice = random.choice(["batch1/", "batch2/", "batch3/"])
    base_url = "https://git.acwing.com/Est/dragon/-/raw/main/"
    rdnum = random.randint(
        (
            int(batch_choice[-2])
            -1
        )*500+1,
        (
            int(batch_choice[-2])
            *500
        )
            )
    for ext in [".jpg", ".png", ".gif"]:
        image_url = f"{base_url}{batch_choice}dragon_{rdnum}_{ext}"
        resp = await Request(image_url).get()
        if resp.status_code == 200:
            image = resp.content
            await RandomDragonImageMatcher.finish(ms.image(image))

AnswerBookMatcher = on_command("答案之书", priority=5, force_whitespace=True)

@AnswerBookMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    else:
        answer = random.choice(a)
        await AnswerBookMatcher.finish("答案之书给出的建议是：\n" + answer)

CustomBanMatcher = on_command("抽奖", aliases={"抽大奖", "十连抽", "百连抽", "抽巨奖"}, priority=5)

@CustomBanMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, cmd: str = RawCommand(), args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    additions = get_group_settings(event.group_id, "additions")
    self_role = await bot.get_group_member_info(group_id=event.group_id, user_id=event.self_id)
    terminal_role = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
    if "抽奖" not in additions:
        await CustomBanMatcher.finish("本群尚未启用抽奖！\n发送“订阅 抽奖”即可启用。包含以下命令：\n抽奖、抽大奖、十连抽、百连抽")
    if self_role["role"] not in ["owner", "admin"] or terminal_role["role"] in ["owner", "admin"]:
        await CustomBanMatcher.finish("音卡的权限似乎不对？请检查音卡是否为管理员，自身是否为非管理员？")
    max_time = {
        "抽奖": 15,
        "抽大奖": 60,
        "十连抽": 150,
        "百连抽": 1500,
        "抽巨奖": 43200
    }
    reward_time = random.randint(0, max_time[cmd])
    await bot.send_group_msg(group_id=event.group_id, message=f"恭喜你{cmd}的奖励时长：{reward_time}分钟！")
    cache_db.save(
        BanRecord(
            user_id = event.user_id,
            group_id = event.group_id,
            expire = Time().raw_time + reward_time * 60
        )
    )
    await bot.set_group_ban(group_id=event.group_id, user_id=event.user_id, duration=reward_time*60)

AllLiftBanMatcher = on_command("大赦天下", priority=5, force_whitespace=True)

@AllLiftBanMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    terminal_role = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
    if terminal_role["role"] not in ["owner", "admin"]:
        await AllLiftBanMatcher.finish("只有群主或管理员才可以大赦天下！")
    ban_record: list[BanRecord] | Any = cache_db.where_all(BanRecord(), "group_id = ?", str(event.group_id), default=[])
    if not ban_record:
        await AllLiftBanMatcher.finish("当前没有抽奖人员处于禁言状态！")
    else:
        unban_persons: list[int] = [b.user_id for b in ban_record]
        for p in unban_persons:
            await bot.set_group_ban(group_id=event.group_id, user_id=p, duration=0)
        cache_db.delete(BanRecord(), "group_id = ?", str(event.group_id))
        await AllLiftBanMatcher.finish("已解除所有抽奖的禁言！")
