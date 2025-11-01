from enum import Enum


type TaskId = int
type Tag = str


class Difficulty(Enum):
    BREEZE = "breeze"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    CHALLENGING = "challenging"


class Task:
    id: TaskId
    tags: list[Tag]
