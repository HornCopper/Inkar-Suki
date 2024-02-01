from ..SubscribeRegister import *
from src.tools.dep.bot.group_env import *

class GroupStatistics:

    @staticmethod
    def run_single_statistics(groups: list[str]):
        for group in groups:
            GroupActivity(group).update_statistics_slient()

    @staticmethod
    async def run_statistics():
        tasks = await GroupGather.get_all_groups()
        for bot in tasks:
            # 若一个群有多个机器人，则每次记录多次，是正常逻辑
            groups = tasks[bot]
            GroupStatistics.run_single_statistics(groups)


try:
    scheduler.add_job(GroupStatistics.run_statistics, "cron",
                      hour="0", id="GroupStatistics.run_statistics")
except Exception as e:
    logger.warning(f"功能统计的定时任务添加失败，{repr(e)}")
