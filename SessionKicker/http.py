import base64
import binascii
import bcrypt

from aiohttp import web
from json import JSONDecodeError

from .env import HTTP_HOST, HTTP_PORT
from .resources import Sessions
from .misc import generate_root_key


INVALID_AUTH = "Invalid basic auth credentials"


async def incoming(request: web.BaseRequest):
    if "Authorization" not in request.headers:
        return web.json_response({
            "error": "Authorization header not provided",
        }, status=400)

    auth = request.headers["Authorization"]
    try:
        scheme, credentials = auth.split()
        if scheme.lower() != "basic":
            return
        decoded = base64.b64decode(credentials).decode("ascii")
    except (ValueError, UnicodeDecodeError, binascii.Error):
        return web.json_response({
            "error": INVALID_AUTH
        }, status=403)

    _, _, given_key = decoded.partition(":")

    result = await Sessions.db.misc.find_one({
        "type": "key"
    })
    if not bcrypt.checkpw(given_key.encode(),
                          bcrypt.hashpw(result["value"].encode(),
                                        bcrypt.gensalt())):
        return web.json_response({
            "error": INVALID_AUTH
        }, status=403)

    if request.method in ("POST", "DELETE"):
        try:
            json = await request.json()
        except JSONDecodeError:
            return web.json_response({
                "error": "Invalid json payload"
            }, status=400)

        if "UserId" not in json or not isinstance(json["UserId"], str):
            return web.json_response({
                "error": "UserId required"
            }, status=400)

        if ("MediaTypes" not in json or not
                isinstance(json["MediaTypes"], list)):
            return web.json_response({
                "error": "MediaTypes required"
            }, status=400)

        media_types = [
            media_type.lower()
            for media_type in json["MediaTypes"]
        ]

        if request.method == "POST":
            await Sessions.db.whitelist.update_one({
                "UserId": json["UserId"]
            }, {
                "$push": {"MediaTypes": {"$each": media_types}}
            }, upsert=True)
        else:
            await Sessions.db.whitelist.update_one({
                "UserId": json["UserId"]
            }, {
                "$pull": {"MediaTypes": {"$in": media_types}}
            })

        return web.json_response({
            "success": True
        })
    elif request.method == "GET":
        result = []
        async for row in Sessions.db.whitelist.find():
            result.append({
                "UserId": row["UserId"],
                "MediaTypes": row["MediaTypes"]
            })
        return web.json_response(result)
    elif request.method == "PATCH":
        http_key = await generate_root_key()
        return web.json_response({
            "key": http_key
        })
    else:
        return web.json_response({
            "error": "Request method not supported"
        }, status=405)


async def server() -> web.TCPSite:
    server = web.Server(incoming)  # type: ignore
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, HTTP_HOST, HTTP_PORT)
    return site
