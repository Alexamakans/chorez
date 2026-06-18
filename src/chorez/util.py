# pyright: reportExplicitAny=false, reportAny=false, reportUnnecessaryIsInstance=false
import itertools
from operator import attrgetter, itemgetter
from typing import Any, Callable
from collections.abc import Iterable, Sequence

KeySpec = str | Callable[[Any], Any] | tuple[str, Any]


def _to_keyfunc(spec: KeySpec) -> Callable[[Any], Any]:
    """
    Turn a key spec into a callable:
      - callable: used as-is
      - str: attribute lookup (supports dotted paths like 'owner.name')
      - ('item', 'k'): dict-item lookup like item['k']  (or ('item','k','sub'))
    """
    if callable(spec):
        return spec
    if isinstance(spec, str):
        return attrgetter(spec)  # dotted paths supported
    if isinstance(spec, tuple) and spec and spec[0] == "item":
        return itemgetter(*spec[1:]) if len(spec) > 2 else itemgetter(spec[1])  # pyright: ignore[reportUnknownVariableType]
    raise TypeError(f"Unsupported key spec: {spec!r}")


def _sort_keyfunc(keyfuncs: Sequence[Callable[[Any], Any]]) -> Callable[[Any], Any]:
    return lambda x: tuple(kf(x) for kf in keyfuncs)


def groupby_multi(iterable: Iterable[Any], *keys: KeySpec):
    """
    Return a sorted iterable and a sequence of keyfuncs so `itertools.groupby`
    can be applied recursively.

    Usage:
        data, keyfuncs = groupby_multi(tasks, 'priority', 'status')
        # then do recursive groupby(data, keyfuncs) as you like

    Notes:
    - We sort by all keys up front so that nested groupby works correctly.
    """
    keyfuncs = tuple(_to_keyfunc(k) for k in keys)
    if not keyfuncs:
        # no grouping: return iterable as-is
        return list(iterable), keyfuncs
    data = sorted(iterable, key=_sort_keyfunc(keyfuncs))
    return data, keyfuncs


def walk_groupby(
    iterable: Iterable[Any],
    *keys: KeySpec,
    on_group: Callable[[int, Any, list[Any]], None] | None = None,
    on_leaf: Callable[[int, list[Any]], None] | None = None,
):
    """
    Recursively apply groupby for an arbitrary number of keys and call hooks.

    Hooks:
      - on_group(level, key, group_list): called at each level before descending
      - on_leaf(level, items): called when there are no more keys (leaf level)

    Example printing usage is shown below.
    """
    data, keyfuncs = groupby_multi(iterable, *keys)

    def _recurse(chunk: list[Any], depth: int) -> None:
        if depth == len(keyfuncs):
            if on_leaf:
                on_leaf(depth, chunk)
            return
        kf = keyfuncs[depth]
        for key, grp in itertools.groupby(chunk, key=kf):
            grp_list = list(grp)
            if on_group:
                on_group(depth, key, grp_list)
            _recurse(grp_list, depth + 1)

    _recurse(list(data), 0)


# --- Example: replicate/extend your printout ---------------------------------


def print_grouped(
    items: Iterable[Any],
    *,
    keys: Iterable[KeySpec],
    item_str: Callable[[Any], str] = str,
):
    """
    Pretty-prints nested groups with counts, for any depth.
    `keys` can be:
      - 'priority' (attr), 'status' (attr), 'owner.name' (nested attr),
      - ('item','k') for dicts (item['k']), or callables like lambda t: t.priority
    """
    indent = "\t"

    def on_group(level: int, key: Any, group_list: list[Any]) -> None:
        # Try to print a nice value if it has `.value`, else as-is
        shown = getattr(key, "value", key)
        print(f"{indent * level}{shown} (count={len(group_list)})")

    def on_leaf(level: int, items: list[Any]) -> None:
        for it in items:
            print(f"{indent * level}{item_str(it)}")

    walk_groupby(items, *keys, on_group=on_group, on_leaf=on_leaf)
