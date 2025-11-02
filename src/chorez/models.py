from enum import Enum
from typing import final

from sqlalchemy import JSON
from chorez.settings import settings

from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


type TaskId = int
type Tag = str


class Difficulty(Enum):
    BREEZE = settings.task.breeze_difficulty_name
    EASY = settings.task.easy_difficulty_name
    MEDIUM = settings.task.medium_difficulty_name
    HARD = settings.task.hard_difficulty_name
    CHALLENGING = settings.task.challenging_difficulty_name


class Base(MappedAsDataclass, DeclarativeBase):  # pyright: ignore[reportUnsafeMultipleInheritance]
    pass


@final
class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[TaskId] = mapped_column(primary_key=True, init=False, repr=True)

    name: Mapped[str]
    tags: Mapped[list[Tag]] = mapped_column(JSON())
    description: Mapped[str]
