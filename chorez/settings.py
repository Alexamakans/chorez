from enum import Enum
from typing import ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskSettings(BaseSettings):
    breeze_difficulty_name: str = "breeze"
    easy_difficulty_name: str = "easy"
    medium_difficulty_name: str = "medium"
    hard_difficulty_name: str = "hard"
    challenging_difficulty_name: str = "challenging"

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CHOREZ_TASK_",
    )


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
    task: TaskSettings = TaskSettings()
    database: DatabaseSettings = DatabaseSettings()

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CHOREZ_",
    )


settings = Settings()
