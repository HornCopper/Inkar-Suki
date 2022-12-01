import httpx
import datetime
import time

def checknumber(number):
    return number.isdecimal()

async def get_url(url, proxy: dict = None, args: dict = None, headers: str = None, timeout: int = 300):
    async with httpx.AsyncClient(proxies=proxy, follow_redirects = True) as client:
        if args == None:
            resp = await client.get(url, timeout = timeout, headers = headers)
        else:
            resp = await client.get(url, timeout = timeout, headers = headers, params=args)
        result = resp.text
        return result

async def get_api(url, proxy: dict = None, args: dict = None, headers: str = None, timeout: int = 300, data: dict = None):
    async with httpx.AsyncClient(proxies=proxy, follow_redirects = True) as client:
        if args == None:
            resp = await client.get(url, timeout = timeout, headers = headers)
        else:
            if data != None:
                resp = await client.get(url, timeout = timeout, headers = headers, params=args, data = data)
            else:
                resp = await client.get(url, timeout = timeout, headers = headers, params=args)
        result = resp.json()
        return result

async def post_url(url, proxy: dict = None, args: dict = None, headers: str = None, timeout: int = 300, data: dict = None):
    async with httpx.AsyncClient(proxies=proxy, follow_redirects = True) as client:
        if args == None:
            resp = await client.post(url, timeout = timeout, headers = headers)
        else:
            if data != None:
                resp = await client.post(url, timeout = timeout, headers = headers, params=args, data = data)
            else:
                resp = await client.post(url, timeout = timeout, headers = headers, params=args)
        result = resp.text
        return result

async def data_post(url, proxy: dict = None, json: dict = None, headers: str = None, timeout: int = 300):
    async with httpx.AsyncClient(proxies=proxy, follow_redirects = True) as client:
        if json == None:
            resp = await client.post(url, timeout = timeout, headers = headers)
        else:
            resp = await client.post(url, timeout = timeout, headers = headers, json=json)
        result = resp.text
        return result
    
async def get_status(url, proxy: dict = None, args: dict = None, headers: str = None, timeout: int = 300):
    async with httpx.AsyncClient(proxies=proxy, follow_redirects = True) as client:
        if args == None:
            resp = await client.get(url, timeout = timeout, headers = headers)
        else:
            resp = await client.get(url, timeout = timeout, headers = headers, params=args)
        result = resp.status_code
        return result

async def get_content(url, proxy: dict = None, args: dict = None, headers: str = None, timeout: int = 300):
    async with httpx.AsyncClient(proxies=proxy, follow_redirects = True) as client:
        if args == None:
            resp = await client.get(url, timeout = timeout, headers = headers)
        else:
            resp = await client.get(url, timeout = timeout, headers = headers, params=args)
        results = resp.content
        return results

def convert_time(timestamp: int):
    time_local = time.localtime(timestamp / 1000)
    dt = time.strftime("%Y年%m月%d日 %H:%M:%S", time_local)
    return dt

def nodetemp(nickname: str, qqnumber: str, message: str) -> dict:
    return {"type":"node","data":{"name":nickname,"uin":qqnumber,"content":message}}