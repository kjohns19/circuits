import collections.abc as abc
import functools
import operator
import typing as t

from .. import utils


CATEGORY = 'Arithmetic'

_operators: list[tuple[str, abc.Callable[..., t.Any], int, int]] = [
    ('Add', (lambda *args: sum(args)), 2, 10),
    ('Sub', (lambda a, b: a-b), 2, 2),
    ('Mul', (lambda *args: functools.reduce(operator.mul, args)), 2, 10),
    ('Div', (lambda a, b: a//b), 2, 2)
]

for name, op, min_inputs, max_inputs in _operators:
    utils.create_nary_component(
        name, CATEGORY, op,
        min_inputs=min_inputs, max_inputs=max_inputs,
        default_value=0)
