from component import Component
from component_registry import registry

import operator


CATEGORY = 'Arithmetic'


_operators = [
    ('Add', operator.add),
    ('Sub', operator.sub),
    ('Mul', operator.mul),
    ('Div', operator.floordiv)
]

for name, op in _operators:
    @registry.register(name, CATEGORY)
    def creator(circuit, name=name, op=op):
        def on_update(component):
            op1 = component.inputs[0].value
            op2 = component.inputs[1].value
            try:
                result = op(op1, op2)
            except TypeError:
                result = 0
            component.outputs[0].value = result
        return Component(
            circuit, num_inputs=2, num_outputs=1, on_update=on_update)
