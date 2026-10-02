from functools import cache
from fnmatch import fnmatchcase
import json
from typing import Any, Literal, Sequence

from src.const.path import ASSETS, build_path
from src.utils.database.classes import Account, GroupSettings
from src.utils.database import db


def _bot_owner_ids() -> tuple[str, ...]:
    try:
        from src.config import Config
    except ModuleNotFoundError:
        return ()
    return tuple(Config.bot_basic.bot_owner)


def _is_bot_owner(user_id: str | int) -> bool:
    return str(user_id) in _bot_owner_ids()


def _normalize_node(node: str | int) -> str:
    return str(node).strip().strip(".")


def _child_node(parent: str, child: str) -> str:
    if child.startswith(parent + "."):
        return child
    return f"{parent}.{child}"


@cache
def _defined_leaf_nodes(scope: str = "user") -> tuple[str, ...]:
    node_file = build_path(ASSETS, ["source", "permission", "node.json"])
    with open(node_file, "r", encoding="utf-8") as f:
        node_data = json.load(f)

    leaves: list[str] = []

    def walk(nodes: list[dict[str, Any]], prefix: str = "") -> None:
        for node in nodes:
            name = _normalize_node(str(node.get("name", "")))
            if not name:
                continue
            full_name = _child_node(prefix, name) if prefix else name
            sub_nodes = node.get("sub_node", [])
            if isinstance(sub_nodes, list) and sub_nodes:
                walk(sub_nodes, full_name)
            else:
                leaves.append(full_name)

    nodes = node_data.get(scope, [])
    if isinstance(nodes, list):
        walk(nodes)

    return tuple(sorted(set(leaves)))


def _node_match(granted: str | int, required: str | int) -> bool:
    granted = _normalize_node(granted)
    required = _normalize_node(required)
    if not granted or not required:
        return False
    if granted == "*":
        return True
    if granted.endswith(".*"):
        prefix = granted[:-2]
        return required == prefix or required.startswith(prefix + ".")
    if "*" in granted:
        return fnmatchcase(required, granted)
    return required == granted or required.startswith(granted + ".")


def _split_permission_nodes(nodes: Sequence[str | int]) -> tuple[list[str], list[str]]:
    grants: list[str] = []
    denies: list[str] = []
    for raw_node in nodes:
        node = _normalize_node(raw_node)
        if not node:
            continue
        if node.startswith("-"):
            denied_node = _normalize_node(node[1:])
            if denied_node:
                denies.append(denied_node)
        else:
            grants.append(node)
    return grants, denies


def _check_node_permission(account: Account, required: str | int) -> bool:
    required = _normalize_node(required)
    if not required:
        return False
    if required == "*":
        return "*" in account.permission_nodes
    return _check_nodes_permission(account.permission_nodes, required)


def _check_nodes_permission(nodes: Sequence[str | int], required: str | int) -> bool:
    grants, denies = _split_permission_nodes(nodes)
    if any(_node_match(node, required) for node in denies):
        return False
    return any(_node_match(node, required) for node in grants)


def _check_user_permission(account: Account, node: str | int) -> bool:
    if _is_bot_owner(account.user_id):
        _, denies = _split_permission_nodes(account.permission_nodes)
        return not any(_node_match(denied_node, node) for denied_node in denies)
    return _check_node_permission(account, node)


def normalize_permission_nodes(nodes: Sequence[str | int]) -> list[str]:
    normalized: list[str] = []
    for raw_node in nodes:
        node = _normalize_node(raw_node)
        if not node:
            continue
        if node.startswith("-"):
            denied_node = _normalize_node(node[1:])
            node = f"-{denied_node}" if denied_node else ""
        if node and node not in normalized:
            normalized.append(node)
    return normalized


def is_defined_permission_node(node: str | int, scope: str = "user") -> bool:
    node = _normalize_node(node)
    if not node:
        return False
    if node == "*":
        return True
    return any(_node_match(node, leaf) for leaf in _defined_leaf_nodes(scope))


def _resolve_deepest_nodes(raw_nodes: Sequence[str | int], leaves: tuple[str, ...]) -> list[str]:
    result: set[str] = set()
    grants, denies = _split_permission_nodes(raw_nodes)
    for node in grants:
        matched = {leaf for leaf in leaves if _node_match(node, leaf)}
        if matched:
            result.update(matched)
        else:
            result.add(node)
    for node in denies:
        matched = {leaf for leaf in leaves if _node_match(node, leaf)}
        if matched:
            result.difference_update(matched)
        else:
            result.discard(node)
    return sorted(result)


def get_deepest_permission_nodes(user_id: str | int) -> list[str]:
    """
    返回用户最终生效的最深层权限节点。

    父节点和通配符会展开为 node.json 中定义的叶子节点。
    未知的自定义节点会原样保留，方便管理员查看。
    """
    data: Account | Any = db.where_one(
        Account(),
        "user_id = ?",
        int(user_id),
        default=Account(user_id=int(user_id)),
    )
    leaves = _defined_leaf_nodes("user")
    if _is_bot_owner(user_id):
        return _resolve_deepest_nodes(["*", *data.permission_nodes], leaves)
    return _resolve_deepest_nodes(data.permission_nodes, leaves)


def get_deepest_group_permission_nodes(group_id: str | int) -> list[str]:
    from src.utils.database.classes import GroupSettings

    data: GroupSettings | Any = db.where_one(
        GroupSettings(),
        "group_id = ?",
        str(group_id),
        default=GroupSettings(group_id=str(group_id)),
    )
    return _resolve_deepest_nodes(data.permission_nodes, _defined_leaf_nodes("group"))


def check_permission(user_id: str | int, node: str | int) -> bool:
    """
    检查用户是否满足某个权限节点。

    参数:
        user_id (str, int): 用户 QQ 号。
        node (str): 所需的权限节点。
    """
    data: Account | Any = db.where_one(
        Account(),
        "user_id = ?",
        int(user_id),
        default=Account(user_id=int(user_id)),
    )
    return _check_user_permission(data, node)


def check_group_permission(group_id: str | int, node: str | int) -> bool:
    data: GroupSettings | Any = db.where_one(
        GroupSettings(),
        "group_id = ?",
        str(group_id),
        default=GroupSettings(group_id=str(group_id)),
    )
    return _check_nodes_permission(data.permission_nodes, node)


def get_permission_holders(node: str, scope: Literal["user", "group"]) -> list[str]:
    """反查具体节点的有效持有者，一次读取账户，避免逐个查询数据库。"""
    if scope not in {"user", "group"}:
        raise ValueError("查询范围需要是用户或群。")
    node = _normalize_node(node)
    if not node or "*" in node or node.startswith("-"):
        raise ValueError("请使用非空的具体权限节点，不支持通配符或拒绝节点。")

    matches: set[str] = set()
    if scope == "user":
        accounts: dict[str, Account] = {}
        for account in db.where_all(Account(), "1=1 ORDER BY id", default=[]):
            if account.user_id > 0:
                accounts.setdefault(str(account.user_id), account)
        # Bot 主人即使没有账户记录也具备权限，显式拒绝仍然生效。
        for owner_id in _bot_owner_ids():
            if owner_id.isdigit() and int(owner_id) > 0:
                accounts.setdefault(owner_id, Account(user_id=int(owner_id)))
        matches.update(user_id for user_id, account in accounts.items() if _check_user_permission(account, node))
    else:
        groups: dict[str, GroupSettings] = {}
        for group in db.where_all(GroupSettings(), "1=1 ORDER BY id", default=[]):
            if group.group_id.isdigit() and int(group.group_id) > 0:
                groups.setdefault(group.group_id, group)
        matches.update(group_id for group_id, group in groups.items() if _check_nodes_permission(group.permission_nodes, node))
    return sorted(matches, key=int)


def denied(node: str | int) -> str:
    """
    构造权限不足提示。

    参数:
        node (str): 没有达到的权限节点。
    """
    return f"唔……你权限不够哦，这条命令需要 {node} 权限哦~"
