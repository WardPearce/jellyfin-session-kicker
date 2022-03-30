import os

from tinydb import TinyDB

if not os.path.exists("./data"):
    os.mkdir("./data")

DB = TinyDB("./data/session_kicker.json")
