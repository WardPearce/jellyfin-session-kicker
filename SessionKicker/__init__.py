import asyncio
import aiohttp
import secrets
import logging

from sys import stdout
from typing import List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

try:
    import uvloop
except ImportError:
    pass
else:
    try:
        uvloop.install()
    except Exception:
        pass

from .session import JellySession
from .http import server
from .env import (
    MAX_WATCH_TIME_IN_SECONDS, DONT_KICK_ITEM_TYPE,
    CHECK_DELAY_IN_SECONDS, JELLYFIN_API_KEY, JELLYFIN_API_URL,
    RESET_AFTER_IN_HOURS, WATCH_TIME_OVER_MSG, NOT_WHITELISTED_MSG,
    ITEM_ID_ON_SESSION_KICKED, DELETE_DEVICE_IF_NO_MEDIA_CONTROLS,
    MONGO_DB, MONGO_HOST, MONGO_PORT
)
from .resources import Sessions


logger = logging.getLogger("session-kicker")
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stdout)
logger.addHandler(consoleHandler)


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
        async with Sessions.http.get("/Sessions") as resp:
            return await resp.json()

    async def __stop_then_media(self, inter: JellySession,
                                session: dict) -> None:
        if "DisplayMessage" in session["Capabilities"]["SupportedCommands"]:
            await inter.send_message(WATCH_TIME_OVER_MSG)

        if (not session["Capabilities"]["SupportsMediaControl"]
                and DELETE_DEVICE_IF_NO_MEDIA_CONTROLS):
            # If media controls not supported, nuke the
            # device as a last resort.
            await Sessions.http.delete(
                f"/Devices?id={session['DeviceId']}"
            )
        else:
            await inter.playstate("stop")
            # Attempt to force stop encoding the video
            # for the session, as a backup for the stop command.
            await inter.stop_encoding(session["DeviceId"])

            if ITEM_ID_ON_SESSION_KICKED:
                await asyncio.sleep(2)
                await inter.play(
                    ITEM_ID_ON_SESSION_KICKED
                )

    async def __check(self) -> None:
        for session in await self._sessions():

            if "NowPlayingItem" not in session:
                continue

            item_type = session["NowPlayingItem"]["Type"].lower()
            if item_type in DONT_KICK_ITEM_TYPE:
                continue

            if session["PlayState"]["IsPaused"]:
                continue

            if (ITEM_ID_ON_SESSION_KICKED and ITEM_ID_ON_SESSION_KICKED ==
                    session["NowPlayingItem"]["Id"]):
                continue

            result = await Sessions.db.whitelist.find_one({
                "UserId": session["UserId"]
            })
            if result and item_type in result["MediaTypes"]:
                continue

            inter = JellySession(session["Id"])

            # Add check to ensure they are whitelisted.
            if session["UserId"] not in self._user_sessions:
                self._user_sessions[session["UserId"]] = 0
                asyncio.create_task(
                    inter.send_message(NOT_WHITELISTED_MSG)
                )

            if (self._user_sessions[session["UserId"]]
                    >= MAX_WATCH_TIME_IN_SECONDS):
                asyncio.create_task(
                    self.__stop_then_media(
                        inter, session
                    )
                )
                continue

            self._user_sessions[session["UserId"]] += (
                CHECK_DELAY_IN_SECONDS
            )

    async def close(self) -> None:
        await Sessions.http.close()
        await self._server.stop()

    async def run(self) -> None:
        Sessions.http = aiohttp.ClientSession(
            base_url=JELLYFIN_API_URL,
            headers={
                "X-Emby-Authorization": (
                    'MediaBrowser Client="Jellyfin Session Timer",'
                    'Device="aiohttp", DeviceId="1", Version="0.0.1"'
                    f', Token="{JELLYFIN_API_KEY}"')
            },
        )

        Sessions.db = AsyncIOMotorClient(
            MONGO_HOST, MONGO_PORT
        )[MONGO_DB]

        result = await Sessions.db.misc.find_one({
            "type": "key"
        })
        if not result:
            http_key = secrets.token_urlsafe(40)
            await Sessions.db.misc.insert_one({
                "value": http_key,
                "type": "key"
            })
        else:
            http_key = result["value"]

        logger.debug(f"Your basic auth: {http_key}\n")

        self._server = await server()
        await self._server.start()

        while True:  # Loop forever
            await self.__check()
            if RESET_AFTER_IN_HOURS and datetime.now() >= self._next_wipe_in:
                self.__set_next_wipe()
                self._user_sessions = {}

            await asyncio.sleep(CHECK_DELAY_IN_SECONDS)
