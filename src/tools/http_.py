import httpx
class http:
    async def get_url(url):
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(url,timeout=300)
            result = resp.text
            return result
        
    async def post_url(url):
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.post(url,timeout=300)
            result = resp.text
            return result
    
    async def get_status(url):
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(url,timeout=300)
            result = resp.status_code
            return result