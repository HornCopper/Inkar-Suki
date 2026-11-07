"""OneBot 查询到 QQ 官方接口的转换，所有 OpenID 均限制在当前应用和会话。"""

from typing import Any, TYPE_CHECKING
from datetime import timedelta

from nonebot.adapters.qq.exception import ActionFailed
from nonebot.adapters.qq.models.qq import SetMemberMuteState

if TYPE_CHECKING:
    from . import QQCompatBot

UNHANDLED = object()
UNSUPPORTED_APIS = frozenset({"get_cookies", "get_group_file_url", "set_group_leave", "set_group_add_request"})


def unavailable(error: ActionFailed) -> bool:
    return error.code == 11253 or error.status_code in {403, 404}


class ContextAPI:
    def __init__(self, bot: "QQCompatBot"):
        self.bot = bot
        self.notes: set[str] = set()
        self.members: list[dict[str, Any]] | None = None
        self.profiles: dict[int, dict[str, Any]] = {}
        self.group: dict[str, Any] | None = None
        self.bot_state: Any = None

    def same_target(self, scope: str, value: Any, expected: int) -> bool:
        try:
            store = self.bot.identities
            return store.resolve(scope, value) == store.resolve(scope, expected)
        except (ValueError, TypeError):
            return False

    def require_group(self, data: dict[str, Any]) -> None:
        if not self.bot.is_group or not self.same_target("group", data.get("group_id"), self.bot.group_id):
            self.bot.skip("接口仅适用于当前官方群")

    def member(self, value: Any) -> dict[str, Any]:
        bot = self.bot
        raw = bot.identities.identify(bot.app_id, f"member:{bot.target}", value.member_openid)
        uid = bot.identities.resolve("user", raw)
        row = {
            "group_id": bot.group_id, "user_id": uid,
            "nickname": value.username or str(uid), "card": "",
            "role": value.member_role or "member", "bot": value.bot,
        }
        if value.joined_at is not None:
            row["join_time"] = int(value.joined_at.timestamp())
        self.profiles[uid] = row
        return row

    async def group_info(self) -> dict[str, Any]:
        if self.group is None:
            try:
                value = await self.bot.native.get_group_info(group_id = self.bot.target)
            except ActionFailed as error:
                if not unavailable(error):
                    raise
                self.bot.log_compatibility("群资料接口不可用，使用群号显示", action = "降级", official_api = "get_group_info",
                                           code = error.code, status = error.status_code)
                self.notes.add("群名未获取，使用群号显示。")
                self.group = {"group_id": self.bot.group_id, "group_name": str(self.bot.group_id)}
            else:
                self.group = {
                    "group_id": self.bot.group_id, "group_name": value.group_name,
                    "member_count": value.group_member_num, "group_memo": value.group_finger_memo,
                }
        return self.group.copy()

    async def member_info(self, user_id: Any) -> dict[str, Any]:
        bot = self.bot
        if self.same_target("user", user_id, bot.user_id):
            return bot.sender_info()
        if int(user_id) == int(bot.self_id):
            if self.bot_state is None:
                try:
                    self.bot_state = await bot.native.get_group_bot_state(group_id = bot.target)
                except ActionFailed as error:
                    if unavailable(error):
                        return bot.skip("机器人群内状态接口未获授权", official_api = "get_group_bot_state",
                                        code = error.code, status = error.status_code)
                    raise
            return {"group_id": bot.group_id, "user_id": int(bot.self_id), "nickname": "QQ机器人",
                    "card": "", "role": self.bot_state.member_role, "bot": True}
        uid = bot.identities.resolve("user", user_id)
        if uid in self.profiles:
            return self.profiles[uid].copy()
        openid = bot.identities.lookup(bot.app_id, f"member:{bot.target}", user_id)
        if openid is None:
            return bot.skip("当前群没有该用户对应的 OpenID")
        try:
            return self.member(await bot.native.get_group_member(group_openid = bot.target, member_openid = openid))
        except ActionFailed as error:
            if unavailable(error):
                return bot.skip("群成员信息接口未获授权", official_api = "get_group_member",
                                code = error.code, status = error.status_code)
            raise

    async def member_list(self) -> list[dict[str, Any]]:
        if self.members is None:
            cursor = None
            cursors: set[str] = set()
            rows: dict[int, dict[str, Any]] = {}
            while True:
                try:
                    value = await self.bot.native.get_group_members(group_openid = self.bot.target, cursor = cursor)
                except ActionFailed as error:
                    if unavailable(error):
                        return self.bot.skip("完整群成员名单需要官方白名单权限", official_api = "get_group_members",
                                             code = error.code, status = error.status_code)
                    raise
                for item in value.members:
                    row = self.member(item)
                    rows[row["user_id"]] = row
                if not value.next_cursor:
                    break
                if value.next_cursor in cursors:
                    return self.bot.skip("群成员列表返回重复分页游标")
                cursor = value.next_cursor
                cursors.add(cursor)
            self.members = list(rows.values())
        return [row.copy() for row in self.members]

    async def call(self, api: str, data: dict[str, Any]) -> Any:
        bot = self.bot
        if api in {"get_group_list", "get_friend_list"}:
            bot.log_compatibility("平台未提供完整群/好友名单，使用本地已识别会话", action = "降级")
            group = api == "get_group_list"
            known = dict(bot.identities.known(bot.app_id, "group" if group else "user"))
            if group:
                return [{"group_id": uid, "group_name": str(uid), "qq_official_partial": True} for uid in known]
            return [{"user_id": uid, "nickname": str(uid), "remark": "", "qq_official_partial": True} for uid in known]
        if api == "get_stranger_info":
            uid = bot.identities.resolve("user", data["user_id"])
            if uid == bot.user_id:
                return {"user_id": uid, "nickname": bot.sender_info()["nickname"]}
            if uid in self.profiles:
                return self.profiles[uid].copy()
            bot.log_compatibility("用户昵称不可用，使用用户 ID 显示", action = "降级")
            self.notes.add("未获取的用户昵称以用户 ID 显示。")
            return {"user_id": uid, "nickname": str(uid), "qq_official_partial": True}
        if api == "get_image":
            requested = str(data.get("file", ""))
            for attachment in bot.source.attachments or []:
                url = attachment.url or ""
                if url.startswith("//"):
                    url = "https:" + url
                if (requested in {url, attachment.filename} and attachment.content_type.startswith("image/")
                    and url.startswith(("https://", "http://"))):
                    return {"url": url, "file": url, "filename": attachment.filename, "file_size": attachment.size}
            return bot.skip("当前消息中没有可解析的图片附件")
        if api == "get_group_member_info" and self.same_target("group", data.get("group_id"), bot.group_id):
            if self.same_target("user", data.get("user_id"), bot.user_id):
                return bot.sender_info()
        if api == "get_group_info" and not bot.is_group and self.same_target("group", data.get("group_id"), bot.group_id):
            return {"group_id": bot.group_id, "group_name": "QQ 单聊上下文"}
        if api in {"get_group_info", "get_group_member_info", "get_group_member_list", "set_group_ban"}:
            self.require_group(data)
            if api == "get_group_info":
                return await self.group_info()
            if api == "get_group_member_info":
                return await self.member_info(data["user_id"])
            if api == "get_group_member_list":
                return await self.member_list()
            duration = int(data.get("duration", 1800))
            if not 0 <= duration <= 30 * 86400:
                return bot.skip("官方禁言时长必须在 0 至 30 天之间")
            openid = bot.identities.lookup(bot.app_id, f"member:{bot.target}", data["user_id"])
            if openid is None:
                return bot.skip("当前群没有该用户对应的 OpenID")
            state = SetMemberMuteState(op = "add" if duration else "del", member_openid = openid,
                                       mute_expire_at = timedelta(seconds = duration) if duration else None)
            await bot.native.set_group_members_mute(group_id = bot.target, members = [state])
            return None
        return UNHANDLED
