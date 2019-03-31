import utils


CATEGORY = 'Arithmetic'

_operators = [
    ('Add', lambda a, b: a+b),
    ('Sub', lambda a, b: a-b),
    ('Mul', lambda a, b: a*b),
    ('Div', lambda a, b: a//b)
]

for name, op in _operators:
    utils.create_nary_component(name, CATEGORY, op, default_value=0)
