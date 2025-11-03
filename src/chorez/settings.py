from enum import Enum
from typing import ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseKind(Enum):
    SQLITE = "sqlite"


class SqliteDatabaseSettings(BaseSettings):
    database: str = "sqlite.db"
    """
    You can use ":memory:" to open a database connection to a database that
    resides in RAM instead of on disk.
    """

    tasks_table_name: str = "tasks"

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CHOREZ_DB_SQLITE_",
    )


class DatabaseSettings(BaseSettings):
    kind: DatabaseKind = DatabaseKind.SQLITE
    sqlite: SqliteDatabaseSettings = SqliteDatabaseSettings()

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CHOREZ_DB_",
    )


class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CHOREZ_",
    )


settings = Settings()
