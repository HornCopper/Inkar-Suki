class BotException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidArgumentException(BotException):
    '''
    invalid argument
    '''
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
