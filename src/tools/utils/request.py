from nonebot.log import logger
import httpx


async def get_default_args(**kwargs):
    kwargs["timeout"] = kwargs.get("timeout") or 5
    return kwargs


async def send_with_async(method: str, url: str, **kwargs) -> httpx.Response:
    """
    @param method str:请求方式，不区分大小写 如GET POST PUT PATCH OPTION DELETE HEADER TRACE等
    @param url str:请求的地址
    @param proxy dict:使用的代理 格式为{"http":"http://xxxx:xxx","https":...}
    @param **kwargs:其他参数如 headers json data timeout等
    @return httpx.Response:响应结果
    以指定方式发出请求，并返回请求结果的Response对象
    """
    kwargs = await get_default_args(**kwargs)
    client = kwargs.get("client")
    if client:
        del kwargs["client"]
    else:
        client = httpx.AsyncClient(follow_redirects=True, verify=False)

    max_try_time = 3
    current_try_time = 0
    while True:
        # TODO use AOP
        try:
            logger.debug(f"request:{method}@{url}")
            req = await client.request(method, url, **kwargs)
            req.encoding = "utf-8"
            return req
        except httpx.TimeoutException as ex:
            current_try_time += 1
            if max_try_time > current_try_time:
                continue
            msg = f"max_try_time(count={current_try_time}) exceeded to request in httpx({method} -> {url}):[{type(ex).__name__}]{ex}"
            logger.error(msg)
            return None
        except Exception as ex:
            logger.error(f"fail to request in httpx({method} -> {url}):[{type(ex).__name__}]{ex}")
            return None


async def get_url(url: str, **kwargs) -> str:
    """
    以get方式发出请求，并将返回的结果以plaintext方式处理
    """
    r = await send_with_async("get", url, **kwargs)
    return r and r.text


async def get_api(url, **kwargs) -> dict:
    """
    以get方式发出请求，并将返回的结果以json方式处理
    """
    r = await send_with_async("get", url, **kwargs)
    try:
        return r and r.json()
    except Exception as ex:
        logger.error(f"fail convert response to json:{ex},raw:{r.text}")
        return None


async def post_url(url, **kwargs) -> str:
    """
    以post方式发出请求，data为form-url-encoded, json为application/json
    """
    r = await send_with_async("post", url, **kwargs)
    return r and r.text


async def data_post(url, **kwargs) -> str:
    """
    功能与post_url一致
    """
    await post_url(url, **kwargs)


async def get_status(url, **kwargs) -> int:
    """
     以get方式发出请求，获取请求结果的status_code
    """
    r = await send_with_async("get", url, **kwargs)
    return r and r.status_code


async def get_content(url, **kwargs) -> bytes:
    """
     以get方式发出请求，获取请求结果的直接内容
    """
    r = await send_with_async("get", url, **kwargs)
    return r and r.content
