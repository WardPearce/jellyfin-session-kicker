import os

JELLYFIN_API_KEY = os.environ["JELLYFIN_API_KEY"]
JELLYFIN_API_URL = os.environ["JELLYFIN_API_URL"]

DONT_KICK_ITEM_TYPE = os.getenv("DONT_KICK_ITEM_TYPE", "movie").split(",")
CHECK_DELAY_IN_SECONDS = float(os.getenv("CHECK_DELAY_IN_SECONDS", 10.0))
MESSAGE_TIME_IN_MILLI = int(os.getenv("MESSAGE_TIME_IN_MILLI", 60000))
MAX_WATCH_TIME_IN_SECONDS = float(os.getenv("MAX_WATCH_TIME_IN_SECONDS", 50.0))

# Blank to disable
ITEM_ID_ON_SESSION_KICKED = os.getenv("ITEM_ID_ON_SESSION_KICKED", None)

WATCH_TIME_OVER_MSG = os.getenv(
    "WATCH_TIME_OVER",
    "You have used up your watch time."
)
NOT_WHITELISTED_MSG = os.getenv(
    "NOT_WHITELISTED",
    "You aren't whitelisted for unlimited watch time."
)

# leave as 0 to disable
RESET_AFTER_IN_HOURS = float(os.getenv("RESET_AFTER_IN_HOURS", 24))

HTTP_HOST = os.getenv("HTTP_HOST", "localhost")
HTTP_PORT = int(os.getenv("HTTP_PORT", 8887))

MONGO_DB = os.getenv("MONGO_DB", "session_timer")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
