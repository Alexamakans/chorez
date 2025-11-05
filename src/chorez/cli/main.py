import sys

from chorez.chorez import Chorez
from chorez.cli.root import RootCLI


def main() -> None:
    args = sys.argv[1:]
    chorez = Chorez()
    parsed = RootCLI().parse_args(args)
    if hasattr(parsed, "run"):
        sys.exit(parsed.run(parsed, chorez))  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownArgumentType]
    else:
        print(parsed)


if __name__ == "__main__":
    main()
