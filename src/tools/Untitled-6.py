import httpx
from bs4 import BeautifulSoup

async def get_url(url, proxy: dict = None, args: dict = None, headers: str = None, timeout: int = 300, data: dict = None):
    async with httpx.AsyncClient(proxies=proxy, follow_redirects = True) as client:
        if args == None:
            resp = await client.get(url, timeout = timeout, headers = headers)
        else:
            if data != None:
                resp = await client.get(url, timeout = timeout, headers = headers, params=args, data = data)
            else:
                resp = await client.get(url, timeout = timeout, headers = headers, params=args)
        result = resp.text
        return result


        

import asyncio
result = asyncio.run(verify_cheater("3328236362"))
print(result)