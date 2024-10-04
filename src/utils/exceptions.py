from httpx import ConnectTimeout

class RequestDataException(Exception):
    """
    `httpx`异步请求的请求体携带错误类型的数据。

    `await client.get(url, data=...)`, `data` require type `str`.
    """
    ...

class BrowserNotInitializedException(Exception):
    """
    `Playwright`网页访问尚未初始化浏览器。
    """
    ...

class DatabaseInternelException(Exception):
    """
    `SQLite3`数据库错误。
    """

class QixueDataUnavailable(Exception):
    """
    没有任何可用的奇穴数据。
    """
    ...

class ConfigurationException(Exception):
    """
    配置文件有问题。

    例如启用`JX3API`但没有给出`Token`。
    """