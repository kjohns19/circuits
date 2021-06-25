import utils


CATEGORY = 'Convert'


_functions = [
    ('int', lambda x: int(x)),
    ('str', lambda x: str(x)),
    ('chr', chr),
    ('ord', ord)
]

for name, op in _functions:
    utils.create_nary_component(name, CATEGORY, op)
