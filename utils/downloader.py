import asyncio
from hashlib import md5
from pathlib import Path

from aiohttp import ClientSession
from aiofiles import open as aopen

from ..config import HEADERS, REQUESTS_LIMIT, CACHE_PATH
from .logger import logger


class Downloader:
    cache_path = CACHE_PATH
    attemps = 20

    def __init__(self):
        self.locker = asyncio.Semaphore(REQUESTS_LIMIT)
        if not self.cache_path.exists():
            self.cache_path.mkdir(parents=True)

    async def start(self):
        self.session = ClientSession(headers=HEADERS)

    async def stop(self):
        await self.session.close()

    async def request(self, method, url, *args, **kwargs):
        async with self.locker:
            for _ in range(self.attemps):
                async with self.session.request(method, url, *args, **kwargs) as resp:
                    if resp.status == 200:
                        return await resp.read()
                    else:
                        await asyncio.sleep(2)

    async def get(self, *args, **kwargs):
        return await self.cache("GET", *args, **kwargs)

    async def post(self, *args, **kwargs):
        return await self.cache("POST", *args, **kwargs)

    async def cache(self, method, url, *args, **kwargs):
        url_hash = md5(url.encode()).hexdigest()
        file_name = f"{url_hash}.cache"
        file_path = Path(self.cache_path, file_name)
        if file_path.exists():
            async with aopen(file_path, 'rb') as f:
                response_data = await f.read()
            logger.info(f"Url {url} read from {file_name} cache")
        else:
            response_data = await self.request(method, url, *args, **kwargs)
            if not response_data or b"Too Many Requests" in response_data:
                raise Exception("Not Data")
            async with aopen(file_path, 'wb') as f:
                await f.write(response_data)
            logger.info(f"Url {url} cached in {file_name} cache")
        return response_data