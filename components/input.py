from component import Component
from component_registry import registry
import utils

from properties import ListProperty


CATEGORY = 'Input'


@registry.register('Constant', CATEGORY)
def constant(circuit):
    component = Component(circuit, num_inputs=0, num_outputs=2)
    component.outputs[0].value = 0
    component.outputs[1].value = 1
    return component


def constant_getter(component):
    return [output.value for output in component.outputs]


def constant_setter(component, values):
    component.num_outputs = len(values)
    for i, value in enumerate(values):
        component.outputs[i].value = value


constant.add_property(ListProperty(
    getter=constant_getter,
    setter=constant_setter,
    title='Outputs'))


@registry.register('Button', CATEGORY)
def button(circuit):
    def on_click(component, button):
        if button == utils.MouseButton.LEFT:
            component.outputs[0].value = 1
            component.data['pressed'] = True
        elif button == -utils.MouseButton.LEFT:
            component.data['pressed'] = False
            component.schedule_update()

    def on_update(component):
        if not component.data.get('pressed'):
            component.outputs[0].value = 0

    component = Component(
        circuit,
        num_inputs=0, num_outputs=1,
        on_click=on_click,
        on_update=on_update)
    component.outputs[0].value = 0
    return component
