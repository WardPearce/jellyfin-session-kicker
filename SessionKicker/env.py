import os

JELLYFIN_API_KEY = os.environ["JELLYFIN_API_KEY"]
JELLYFIN_API_URL = os.environ["JELLYFIN_API_URL"]

MEDIA_TYPE_TIME = os.getenv("MEDIA_TYPE_TIME", "episode").split(",")
CHECK_DELAY_IN_SECONDS = float(os.getenv("CHECK_DELAY_IN_SECONDS", 10.0))
MESSAGE_TIME_IN_MILLI = int(os.getenv("MESSAGE_TIME_IN_MILLI", 60000))
MAX_WATCH_TIME_IN_SECONDS = float(os.getenv("MAX_WATCH_TIME_IN_SECONDS", 50.0))

# Blank to disable
ITEM_ON_SESSION_KICKED = os.getenv("ITEM_ON_SESSION_KICKED", None)
ITEM_TYPE_ON_SESSION_KICKED = os.getenv("ITEM_TYPE_ON_SESSION_KICKED", None)
ITEM_NAME_ON_SESSION_KICKED = os.getenv("ITEM_TYPE_ON_SESSION_KICKED", None)

WATCH_TIME_OVER_MSG = os.getenv(
    "WATCH_TIME_OVER",
    "You aren't whitelisted for unlimited watch time."
)
NOT_WHITELISTED_MSG = os.getenv(
    "NOT_WHITELISTED",
    "You have used up your watch time."
)

# leave as 0 to disable
RESET_AFTER_IN_HOURS = float(os.getenv("RESET_AFTER_IN_HOURS", 24))

assert (
    ITEM_ON_SESSION_KICKED and ITEM_TYPE_ON_SESSION_KICKED
    and ITEM_NAME_ON_SESSION_KICKED
) or not ITEM_ON_SESSION_KICKED, "Required Item envs not provided."
