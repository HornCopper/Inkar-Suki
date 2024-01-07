from src.tools.dep import *


@Jx3Arg.requireToken
@Jx3Arg.requireTicket
async def arena_records(server: str = None, name: str = None, mode: str = "33"):
    final_url = f"{Config.jx3api_link}/view/match/recent?token={token}&name={name}&server={server}&robot={bot}&ticket={ticket}&mode={mode}&scale=1"
    return await Jx3ApiRequest(final_url).output_url()


@Jx3Arg.requireToken
@Jx3Arg.requireTicket
async def arena_rank(mode: str = "33"):
    final_url = f"{Config.jx3api_link}/view/match/awesome?token={token}&robot={bot}&ticket={ticket}&mode={mode}&scale=1"
    return await Jx3ApiRequest(final_url).output_url()


@Jx3Arg.requireToken
@Jx3Arg.requireTicket
async def arena_statistics(mode: str = "33"):
    final_url = f"{Config.jx3api_link}/view/match/schools?token={token}&robot={bot}&ticket={ticket}&mode={mode}&scale=1"
    return await Jx3ApiRequest(final_url).output_url()
