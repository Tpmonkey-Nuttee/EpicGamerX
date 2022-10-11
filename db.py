import pytz
import json
import datetime
from typing import Any, NoReturn



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
    def __init__(self) -> None:
        self._data = json.load(open("db.json", "r"))
    
    def loads(self, key: str, default: Any) -> Any:
        return self._data.get(key, default)

    async def load(self, key: str, default: Any) -> Any:
        return self.loads(key, default)
    
    def dumps(self, key: str, value: Any) -> NoReturn:
        self._data[key] = value
        
        json.dump(open("db.json", "w"))
    
    async def dump(self, key: str, value: Any) -> NoReturn:
        self.dumps(key, value)