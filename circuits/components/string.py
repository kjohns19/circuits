from .. import utils

CATEGORY = 'String'

utils.create_nary_component(
    'Index', CATEGORY, lambda s, i: s[i],
    input_labels=['str', 'idx'])
