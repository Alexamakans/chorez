import sys
from datetime import datetime
from typing import Any, Self, override

import dateparser
from tap import Tap

from chorez.chorez import Chorez
from chorez.cli.constants import EXIT_FAILURE, EXIT_SUCCESS
from chorez import models


def dateparser_settings() -> Any:  # pyright: ignore[reportAny, reportExplicitAny]
    return {
        "RETURN_AS_TIMEZONE_AWARE": True,
        "DATE_ORDER": "YMD",
        "RELATIVE_BASE": datetime.now(),
    }


class TimeStart(Tap):
    task_id: int  # pyright: ignore[reportUninitializedInstanceVariable]
    start: str = "now"
    end: str | None = None

    @override
    def configure(self) -> None:
        self.add_argument("task_id", help="The task ID to assign the time entry to")  # pyright: ignore[reportUnknownMemberType]
        self.add_argument("--start", "-s", dest="start")  # pyright: ignore[reportUnknownMemberType]
        self.add_argument("--end", "-e", dest="end")  # pyright: ignore[reportUnknownMemberType]

        self.set_defaults(run=self.run)

    def run(self, args: Self, chorez: Chorez) -> int:
        filter = f"{models.Task.id.key}={args.task_id}"
        tasks = chorez.db.list_tasks(filter)
        if len(tasks) == 0:
            print(f"Task with ID {args.task_id} not found", file=sys.stderr)
            return EXIT_FAILURE
        assert len(tasks) == 1

        start = dateparser.parse(args.start, settings=dateparser_settings())  # pyright: ignore[reportAny]
        if start is None:
            print(f"Invalid start date/time {args.start!r}", file=sys.stderr)
            return EXIT_FAILURE

        end: datetime | None = None
        if args.end is not None:
            end = dateparser.parse(args.end, settings=dateparser_settings())  # pyright: ignore[reportAny]
            if end is None:
                print(f"Invalid end date/time {args.start!r}", file=sys.stderr)
                return EXIT_FAILURE

        time_entry = models.TimeEntry(task_id=args.task_id, start=start, end=end)
        chorez.db.save_time_entry(time_entry)

        return EXIT_SUCCESS


class TimeActive(Tap):
    @override
    def configure(self) -> None:
        self.set_defaults(run=self.run)

    def run(self, args: Self, chorez: Chorez) -> int:  # pyright: ignore[reportUnusedParameter]
        time_entries = chorez.db.list_time_entries(
            filter="end IS NULL",
        )
        for entry in time_entries:
            print(entry.pretty_with_task())

        return EXIT_SUCCESS


class TimeCLI(Tap):
    @override
    def configure(self) -> None:
        self.add_subparsers(dest="subcommand", required=True, help="time subcommands")  # pyright: ignore[reportUnknownMemberType]
        self.add_subparser("start", TimeStart)  # pyright: ignore[reportUnknownMemberType]
        self.add_subparser("active", TimeActive)  # pyright: ignore[reportUnknownMemberType]
