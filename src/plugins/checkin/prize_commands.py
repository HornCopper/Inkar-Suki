import shlex
from html import escape
from jinja2 import Template

from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from nonebot.params import CommandArg

from src.accounts.prize_pool import (
    POOL_PERMISSION,
    PrizePoolManage,
    format_probability,
    parse_probability,
)
from src.utils.command import on_command
from src.utils.database import db
from src.utils.database.classes import CheckinPrize, CheckinPrizeAward
from src.utils.permission import check_permission, denied
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import HTMLSourceCode

from ._template import (
    backpack_table_head,
    backpack_row,
    backpack_css,
    pending_prize_table_head,
    pending_prize_row,
)

POOL_HELP = """签到奖池：每次成功签到最多抽中一件奖品，概率独立于原签到金币奖励。
查看：签到奖池 [页码]
投放：签到奖池 投放 <名称> <概率%> <数量|不限量>
绑定权限：签到奖池 权限 <奖品编号> <群权限|个人权限> <权限节点>
取消绑定：签到奖池 权限 <奖品编号> 取消
调整：签到奖池 概率 <奖品编号> <概率%>
补货：签到奖池 补货 <奖品编号> <数量>
上下架：签到奖池 <上架|下架|删除> <奖品编号>
中奖记录：签到奖池 记录 <QQ号> [页码]
未兑奖记录：签到奖池 未兑奖 <奖品编号> [页码]
标记兑付：签到奖池 兑付 <背包记录编号>
自助兑奖：兑奖 <背包记录编号>，或 签到奖池 兑奖 <背包记录编号>
我的奖品：背包 [页码]
清空全部背包（仅 Bot 主人）：签到奖池 清空背包
例如：签到奖池 投放 "纪念徽章" 5% 10
例如：签到奖池 投放 "角色名片使用权" 5% 10
例如：签到奖池 权限 1 群权限 group.application.role_card
上架总概率不超过100%；耗尽后不再抽取，其他奖品概率保持不变。
奖池全局共享；管理操作需要 economy.checkin.pool.manage 权限。
投放人可为自己的奖品绑定权限，Bot 主人可管理全部奖品；绑定或取消只对后续中奖生效。
仅权限奖品支持自助兑奖；个人权限授予本人，群权限需在目标群内兑奖。
已拥有或被拒绝的权限不会消耗奖品；普通奖品由投放人安排发放，兑付命令仅记录状态。
清空背包会删除所有人的已兑付和未兑付记录；奖池、库存及已授予的权限保留。"""
PAGE_SIZE = 10

def positive_number(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise ValueError("编号、QQ号、数量和页码需要是正整数。") from None
    if number <= 0 or number > 9_223_372_036_854_775_807:
        raise ValueError("编号、QQ号、数量和页码需要是有效的正整数。")
    return number

def page_bounds(total: int, page: int) -> tuple[int, int]:
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    if not 1 <= page <= pages:
        raise ValueError(f"页码超出范围，共 {pages} 页。")
    return pages, (page - 1) * PAGE_SIZE

def pool_listing(page: int) -> str:
    total = db.fetch_all("SELECT COUNT(*) FROM checkin_prizes")[0][0]
    pages, offset = page_bounds(total, page)
    entries = db.where_all(
        CheckinPrize(),
        "1=1 ORDER BY id LIMIT ? OFFSET ?",
        PAGE_SIZE,
        offset,
        default = [],
    )
    lines = [f"签到奖池（{page}/{pages}页）"]
    for entry in entries:
        stock = "不限量" if entry.remaining == -1 else f"剩余 {entry.remaining} 件"
        state = "下架" if not entry.enabled else "已耗尽" if entry.remaining == 0 else "上架"
        lines.append(f"#{entry.id} {entry.name}｜{format_probability(entry.probability)}｜{stock}｜{state}")
    if not entries:
        lines.append("奖池暂时为空，原有签到奖励照常发放。")
    lines.append("发送「签到奖池 帮助」查看规则和投放方式。")
    return "\n".join(lines)

def backpack_listing(user_id: int, page: int) -> str:
    """生成背包报告 HTML，个人查询和管理员查看共用同一界面。"""
    total, pending = db.fetch_all(
        "SELECT COUNT(*), COALESCE(SUM(delivered_at = 0), 0) FROM checkin_prize_awards WHERE user_id = ?",
        user_id,
    )[0]
    pages, offset = page_bounds(total, page)
    awards = db.where_all(
        CheckinPrizeAward(),
        "user_id = ? ORDER BY id DESC LIMIT ? OFFSET ?",
        user_id,
        PAGE_SIZE,
        offset,
        default = [],
    )
    row_template = Template(backpack_row, autoescape = True)
    rows = [
        row_template.render(
            prize_name = award.prize_name,
            award_id = award.id,
            provider_id = award.provider_id,
            awarded_at = Time(award.awarded_at).format("%Y-%m-%d %H:%M"),
            delivered_at = Time(award.delivered_at).format("%Y-%m-%d %H:%M") if award.delivered_at else "",
            permission_scope = award.permission_scope,
            delivered_target = award.delivered_target,
        ) for award in awards
    ]
    if not awards:
        rows.append(
            """<tr><td colspan="5" class="backpack-empty">
            <p class="backpack-empty-title">背包暂时为空</p>
            <p class="backpack-empty-hint">每天签到，有机会获得奖池奖品。</p>
        </td></tr>""",
        )
    return str(
        HTMLSourceCode(
            application_name = f"背包 · QQ {user_id} · 累计 {total} 件 / 待兑付 {pending} 件 / 已兑付 {total - pending} 件",
            table_head = backpack_table_head,
            table_body = "\n".join(rows),
            additional_css = backpack_css,
            footer = (
                f"第 {page}/{pages} 页 · 每页 {PAGE_SIZE} 件 · 权限奖品发送「兑奖 记录编号」领取，群权限需在目标群内兑奖。"
                "普通奖品请联系投放人，兑付后保留记录。"
            ),
        ),
    )

def pending_prize_listing(prize_id: int, page: int) -> str:
    """列出同一个投放奖品的全部待兑付记录，奖品删除后仍可查询。"""
    prize = db.where_one(CheckinPrize(), "id = ?", prize_id)
    if prize is not None:
        name = prize.name
    else:
        historical_award = db.where_one(
            CheckinPrizeAward(),
            "prize_id = ? ORDER BY id DESC LIMIT 1",
            prize_id,
        )
        if historical_award is None:
            raise ValueError("没有这个奖品编号，也没有对应的中奖记录。请先查看签到奖池。")
        name = historical_award.prize_name
    total = db.fetch_all(
        "SELECT COUNT(*) FROM checkin_prize_awards WHERE prize_id = ? AND delivered_at = 0",
        prize_id,
    )[0][0]
    pages, offset = page_bounds(total, page)
    awards = db.where_all(
        CheckinPrizeAward(),
        "prize_id = ? AND delivered_at = 0 ORDER BY id LIMIT ? OFFSET ?",
        prize_id,
        PAGE_SIZE,
        offset,
        default = [],
    )
    row_template = Template(pending_prize_row, autoescape = True)
    rows = [
        row_template.render(
            prize_name = award.prize_name,
            award_id = award.id,
            user_id = award.user_id,
            provider_id = award.provider_id,
            awarded_at = Time(award.awarded_at).format("%Y-%m-%d %H:%M"),
        ) for award in awards
    ]
    if not awards:
        rows.append(
            """<tr><td colspan="5" class="backpack-empty">
            <p class="backpack-empty-title">没有未兑奖记录</p>
            <p class="backpack-empty-hint">该奖品尚未被抽中，或中奖奖品均已兑付。</p>
        </td></tr>""",
        )
    footer = (
        f"第 {page}/{pages} 页 · 每页 {PAGE_SIZE} 件 · 权限奖品由中奖者自助兑奖；"
        "普通奖品实际发放后使用「签到奖池 兑付 记录编号」标记已兑付。"
    )
    if page < pages:
        footer += f" 下一页：签到奖池 未兑奖 {prize_id} {page + 1}"
    return str(
        HTMLSourceCode(
            application_name = f"未兑奖记录 · 奖品 #{prize_id} {escape(name)} · 共 {total} 件待兑付",
            table_head = pending_prize_table_head,
            table_body = "\n".join(rows),
            additional_css = backpack_css,
            footer = footer,
        ),
    )

PrizePoolMatcher = on_command("签到奖池", force_whitespace = True, priority = 5)
BackpackMatcher = on_command("背包", aliases = {"我的背包"}, force_whitespace = True, priority = 5)
RedeemMatcher = on_command("兑奖", aliases = {"自助兑奖"}, force_whitespace = True, priority = 5)

def redeem_response(event: MessageEvent, award_id: int) -> str:
    award = PrizePoolManage(event.user_id).redeem(award_id, getattr(event, "group_id", 0))
    target = f"群 {award.delivered_target}" if award.permission_scope == "group" else f"你（{award.user_id}）"
    return f"兑奖成功！已为{target}开通「{award.prize_name}」（记录 #{award.id}）。"

@PrizePoolMatcher.handle()
async def handle_prize_pool(event: MessageEvent, args: Message = CommandArg()):
    response: str | MessageSegment
    try:
        parts = shlex.split(args.extract_plain_text())
        if parts == ["帮助"]:
            response = POOL_HELP
        elif not parts or (len(parts) == 1 and parts[0].isdigit()):
            response = pool_listing(positive_number(parts[0]) if parts else 1)
        elif len(parts) == 2 and parts[0] == "兑奖":
            response = redeem_response(event, positive_number(parts[1]))
        else:
            if not check_permission(event.user_id, POOL_PERMISSION):
                raise PermissionError(POOL_PERMISSION)
            manager = PrizePoolManage(event.user_id)
            action = parts[0]
            if action == "清空背包" and len(parts) == 1:
                user_count, award_count = manager.clear_backpacks()
                response = f"已清空所有人的背包，共 {user_count} 人、{award_count} 条记录。"
            elif action == "投放" and len(parts) == 4:
                stock = -1 if parts[3] == "不限量" else positive_number(parts[3])
                prize = manager.add(parts[1], parse_probability(parts[2]), stock)
                response = f"已投放奖品 #{prize.id}：{prize.name}，概率 {format_probability(prize.probability)}。"
            elif action == "权限" and len(parts) == 4:
                scope = {"群权限": "group", "群": "group", "个人权限": "user", "个人": "user"}.get(parts[2])
                if scope is None:
                    raise ValueError("权限类型请使用「群权限」或「个人权限」。")
                prize = manager.set_permission(positive_number(parts[1]), scope, parts[3])
                kind = "群权限" if scope == "group" else "个人权限"
                response = f"已将奖品 #{prize.id}「{prize.name}」设为{kind}奖励，对后续中奖生效。"
            elif action == "权限" and len(parts) == 3 and parts[2] == "取消":
                prize = manager.set_permission(positive_number(parts[1]), "")
                response = f"已取消奖品 #{prize.id}「{prize.name}」的权限绑定，后续中奖改为人工兑付。"
            elif action in {"概率", "补货"} and len(parts) == 3:
                value = parse_probability(parts[2]) if action == "概率" else positive_number(parts[2])
                prize = manager.change(positive_number(parts[1]), action, value)
                response = f"已{action}奖品 #{prize.id}：{prize.name}。"
            elif action in {"上架", "下架", "删除"} and len(parts) == 2:
                prize = manager.change(positive_number(parts[1]), action)
                response = f"已{action}奖品 #{prize.id}：{prize.name}。"
            elif action == "记录" and len(parts) in {2, 3}:
                html = backpack_listing(positive_number(parts[1]), positive_number(parts[2]) if len(parts) == 3 else 1)
                response = await generate(html, ".container", segment = True)
            elif action in {"未兑奖", "未兑付", "待兑付"} and len(parts) in {2, 3}:
                html = pending_prize_listing(
                    positive_number(parts[1]),
                    positive_number(parts[2]) if len(parts) == 3 else 1,
                )
                response = await generate(html, ".container", segment = True)
            elif action == "兑付" and len(parts) == 2:
                award = manager.deliver(positive_number(parts[1]))
                response = f"已将 {award.user_id} 的奖品「{award.prize_name}」（记录 #{award.id}）标记为已兑付。"
            else:
                response = "命令格式错误。\n" + POOL_HELP
    except PermissionError as error:
        response = denied(POOL_PERMISSION) if str(error) == POOL_PERMISSION else str(error)
    except ValueError as error:
        response = str(error)
    await PrizePoolMatcher.finish(response)

@RedeemMatcher.handle()
async def handle_redeem(event: MessageEvent, args: Message = CommandArg()):
    try:
        parts = args.extract_plain_text().split()
        if len(parts) != 1:
            raise ValueError("格式：兑奖 <背包记录编号>。群权限奖品请在目标群内兑奖。")
        response = redeem_response(event, positive_number(parts[0]))
    except ValueError as error:
        response = str(error)
    await RedeemMatcher.finish(response)

@BackpackMatcher.handle()
async def handle_backpack(event: MessageEvent, args: Message = CommandArg()):
    response: str | MessageSegment
    parts = args.extract_plain_text().split()
    try:
        if len(parts) > 1:
            raise ValueError("格式：背包 [页码]。只能查看自己的背包。")
        html = backpack_listing(event.user_id, positive_number(parts[0]) if parts else 1)
        response = await generate(html, ".container", segment = True)
    except ValueError as error:
        response = str(error)
    await BackpackMatcher.finish(response)
