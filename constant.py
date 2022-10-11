# Bot Backend
# Made by Tpmonkey
# Credit: Repl.it database

import pytz
import logging
import datetime
from typing import Any

from replit import db

log = logging.getLogger(__name__)

def today(raw=False) -> datetime.datetime:
    # Return today date/time
    r = pytz.utc.localize(datetime.datetime.utcnow()).astimezone(
        pytz.timezone("Etc/GMT-1"))
    if not raw:
        r = str(r)[:10].strip()
    return r

def today_th(raw=False) -> datetime.datetime:
    # Return today date/time
    r = pytz.utc.localize(datetime.datetime.utcnow()).astimezone(
        pytz.timezone("Etc/GMT-7"))
    if not raw:
        r = str(r)[:10].strip()
    return r

class Database:
    async def load(self, key: str, return_to: Any = None) -> str:
        # Load data from database
        try:
            r = db[key]
        except:
            # log.trace(f"Unable to load requested data from the database, Key: {key} ({type(key)})")
            return return_to
        # log.trace(f"Loaded data from database, Key: {key}")
        return r

    async def dump(self, key: str, value: Any) -> bool:
        # Dump data to database
        try:
            db[key] = value
        except:
            """log.warning(
                str(
                    f"Unable to dump data"
                    f"Key: {key} ({type(key)})"
                    f"Value: {value} ({type(value)})"
                    f"with an error: \n{e}"
                )
            )"""
            return False
        """log.trace(
            str(
            "Dumped data to the database succesfully"
            f"Key: {key} ({type(key)})"
            f"Value: ({type(value)})" 
            )
        )"""
        return True

    def loads(self, key: str, return_to: Any = None) -> Any:
        try: 
            return db[key]
        except KeyError:
            return return_to
    
    def dumps(self, key: str, value: Any) -> bool:
        try:
            db[key] = value
        except: return False
        return True