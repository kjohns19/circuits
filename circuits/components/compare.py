from .. import utils


CATEGORY = 'Compare'

_operators = [
    ('==', lambda a, b: a == b),
    ('!=', lambda a, b: a != b),
    ('<', lambda a, b: a < b),
    ('<=', lambda a, b: a <= b),
    ('>', lambda a, b: a > b),
    ('>=', lambda a, b: a >= b)
]

for name, op in _operators:
    utils.create_nary_component(name, CATEGORY, op)
