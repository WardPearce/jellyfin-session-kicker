import asyncio
import aiohttp
import os

from typing import List

try:
    import uvloop
except ImportError:
    pass
else:
    try:
        uvloop.install()
    except Exception:
        pass


JELLYFIN_API_KEY = os.environ["JELLYFIN_API_KEY"]
JELLYFIN_API_URL = os.environ["JELLYFIN_API_URL"]

MEDIA_TYPE_TIME = os.getenv("MEDIA_TYPE_TIME", "episode").split(",")
CHECK_DELAY_IN_SECONDS = float(os.getenv("CHECK_DELAY_IN_SECONDS", 10.0))
MESSAGE_TIME_IN_MILLI = int(os.getenv("MESSAGE_TIME_IN_MILLI", 60000))
MAX_WATCH_TIME_IN_SECONDS = float(os.getenv("MAX_WATCH_TIME_IN_SECONDS", 50.0))

# [0]["UserId"] not in paying_users


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

    async def playstate(self, command: str) -> None:
        await self._http.post(f"/Sessions/{self._id}/Playing/{command}")


class Kicker:
    _http: aiohttp.ClientSession
    _user_sessions = {}

    async def _sessions(self) -> List[dict]:
        async with self._http.get("/Sessions") as resp:
            return await resp.json()

    async def __check(self) -> None:
        for session in await self._sessions():
            if ("NowPlayingItem" not in session or
                session["NowPlayingItem"]["Type"].lower()
                    not in MEDIA_TYPE_TIME):
                continue

            if session["PlayState"]["IsPaused"]:
                continue

            # Placeholder for early stage testing
            if session["NowPlayingItem"]["Name"] != "Manhunt":
                continue

            inter = Session(session["Id"], self._http)

            # Add check to ensure they are whitelisted.
            if session["UserId"] not in self._user_sessions:
                self._user_sessions[session["UserId"]] = 0
                asyncio.create_task(inter.send_message(
                    "You aren't whitelisted for unlimited watch time.",
                ))

            if (self._user_sessions[session["UserId"]]
                    >= MAX_WATCH_TIME_IN_SECONDS):
                asyncio.gather(
                    inter.send_message("You have used up your watch time."),
                    inter.playstate("stop")
                )
                continue

            self._user_sessions[session["UserId"]] += CHECK_DELAY_IN_SECONDS

            print(session["NowPlayingItem"]["Name"])
            print(self._user_sessions[session["UserId"]])

    async def close(self) -> None:
        await self._http.close()

    async def run(self) -> None:
        self._http = aiohttp.ClientSession(
            base_url=JELLYFIN_API_URL,
            headers={
                "X-Emby-Authorization": f'MediaBrowser Client="Jellyfin Session Timer", Device="aiohttp", DeviceId="1", Version="0.0.1", Token="{JELLYFIN_API_KEY}"'  # noqa: E501
            },
        )

        while True:  # Loop forever
            await self.__check()
            await asyncio.sleep(CHECK_DELAY_IN_SECONDS)


if __name__ == "__main__":
    kicker = Kicker()

    try:
        asyncio.run(kicker.run())
    except KeyboardInterrupt:
        print("\nPlease wait while sessions are cleaned up")
        asyncio.run(kicker.close())
