import datetime
from enum import Enum
from typing import final

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class Difficulty(Enum):
    CHALLENGING = "challenging"
    HARD = "hard"
    MEDIUM = "medium"
    EASY = "easy"
    BREEZE = "breeze"


class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INSIGNIFICANT = "insignificant"


class Base(MappedAsDataclass, DeclarativeBase):  # pyright: ignore[reportUnsafeMultipleInheritance]
    pass


@final
class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = tuple(
        sa.UniqueConstraint(
            "name", "source_id", "source_url", "source_tags", name="uq_task_identity"
        )
    )

    id: Mapped[int | None] = mapped_column(
        primary_key=True,
        init=False,
        repr=True,
    )

    name: Mapped[str] = mapped_column(nullable=False)
    priority: Mapped[Priority] = mapped_column(
        sa.Enum(Priority),
        default=Priority.MEDIUM,
        nullable=False,
    )
    difficulty: Mapped[Difficulty] = mapped_column(
        sa.Enum(Difficulty),
        default=Difficulty.MEDIUM,
        nullable=False,
    )
    tags: Mapped[list[str]] = mapped_column(
        sa.JSON(),
        default_factory=list,
        nullable=False,
    )
    desc: Mapped[str] = mapped_column(
        default="",
        nullable=False,
    )

    is_imported: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    source_id: Mapped[str | None] = mapped_column(
        default=None,
        nullable=True,
    )
    source_tags: Mapped[list[str] | None] = mapped_column(
        sa.JSON(), default=None, nullable=True
    )
    source_url: Mapped[str | None] = mapped_column(
        default=None,
        nullable=True,
    )


@final
class TimeEntry(Base):
    __tablename__ = "time_logs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        init=False,
        repr=True,
    )

    start: Mapped[datetime.datetime]
    end: Mapped[datetime.datetime | None]

    def is_active(self) -> bool:
        return self.end is None
