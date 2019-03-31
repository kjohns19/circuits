from component import Component
from component_registry import registry
import properties
import utils


CATEGORY = 'Logic'

_operators = [
    ('And',  lambda a, b: bool(a and b)),
    ('Or',   lambda a, b: bool(a or b)),
    ('Nand', lambda a, b: not (a and b)),
    ('Nor',  lambda a, b: not (a or b)),
    ('Xor',  lambda a, b: bool(a) != bool(b)),
    ('Xnor', lambda a, b: bool(a) == bool(b)),
    ('Not',  lambda a: not a)
]

for name, op in _operators:
    utils.create_nary_component(name, CATEGORY, op)


@registry.register('Mux', CATEGORY)
def mux(circuit):
    def on_update(component):
        try:
            select = int(component.inputs[0].value or 0)
        except ValueError:
            select = None
        if select is None or select >= component.num_inputs-1:
            component.outputs[0].value = None
        else:
            component.outputs[0].value = component.inputs[select+1].value

    component = Component(
        circuit, num_inputs=3, num_outputs=1,
        input_labels=['sel', 'in1', 'in2'],
        on_update=on_update)
    return component


def _mux_set_labels(component, value):
    component.input_labels = (
        ['sel'] + ['in{}'.format(i+1) for i in range(value-1)]
    )


mux.add_property(properties.NumInputsProperty(
    callback=_mux_set_labels, min_value=3))
