import httpx

def checknumber(number):
    return number.isdecimal()

async def get_url(url, headers: str = None, timeout: int = 300):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url,timeout=timeout,headers=headers)
        result = resp.text
        return result
        
async def post_url(url):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.post(url,timeout=300)
        result = resp.text
        return result
    
async def get_status(url):
    async with httpx.AsyncClient(follow_redirects=False) as client:
        resp = await client.get(url,timeout=300)
        result = resp.status_code
        return result