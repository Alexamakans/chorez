import datetime
from enum import Enum
from typing import Any, final

import sqlalchemy as sa
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)


class Difficulty(str, Enum):
    CHALLENGING = "challenging"
    HARD = "hard"
    MEDIUM = "medium"
    EASY = "easy"
    BREEZE = "breeze"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INSIGNIFICANT = "insignificant"


class Base(MappedAsDataclass, DeclarativeBase):  # pyright: ignore[reportUnsafeMultipleInheritance]
    """
    Add some default properties and methods to the SQLAlchemy declarative base.
    """

    @property
    def columns(self):
        return [c.name for c in self.__table__.columns]  # pyright: ignore[reportAny]

    @property
    def columnitems(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        return dict([(c, getattr(self, c)) for c in self.columns])  # pyright: ignore[reportAny]

    def toDict(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        return self.columnitems


@final
class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = tuple(
        sa.UniqueConstraint("name", "source_id", "source_url", name="uq_task_identity")
    )

    id: Mapped[int | None] = mapped_column(
        primary_key=True,
        init=False,
        repr=True,
    )
    name: Mapped[str] = mapped_column(nullable=False)

    time_entries: Mapped[list["TimeEntry"]] = relationship(
        init=False,
        back_populates="task",
        default_factory=list,
        lazy="selectin",
    )

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
    source_url: Mapped[str | None] = mapped_column(
        default=None,
        nullable=True,
    )

    def pretty(self) -> str:
        return f"Task #{self.id} [{self.name}] [Diff: {self.difficulty.value}, Prio: {self.priority.value}]"

    def pretty_with_times(self, indent: int = 0) -> str:
        assert indent >= 0
        lines: list[str] = []
        lines.append(f"{'\t' * indent}{self.pretty()}")
        for time_entry in self.time_entries:
            lines.append(f"{'\t' * (indent + 1)}{time_entry.pretty()}")
        return "\n".join(lines)


@final
class TimeEntry(Base):
    __tablename__ = "time_entries"

    id: Mapped[int | None] = mapped_column(
        primary_key=True,
        init=False,
        repr=True,
    )

    task_id: Mapped[int] = mapped_column(
        sa.ForeignKey(f"{Task.__tablename__}.id", ondelete="CASCADE"),  # pyright: ignore[reportAny]
    )
    task: Mapped["Task"] = relationship(
        init=False,
        back_populates="time_entries",
        lazy="selectin",
    )
    start: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(),
        nullable=False,
        default_factory=datetime.datetime.now,
    )
    end: Mapped[datetime.datetime | None] = mapped_column(
        sa.DateTime(),
        nullable=True,
        default=None,
    )

    def duration(self) -> datetime.timedelta:
        if self.end is None:
            return datetime.datetime.now() - self.start
        return self.end - self.start

    def pretty_with_task(self) -> str:
        lines: list[str] = []
        lines.append(self.task.pretty() if self.task else f"Task #{self.task_id}")
        lines.append(f"\t{self.pretty()}")
        return "\n".join(lines)

    def pretty(self) -> str:
        start = self.start - datetime.timedelta(microseconds=self.start.microsecond)
        end = (
            None
            if self.end is None
            else self.end - datetime.timedelta(microseconds=self.end.microsecond)
        )

        duration = self.duration()
        duration = duration - datetime.timedelta(microseconds=duration.microseconds)
        return f"{start} -> {end if end else 'active'}: {duration}"
