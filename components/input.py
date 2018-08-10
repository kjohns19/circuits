from component import Component
from component_registry import registry
import utils


CATEGORY = 'Input'


@registry.register('Constant', CATEGORY)
def constant(circuit):
    component = Component(circuit, num_inputs=0, num_outputs=2)
    # TODO Custom values
    component.outputs[0].value = 0
    component.outputs[1].value = 1
    return component


@registry.register('Button', CATEGORY)
def button(circuit):
    def on_click(component, button):
        if button == utils.MouseButton.LEFT:
            component.outputs[0].value = 1
        elif button == -utils.MouseButton.LEFT:
            component.outputs[0].value = 0

    component = Component(
        circuit,
        num_inputs=0, num_outputs=1,
        on_click=on_click)
    component.outputs[0].value = 0
    return component
