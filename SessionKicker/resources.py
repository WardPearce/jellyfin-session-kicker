import aiohttp
from motor.motor_asyncio import AsyncIOMotorCollection


class Sessions:
    http: aiohttp.ClientSession
    db: AsyncIOMotorCollection
