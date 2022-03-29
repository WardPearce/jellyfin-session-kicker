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

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

# Include [0]["AdditionalUsers"]
# [0]["NowPlayingItem"]["Type"] == "Episode"
# [0]["PlayState"]["IsPaused"] is False
# [0]["UserId"] not in paying_users
# [0]["LastActivityDate"]


class SessionTimer:
    _http: aiohttp.ClientSession
    _user_sessions = {}

    async def _sessions(self) -> List[dict]:
        async with self._http.get("/Sessions") as resp:
            return await resp.json()

    async def _send_message(self, session_id: str,
                            text: str, timeout: int) -> None:
        await self._http.post(f"/Sessions/{session_id}/Message", json={
            "Text": text,
            "TimeoutMs": timeout
        })

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

            # Add check to ensure they are whitelisted.
            if session["UserId"] not in self._user_sessions:
                self._user_sessions[session["UserId"]] = 0
                await self._send_message(
                    session["Id"],
                    "You aren't whitelisted for unlimited watch time",
                    MESSAGE_TIME_IN_MILLI
                )

            self._user_sessions[session["UserId"]] += CHECK_DELAY_IN_SECONDS

            print(session["NowPlayingItem"]["Name"])
            print(self._user_sessions[session["UserId"]])

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


try:
    asyncio.run(SessionTimer().run())
except KeyboardInterrupt:
    pass
