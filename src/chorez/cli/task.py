import itertools
import json
import sys
from enum import Enum
from typing import Self, override

import yaml
from tap import Tap

from chorez.chorez import Chorez
from chorez.models import Difficulty, Priority, Task

EXIT_SUCCESS = 0
EXIT_FAILURE = 1


class Format(str, Enum):
    PRETTY = "pretty"
    JSON = "json"
    YAML = "yaml"


class TaskShow(Tap):
    format: Format = Format.PRETTY
    filter: str = ""

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

    def run(self, args: Self, chorez: Chorez) -> int:
        tasks = chorez.db.list_tasks(args.filter)
        match args.format:
            case Format.PRETTY:
                print(f"Found {len(tasks)} tasks:")
                by_priority = itertools.groupby(tasks, lambda e: e.priority)
                for prio, group in by_priority:
                    group = list(group)
                    print(f"\tPrio {prio.value} (count={len(group)})")
                    for task in group:
                        print(f"\t\t{task.pretty()}")
            case Format.JSON:
                task_dicts = [x.toDict() for x in tasks]
                print(json.dumps(task_dicts, sort_keys=True))
            case Format.YAML:
                print(yaml.dump(tasks, sort_keys=True))
        return EXIT_SUCCESS


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

    def run(self, args: Self, chorez: Chorez) -> int:
        task = Task(
            name=args.name,
            priority=args.priority,
            difficulty=args.difficulty,
            tags=args.tags,
        )
        chorez.db.save_task(task)
        print(f"Added {task.pretty()}")
        return EXIT_SUCCESS


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

    def run(self, args: Self, chorez: Chorez) -> int:
        tasks = chorez.db.list_tasks(f"id={args.id}")
        if len(tasks) == 0:
            print("Task not found", file=sys.stderr)
            return EXIT_FAILURE
        assert len(tasks) == 1
        task = tasks[0]
        assert task.id == args.id

        if args.name is not None and task.name != args.name:
            print(f"Changed name from {task.name!r} to {args.name!r}")
            task.name = args.name
        if args.priority is not None and task.priority != args.priority:
            print(
                f"Changed priority from {task.priority.value!r} to {args.priority.value!r}"
            )
            task.priority = args.priority
        if args.difficulty is not None and task.difficulty != args.difficulty:
            print(
                f"Changed difficulty from {task.difficulty.value!r} to {args.difficulty.value!r}"
            )
            task.difficulty = args.difficulty
        if args.tags is not None and task.tags != args.tags:
            # + prefix or no prefix -> candidate for adding
            # - prefix -> candidate for removing
            def should_add(tag: str) -> bool:
                if not tag.startswith("-"):
                    return tag.lstrip("+") in task.tags
                return False

            def should_remove(tag: str) -> bool:
                return tag.startswith("-")

            to_add = [tag.lstrip("+") for tag in args.tags if should_add(tag)]
            to_remove = [tag.lstrip("-") for tag in args.tags if should_remove(tag)]

            task.tags = [tag for tag in task.tags if tag not in to_remove]
            task.tags.extend(to_add)
            print(f"Changed tags from {task.tags!r} to {args.tags!r}")
        if args.desc is not None and task.desc != args.desc:
            print(f"Changed desc from {task.desc!r} to {args.desc!r}")
            task.desc = args.desc

        chorez.db.save_task(task)
        return EXIT_SUCCESS


class TaskRm(Tap):
    id: int  # pyright: ignore[reportUninitializedInstanceVariable]

    @override
    def configure(self) -> None:
        self.add_argument("--id", "-i", dest="id", help="The task to remove's ID")  # pyright: ignore[reportUnknownMemberType]

        self.set_defaults(run=self.run)

    def run(self, args: Self, chorez: Chorez) -> int:
        filter = f"id={args.id}"
        tasks = chorez.db.list_tasks(filter)
        if len(tasks) == 0:
            print(f"Task with ID {args.id} not found")
            return EXIT_FAILURE
        assert len(tasks) == 1
        assert chorez.db.clear_tasks(filter) == 1
        print(f"Removed task: {tasks[0].pretty()}")
        return EXIT_SUCCESS


class TaskCLI(Tap):
    @override
    def configure(self) -> None:
        self.add_subparsers(dest="subcommand", required=True, help="task subparsers")  # pyright: ignore[reportUnknownMemberType]
        self.add_subparser("show", TaskShow)  # pyright: ignore[reportUnknownMemberType]
        self.add_subparser("add", TaskAdd)  # pyright: ignore[reportUnknownMemberType]
        self.add_subparser("edit", TaskEdit)  # pyright: ignore[reportUnknownMemberType]
        self.add_subparser("rm", TaskRm)  # pyright: ignore[reportUnknownMemberType]
