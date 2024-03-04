from .dh import *
from .wg import *

from urllib.parse import unquote

async def get_from(url: str):
    data = await get_url(url)
    return unquote(re.findall(r"<meta furl=\".+fname", data)[0][33:-16])