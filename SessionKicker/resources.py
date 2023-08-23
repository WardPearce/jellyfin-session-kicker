import aiohttp
from motor import motor_asyncio


class Sessions:
    http: aiohttp.ClientSession
    db: motor_asyncio.AsyncIOMotorDatabase
