from typing import final

from chorez.database import Database
from chorez.settings import settings


@final
class Chorez:
    def __init__(self) -> None:
        self.db = Database(settings.database.sqlite.database)
