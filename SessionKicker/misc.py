import secrets

from .resources import Sessions


async def generate_root_key() -> str:
    http_key = secrets.token_urlsafe(40)
    await Sessions.db.misc.update_one(
        {"type": "key"},
        {"$set": {"value": http_key}},
        upsert=True
    )
    return http_key
