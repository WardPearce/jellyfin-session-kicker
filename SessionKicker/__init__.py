import asyncio
import aiohttp

from typing import List
from datetime import datetime, timedelta

try:
    import uvloop
except ImportError:
    pass
else:
    try:
        uvloop.install()
    except Exception:
        pass

from .session import Session
from .env import (
    MEDIA_TYPE_TIME, MAX_WATCH_TIME_IN_SECONDS, ITEM_ON_SESSION_KICKED,
    CHECK_DELAY_IN_SECONDS, JELLYFIN_API_KEY, JELLYFIN_API_URL,
    ITEM_TYPE_ON_SESSION_KICKED, ITEM_NAME_ON_SESSION_KICKED,
    RESET_AFTER_IN_HOURS, WATCH_TIME_OVER_MSG, NOT_WHITELISTED_MSG
)


class Kicker:
    _http: aiohttp.ClientSession
    _user_sessions = {}

    def __init__(self) -> None:
        self.__set_next_wipe()

    def __set_next_wipe(self) -> None:
        self._next_wipe_in = datetime.now() + timedelta(
            hours=RESET_AFTER_IN_HOURS
        )

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
                asyncio.create_task(inter.send_message(WATCH_TIME_OVER_MSG))

            if (self._user_sessions[session["UserId"]]
                    >= MAX_WATCH_TIME_IN_SECONDS):
                asyncio.gather(
                    inter.send_message(NOT_WHITELISTED_MSG),
                    inter.playstate("stop") if not ITEM_ON_SESSION_KICKED
                    else inter.view(
                        ITEM_TYPE_ON_SESSION_KICKED,  # type: ignore
                        ITEM_ON_SESSION_KICKED,
                        ITEM_NAME_ON_SESSION_KICKED  # type: ignore
                    )
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
                "X-Emby-Authorization": (
                    'MediaBrowser Client="Jellyfin Session Timer",'
                    'Device="aiohttp", DeviceId="1", Version="0.0.1"'
                    f', Token="{JELLYFIN_API_KEY}"')
            },
        )

        while True:  # Loop forever
            await self.__check()
            if RESET_AFTER_IN_HOURS and datetime.now() >= self._next_wipe_in:
                self.__set_next_wipe()
                self._user_sessions = {}

            await asyncio.sleep(CHECK_DELAY_IN_SECONDS)
