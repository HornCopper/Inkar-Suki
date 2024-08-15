from src.tools.config import Config

proxy = Config.bot_basic.proxy

if proxy == "":
    proxy = None

import httpx

async def get_url(url, **kwargs):
    async with httpx.AsyncClient(follow_redirects=True, verify=False, proxy=proxy) as client:
        resp = await client.get(url, **kwargs)
        result = resp.text
        return result
    
async def get_content(url, **kwargs):
    async with httpx.AsyncClient(follow_redirects=True, verify=False, proxy=proxy) as client:
        resp = await client.get(url, **kwargs)
        result = resp.content
        return result

async def get_status(url, **kwargs):
    async with httpx.AsyncClient(follow_redirects=True, verify=False, proxy=proxy) as client:
        resp = await client.get(url, **kwargs)
        result = resp.status_code
        return result
    
async def get_api(url, **kwargs):
    async with httpx.AsyncClient(follow_redirects=True, verify=False, proxy=proxy) as client:
        resp = await client.get(url, **kwargs)
        result = resp.json()
        return result

async def post_url(url, **kwargs):
    async with httpx.AsyncClient(follow_redirects=True, verify=False, proxy=proxy) as client:
        resp = await client.post(url, **kwargs)
        result = resp.text
        return result