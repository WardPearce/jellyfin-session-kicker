import base64
import binascii
import bcrypt

from tinydb import where
from aiohttp import web
from json import JSONDecodeError

from .db import DB
from .env import HTTP_HOST, HTTP_PORT


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

    # Slow way of validating things, but shouldn't matter.
    key = DB.table("misc").search(
        where("type") == "key"  # type: ignore
    )[0]["value"]
    if not bcrypt.checkpw(given_key.encode(),
                          bcrypt.hashpw(key.encode(), bcrypt.gensalt())):
        return web.json_response({
            "error": INVALID_AUTH
        }, status=403)

    try:
        json = await request.json()
    except JSONDecodeError:
        return web.json_response({
            "error": "Invalid json payload"
        }, status=400)

    if "UserId" not in json:
        return web.json_response({
            "error": "UserId required"
        })

    if request.method == "POST":
        DB.table("whitelist").insert({
            "UserId": json["UserId"]
        })
    elif request.method == "DELETE":
        DB.table("whitelist").remove(where("UserId") == json["UserId"])
    else:
        return web.json_response({
            "error": "Request method not supported"
        })

    return web.json_response({
        "success": True
    })


async def server() -> web.TCPSite:
    server = web.Server(incoming)  # type: ignore
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, HTTP_HOST, HTTP_PORT)
    return site
