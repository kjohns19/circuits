import utils

import functools
import operator


CATEGORY = 'Arithmetic'

_operators = [
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
