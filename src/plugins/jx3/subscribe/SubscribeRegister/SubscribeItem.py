class SubjectCron:
    def __init__(self, exp: str, notify: str = None, level: int = 0) -> None:
        '''
        @param expression CRON-exp
            year (int|str) – 4-digit year
            month (int|str) – month (1-12)
            day (int|str) – day of month (1-31)
            week (int|str) – ISO week (1-53)
            day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
            hour (int|str) – hour (0-23)
            minute (int|str) – minute (0-59)
            second (int|str) – second (0-59)
        @param notify will pass to callback
        @param level will pass to callback
        '''
        self.expression = exp
        self.notify = notify
        self.level = level


class SubscribeSubject:
    def __init__(self, name: str, description: str = None, children_subjects: list = None, cron: list[SubjectCron] = None) -> None:
        self.name = name
        self.description = description
        self.children = [] if not children_subjects else children_subjects
        self.cron = cron
