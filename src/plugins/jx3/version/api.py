from configparser import ConfigParser

from src.utils.network import Request

async def get_latest_version(is_exp: bool, parser: ConfigParser = ConfigParser()) -> str:
    version_type = "exp" if is_exp else "hd"
    url = f"https://jx3hdv4hsyq-autoupdate.xoyocdn.com/jx3hd_v4/zhcn_{version_type}/autoupdateentry.txt"
    parser.read_string(
        (
            await Request(url).get()
        ).text
    )
    return parser["version"]["LatestVersion"]