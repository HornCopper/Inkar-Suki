from typing import Any

from src.utils.database import db
from src.utils.database.classes import PersonalSettings, RoleData
from src.utils.permission import check_permission

class RoleBind:
    def __init__(self, user_id: str | int, roles: list[tuple[str, str]]):
        self.user_id = int(user_id)
        self.roles = roles
        print(self.roles)

    def bind(self) -> str:
        exist_roles: list[RoleData] = []
        personal_settings: PersonalSettings | Any = db.where_one(PersonalSettings(), "user_id = ?", self.user_id, default=PersonalSettings(user_id=self.user_id))
        bound_roles = personal_settings.roles
        for role, server in self.roles:
            role_data: RoleData | Any = db.where_one(RoleData(), "roleName = ? AND serverName = ?", role, server, default=None)
            if role_data is not None:
                exist_roles.append(role_data)
        final_bound_roles = list(set(bound_roles) | set(exist_roles))
        if len(final_bound_roles) > 10 and not check_permission(self.user_id, 10):
            return f"绑定失败！\n绑定后的总角色数量超过10个，请酌情绑定！\n目前已绑定 {len(bound_roles)}/10 个角色"
        personal_settings.roles = final_bound_roles
        db.save(personal_settings)
        msg = "绑定成功，当前绑定的角色如下：\n" + \
            "\n".join(
                [
                    f"○ {r.roleName}·{r.serverName}"
                    for r
                    in final_bound_roles
                ]
            ) + \
            "\n若有已输入但未出现在此处的角色，请提交角色，数据库中未找到对应玩家，已自动过滤。\n本命令的角色名请用中括号包裹起来，命令实例：\n绑定角色 [示例角色·梦江南][示例角色2]\n不指定服务器的角色按本群绑定服务器进行绑定！"
        return msg

    def unbind(self, all: bool = False) -> str:
        personal_settings: PersonalSettings | Any = db.where_one(PersonalSettings(), "user_id = ?", self.user_id, default=PersonalSettings(user_id=self.user_id))
        if all:
            personal_settings.roles = []
            db.save(personal_settings)
            return "已清除所有的角色绑定！"
        else:
            bound_roles = personal_settings.roles
            final_roles = [
                r
                for r
                in bound_roles
                if (r.roleName, r.serverName) not in self.roles
            ]
            personal_settings.roles = final_roles
            db.save(personal_settings)
            msg = "解绑成功，当前剩余绑定的角色如下：\n" + \
                "\n".join(
                    [
                        r.roleName + r.serverName
                        for r
                        in final_roles
                    ]
                )
            return msg