from .. import utils


CATEGORY = 'Bitwise'

_operators = [
    ('And', lambda a, b: a & b),
    ('Or', lambda a, b: a | b),
    ('Nand', lambda a, b: ~(a & b)),
    ('Nor', lambda a, b: ~(a | b)),
    ('Xor', lambda a, b: a ^ b),
    ('Xnor', lambda a, b: ~(a ^ b)),
    ('Not', lambda a: ~a),
    ('Lshift', lambda a, b: a << b),
    ('Rshift', lambda a, b: a >> b)
]

for name, op in _operators:
    utils.create_nary_component(name, CATEGORY, op)
