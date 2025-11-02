from enum import Enum
from typing import TypedDict
from chorez.settings import settings


type TaskId = int
type Tag = str


class Difficulty(Enum):
    BREEZE = settings.task.breeze_difficulty_name
    EASY = settings.task.easy_difficulty_name
    MEDIUM = settings.task.medium_difficulty_name
    HARD = settings.task.hard_difficulty_name
    CHALLENGING = settings.task.challenging_difficulty_name


class Task(TypedDict):
    id: TaskId | None
    tags: list[Tag]
    name: str
    description: str
