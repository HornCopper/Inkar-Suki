from typing import Any
from urllib.request import urlopen

from src.utils.database import cache_db
from src.utils.database.classes import RequestData
from src.utils.exceptions import RequestDataException
from src.utils.decorators import ticket_required
from src.utils.tuilan import gen_xsk, gen_ts, format_body
from src.utils.time import Time

import httpx
import json

class Request:
    def __init__(self, url: str, *, headers: dict = {}, params: str | dict = {}):
        """
        构造网络请求，亦可以请求本地内容。

        Args:
            url (str): 请求的目标`URL`。
            headers (dict): 请求头。
            params (dict, str): 请求体，当为`dict`时按`json`传参给`POST`请求，按`params`传参给`GET`请求；当为`str`时不可传入`GET`请求，按`data`传参给`POST`请求。
        """
        self.url = url
        self.headers = headers 
        self.params = params

    async def get(self, expire_at: int = 0, timeout = 20, **kwargs) -> httpx.Response:
        """
        发送`GET`请求。

        Args:
            expire_at (int): 过期时间戳，在过期时间戳到达之前请求请求同一个地址均会使用第一次返回。
            timeout (int): 超时时间，单位`seconds`，默认为`20`。

        Returns:
            response (httpx.Response): `httpx`响应类。
        """
        if isinstance(self.params, str):
            raise RequestDataException("Method `GET` not accept argument `params` with type `str`!")
        
        if expire_at != 0:
            cached: RequestData | Any = cache_db.where_one(RequestData(), "timestamp >= ? AND url = ?", Time().raw_time, self.url, default=None)
            if cached is not None:
                return httpx.Response(status_code=200, content=cached.response_data.encode("utf-8"))

        async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
            response = await client.get(self.url, params=self.params, headers=self.headers, timeout=timeout, **kwargs)
    
        if expire_at != 0:
            cache_db.delete(RequestData(), "url = ? AND timestamp < ?", self.url, Time().raw_time)
            cache_db.save(
                RequestData(
                    url=self.url,
                    headers=self.headers,
                    params=self.params,
                    response_data=response.text,
                    timestamp=expire_at,
                )
            )

        return response
    
    async def post(self, tuilan: bool = False, timeout: int = 20) -> httpx.Response:
        """
        发送`POST`请求。

        Args:
            tuilan (bool): 是否为推栏请求，如果是则构造推栏请求。
            timeout (int): 超时时间，单位秒（s）。
        """
        async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
            if isinstance(self.params, str):
                request_params = {
                    "url": self.url,
                    "data": self.params,
                    "headers": self.headers
                }
            else:
                request_params = {
                    "url": self.url,
                    "json": self.params,
                    "headers": self.headers
                }
            if tuilan:
                if not isinstance(self.params, dict):
                    raise ValueError("Cannot accept argument `params` without type `dict` when `tuilan` equal `True`.")
                request_params: dict = self._build_tuilan_request(self.params)
            response = await client.post(timeout=timeout, **request_params)
            return response
        
    @property
    def local_content(self) -> bytes:
        """
        读取`File URL`的本地字节内容。
        """
        if not self.url.startswith("file"):
            raise ValueError("Canot accept the argument `url` without one started with `file`!")
        with urlopen(self.url) as f:
            return f.read()
    
    @ticket_required
    def _build_tuilan_request(self, params: dict, ticket: str = "") -> dict:
        """
        构造推栏请求。
        
        Args:
            params (dict): 请求体，可不携带`ts`字段。
            ticket (str): 推栏`Token`，需要通过一些方法获得，由装饰器进行填入，**调用时不要传入`ticket`**。

        Returns:
            arguments (dict): 关键字参数字典。
        """
        if params is {}:
            params = {"ts": gen_ts()}
        if "ts" not in params:
            params["ts"] = gen_ts()
        device_id = ticket.split("::")[-1]
        params_ = format_body(params)
        xsk = gen_xsk(params_)
        basic_headers = {
            "Host": "m.pvp.xoyo.com",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "fromsys": "APP",
            "gamename": "jx3",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "apiversion": "3",
            "platform": "ios",
            "token": ticket,
            "deviceid": device_id,
            "Cache-Control": "no-cache",
            "clientkey": "1",
            "User-Agent": "SeasunGame/202CFNetwork/1410.0.3Darwin/22.6.0",
            "sign": "true",
            "x-sk": xsk
        }
        request_params = {
            "url": self.url,
            "data": params_,
            "headers": basic_headers
        }
        return request_params