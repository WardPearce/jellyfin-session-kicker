from .env import MESSAGE_TIME_IN_MILLI
from .resources import Sessions


class JellySession:
    def __init__(self, id_: str) -> None:
        self._id = id_

    async def send_message(self, text: str,
                           timeout: int = MESSAGE_TIME_IN_MILLI) -> None:
        await Sessions.http.post(f"/Sessions/{self._id}/Message", json={
            "Text": text,
            "TimeoutMs": timeout
        })

    async def play(self, id_: str) -> None:
        await Sessions.http.post(
            f"/Sessions/{self._id}/Playing?playCommand=PlayNow&itemIds={id_}"
        )

    async def playstate(self, command: str) -> None:
        await Sessions.http.post(f"/Sessions/{self._id}/Playing/{command}")
