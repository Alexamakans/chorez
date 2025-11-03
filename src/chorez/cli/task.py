import json
import sys
from enum import Enum
from typing import Self, override

import yaml
from tap import Tap

from chorez.chorez import Chorez
from chorez.models import Difficulty, Priority, Task


class Format(Enum):
    PRETTY = "pretty"
    JSON = "json"
    YAML = "yaml"


class TaskShow(Tap):
    format: Format = Format.PRETTY
    filter: str = "1=1"

    @override
    def configure(self) -> None:
        self.add_argument(  # pyright: ignore[reportUnknownMemberType]
            "--format",
            choices=[m for m in Format],
            dest="format",
            help=f"Format to output as: {', '.join(m.value for m in Format)}",
        )
        self.add_argument("--filter", dest="filter", help="sqlalchemy where clause")  # pyright: ignore[reportUnknownMemberType]
        self.set_defaults(run=self.run)

    def run(self, args: Self, chorez: Chorez) -> None:
        tasks = chorez.db.list_tasks(args.filter)
        match args.format:
            case Format.PRETTY:
                print(f"Found {len(tasks)} tasks:")
                for task in tasks:
                    print(f"\t{task!r}")
            case Format.JSON:
                print(json.dumps(tasks))
            case Format.YAML:
                print(yaml.dump(tasks))


class TaskAdd(Tap):
    name: str  # pyright: ignore[reportUninitializedInstanceVariable]
    priority: Priority = Priority.MEDIUM
    difficulty: Difficulty = Difficulty.MEDIUM
    tags: list[str] = []
    desc: str = ""

    @override
    def configure(self) -> None:
        self.add_argument("--name", "-n", dest="name", help="Task title/name")  # pyright: ignore[reportUnknownMemberType]
        self.add_argument(  # pyright: ignore[reportUnknownMemberType]
            "--priority",
            "-p",
            choices=[m for m in Priority],
            dest="priority",
            help=f"Priority ({', '.join(m.value for m in Priority)})",
        )
        self.add_argument(  # pyright: ignore[reportUnknownMemberType]
            "--difficulty",
            "-d",
            choices=[m.value for m in Difficulty],
            dest="difficulty",
            help=f"Difficulty ({', '.join(m.value for m in Difficulty)})",
        )
        self.add_argument(  # pyright: ignore[reportUnknownMemberType]
            "--tags",
            "-t",
            nargs="+",
            dest="tags",
            help="One or more tags (space-separated)",
        )

        self.add_argument(  # pyright: ignore[reportUnknownMemberType]
            "--desc",
            "-D",
            dest="desc",
            help="Description",
        )

        self.set_defaults(run=self.run)

    def run(self, args: Self, chorez: Chorez) -> None:
        task = Task(
            name=args.name,
            priority=args.priority,
            difficulty=args.difficulty,
            tags=args.tags,
        )
        chorez.db.save_task(task)


class TaskEdit(Tap):
    id: int  # pyright: ignore[reportUninitializedInstanceVariable]

    name: str | None = None
    priority: Priority | None = None
    difficulty: Difficulty | None = None
    tags: list[str] | None = None
    desc: str | None = None

    @override
    def configure(self) -> None:
        super().configure()
        self.add_argument(  # pyright: ignore[reportUnknownMemberType]
            "--id",
            "-i",
            dest="id",
            help="ID of the task to edit",
        )

        self.add_argument("name", nargs="?", help="Task title/name")  # pyright: ignore[reportUnknownMemberType]
        self.add_argument("--name", "-n", dest="name", help="Task title/name")  # pyright: ignore[reportUnknownMemberType]
        self.add_argument(  # pyright: ignore[reportUnknownMemberType]
            "--priority",
            "-p",
            choices=[m for m in Priority],
            dest="priority",
            help=f"Priority ({', '.join(m.value for m in Priority)})",
        )
        self.add_argument(  # pyright: ignore[reportUnknownMemberType]
            "--difficulty",
            "-d",
            choices=[m for m in Difficulty],
            dest="difficulty",
            help=f"Difficulty ({', '.join(m.value for m in Difficulty)})",
        )
        self.add_argument(  # pyright: ignore[reportUnknownMemberType]
            "--tags",
            "-t",
            nargs="+",
            dest="tags",
            help="One or more tags (space-separated)",
        )

        self.add_argument(  # pyright: ignore[reportUnknownMemberType]
            "--desc",
            "-D",
            dest="desc",
            help="Description",
        )

        self.set_defaults(run=self.run)

    def run(self, args: Self, chorez: Chorez) -> None:
        tasks = chorez.db.list_tasks(f"id={args.id}")
        if len(tasks) == 0:
            print("Task not found", file=sys.stderr)
            return
        assert len(tasks) == 1
        task = tasks[0]
        assert task.id == args.id

        if args.name is not None and task.name != args.name:
            print(f"Changed name from {task.name!r} to {args.name!r}")
            task.name = args.name
        if args.priority is not None and task.priority != args.priority:
            print(f"Changed priority from {task.priority!r} to {args.priority!r}")
            task.priority = args.priority
        if args.difficulty is not None and task.difficulty != args.difficulty:
            print(f"Changed difficulty from {task.difficulty!r} to {args.difficulty!r}")
            task.difficulty = args.difficulty
        if args.tags is not None and task.tags != args.tags:
            print(f"Changed tags from {task.tags!r} to {args.tags!r}")
            task.tags = args.tags
        if args.desc is not None and task.desc != args.desc:
            print(f"Changed desc from {task.desc!r} to {args.desc!r}")
            task.desc = args.desc

        chorez.db.save_task(task)


class TaskCLI(Tap):
    @override
    def configure(self) -> None:
        self.add_subparsers(dest="subcommand", required=True, help="task subparsers")  # pyright: ignore[reportUnknownMemberType]
        self.add_subparser("show", TaskShow)  # pyright: ignore[reportUnknownMemberType]
        self.add_subparser("add", TaskAdd)  # pyright: ignore[reportUnknownMemberType]
        self.add_subparser("edit", TaskEdit)  # pyright: ignore[reportUnknownMemberType]
