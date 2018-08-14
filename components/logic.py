import utils


CATEGORY = 'Logic'

_operators = [
    ('And',  lambda a, b: bool(a and b)),
    ('Or',   lambda a, b: bool(a or b)),
    ('Nand', lambda a, b: not (a and b)),
    ('Nor',  lambda a, b: not (a or b)),
    ('Xor',  lambda a, b: bool(a) != bool(b)),
    ('Not',  lambda a: not a)
]

for name, op in _operators:
    utils.create_nary_component(name, CATEGORY, op)
