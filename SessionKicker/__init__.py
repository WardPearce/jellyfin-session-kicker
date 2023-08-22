import asyncio
import aiohttp
import logging

from sys import stdout
from typing import List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from json import JSONDecodeError

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
    ACCRUE_BY_DEVICE_INSTEAD_OF_USER, MONGO_DB, MONGO_HOST, MONGO_PORT
)
from .resources import Sessions
from .misc import generate_root_key


logger = logging.getLogger("session-kicker")
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stdout)
logger.addHandler(consoleHandler)


class Kicker:
    _http: aiohttp.ClientSession
    _user_sessions = {}
    _id_type = "DeviceId" if ACCRUE_BY_DEVICE_INSTEAD_OF_USER else "UserId"

    def __init__(self) -> None:
        self.__set_next_wipe()

    def __set_next_wipe(self) -> None:
        self._next_wipe_in = datetime.now() + timedelta(
            hours=RESET_AFTER_IN_HOURS
        )

    async def _sessions(self) -> List[dict]:
        async with Sessions.http.get("/Sessions") as resp:
            if resp.status == 200:
                try:
                    return await resp.json()
                except (JSONDecodeError, aiohttp.ContentTypeError):
                    logger.warn((
                        "Jellyfin didn't respond with json"
                        ", most likely your `JELLYFIN_API_KEY`"
                        " or `JELLYFIN_API_URL` is incorrect"
                    ))

            return []

    async def __stop_then_media(self, inter: JellySession,
                                session: dict) -> None:
        if "DisplayMessage" in session["SupportedCommands"]:
            await inter.send_message(WATCH_TIME_OVER_MSG)

        if (not session["SupportsMediaControl"]
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

            if (ITEM_ID_ON_SESSION_KICKED and "PlayMediaSource" in
                    session["SupportedCommands"]):
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

            count = await Sessions.db.whitelist.count_documents({
                self._id_type: session[self._id_type],
                "MediaTypes": item_type
            })
            if count > 0:
                continue

            inter = JellySession(session["Id"])

            if session[self._id_type] not in self._user_sessions:
                self._user_sessions[session[self._id_type]] = 0
                if "DisplayMessage" in session["SupportedCommands"]:
                    asyncio.create_task(
                        inter.send_message(NOT_WHITELISTED_MSG)
                    )

            if (self._user_sessions[session[self._id_type]]
                    >= MAX_WATCH_TIME_IN_SECONDS):
                asyncio.create_task(
                    self.__stop_then_media(
                        inter, session
                    )
                )
                continue

            self._user_sessions[session[self._id_type]] += (
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
            http_key = await generate_root_key()
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
