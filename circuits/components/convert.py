import collections.abc as abc
import typing as t

from .. import utils


CATEGORY = 'Convert'


_functions: list[tuple[str, abc.Callable[..., t.Any]]] = [
    ('int', lambda x: int(x)),
    ('str', lambda x: str(x)),
    ('chr', chr),
    ('ord', ord)
]

for name, op in _functions:
    utils.create_nary_component(name, CATEGORY, op)
