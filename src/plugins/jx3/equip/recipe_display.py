"""Use optional recipe descriptions without changing legacy equipment values."""

from collections import defaultdict, deque


def iter_set_attributes(equip: dict):
    descriptions = defaultdict(deque)
    for effect in equip.get("SetEffects", []):
        if effect.get("key") == "atSetEquipmentRecipe":
            # Keep duplicate ID/count terms ordered: they may have different recipe levels.
            descriptions[(str(effect["count"]), str(effect["value"]))].append(effect.get("description") or "")
    for count, attributes in equip.get("SetAttributes", {}).items():
        for attribute in attributes:
            key, value = next(iter(attribute.items()))
            pending = descriptions[(str(count), str(value))] if key == "atSetEquipmentRecipe" else None
            yield count, key, value, pending.popleft() if pending else ""
