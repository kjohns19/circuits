import component as component_module
from component_registry import registry
import properties
import utils


CATEGORY = 'Logic'

_operators = [
    ('And',  (lambda *args: all(args)),         2, 10),
    ('Or',   (lambda *args: any(args)),         2, 10),
    ('Nand', (lambda *args: not all(args)),     2, 10),
    ('Nor',  (lambda *args: not any(args)),     2, 10),
    ('Xor',  (lambda a, b: bool(a) != bool(b)), 2,  2),
    ('Xnor', (lambda a, b: bool(a) == bool(b)), 2,  2),
    ('Not',  (lambda a: not a),                 1,  1)
]

for name, op, min_inputs, max_inputs in _operators:
    utils.create_nary_component(
        name, CATEGORY, op, min_inputs=min_inputs, max_inputs=max_inputs)


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

    component = component_module.Component(
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
