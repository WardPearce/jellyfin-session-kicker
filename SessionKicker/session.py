import aiohttp

from .env import MESSAGE_TIME_IN_MILLI


class Session:
    def __init__(self, id_: str, http: aiohttp.ClientSession) -> None:
        self._id = id_
        self._http = http

    async def send_message(self, text: str,
                           timeout: int = MESSAGE_TIME_IN_MILLI) -> None:
        await self._http.post(f"/Sessions/{self._id}/Message", json={
            "Text": text,
            "TimeoutMs": timeout
        })

    async def play(self, id_: str) -> None:
        await self._http.post(
            f"/Sessions/{self._id}/Playing?playCommand=PlayNow&itemIds={id_}"
        )

    async def playstate(self, command: str) -> None:
        await self._http.post(f"/Sessions/{self._id}/Playing/{command}")
