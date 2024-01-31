from sgtpyutils.logger import logger
from sgtpyutils.extensions import clazz
from .root import *
from .BaseCatalog import *

import importlib
import importlib.util
import pathlib2
import os
from . import permissions_description

cata_module_dict: dict[str, any] = {}
cata_entity_dict: dict[str, BaseCatalog] = {}
root_permission_name = permissions_description.__name__
cata_len = len(root_permission_name) + 1


def get_cata_entity(cata: str):
    if isinstance(cata, str):
        raw_start = "permission"
        if cata.startswith(raw_start):
            cata = cata[len(raw_start):]
        cata = cata_entity_dict.get(cata)
        if not cata:
            return None
    return cata


def register_document():
    root = pathlib2.Path(permissions_description.__file__).parent
    root_pck = permissions_description.__name__
    root_path = root.as_posix()
    p_len = len(root_path) + 1
    for root, dirs, files in os.walk(root_path):
        pck_name = root[p_len:].replace("/", ".").replace("\\", ".")
        modules = [x[0:-3] for x in files if x.endswith(".py")]
        if not modules or not pck_name:
            continue
        for m in modules:
            m = m.replace("__init__", "")
            m_name = f".{m}" if m else ""
            m_full_name = f".{pck_name}{m_name}"
            # logger.debug(f"importing:{m_full_name}")
            module = importlib.import_module(m_full_name, f"{root_pck}")
            cata_module_dict[m_full_name] = module
            setattr(module, "id", module.__name__)


register_document()


def register_parents(root):
    # logger.debug(f"register permission:{path}")
    if not root.name:
        logger.warning(f"invalid permission in:{root.__qualname__}")
        return False
    cata_name = root.__qualname__
    root.path = cata_name
    cata_entity_dict[cata_name] = root
    if not cata_name:
        return False
    children = [getattr(root, x) for x in clazz.class2props(root)]
    p_children = [x for x in children if type(x) == type]
    p_children = [x for x in p_children if not x.__name__ == "BaseCatalog"]
    has_child = False
    for child in p_children:
        if not register_parents(child):
            continue
        setattr(child, "parent", root)
        has_child = True
    if not has_child:
        return True
    setattr(root, "children", p_children)
    return True


register_parents(permission)
pass