import os

from aiotinydb import AIOTinyDB

if not os.path.exists("./data"):
    os.mkdir("./data")

DB = AIOTinyDB("./data/session_kicker.json")
