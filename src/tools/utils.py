import httpx
import datetime
import time

def checknumber(number):
    return number.isdecimal()

async def get_url(url, headers: str = None, timeout: int = 300):
    async with httpx.AsyncClient(follow_redirects = True) as client:
        resp = await client.get(url, timeout = timeout, headers = headers)
        result = resp.text
        return result

async def get_api(url, headers: str = None, timeout: int = 300):
    async with httpx.AsyncClient(follow_redirects = True) as client:
        resp = await client.get(url, timeout = timeout, headers = headers)
        result = resp.json()
        return result

async def post_url(url, timeout: int = 300):
    async with httpx.AsyncClient(follow_redirects = True) as client:
        resp = await client.post(url, timeout = timeout)
        result = resp.text
        return result
    
async def get_status(url, headers: str = None, timeout: int = 300):
    async with httpx.AsyncClient(follow_redirects = False) as client:
        resp = await client.get(url,timeout=timeout)
        result = resp.status_code
        return result

async def get_content(url, headers: str = None, timeout: int = 300):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url, timeout = timeout, headers = headers)
        results = resp.content
        return results

def convert_time(timestamp: int):
    time_local = time.localtime(timestamp / 1000)
    dt = time.strftime("%Y年%m月%d日 %H:%M:%S", time_local)
    return dt

def nodetemp(nickname: str, qqnumber: str, message: str) -> dict:
    return {"type":"node","data":{"name":nickname,"uin":qqnumber,"content":message}}