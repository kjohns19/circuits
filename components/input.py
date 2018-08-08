from component import Component
from component_registry import registry


CATEGORY = 'Input'


@registry.register('Constant', CATEGORY)
def creator(circuit):
    component = Component(circuit, num_inputs=0, num_outputs=2)
    # TODO Custom values
    component.outputs[0].value = 0
    component.outputs[1].value = 1
    return component
