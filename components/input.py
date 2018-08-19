from component import Component
import component_display
from component_registry import registry
import utils

from properties import BoolProperty
from properties import NumberProperty
from properties import MultiValueProperty
from properties import RangedMultiValueProperty


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


constant.add_property(RangedMultiValueProperty(
    getter=constant_getter,
    setter=constant_setter,
    title='Outputs'))


@registry.register('Button', CATEGORY)
def button(circuit):
    def on_click(component, button):
        if button == utils.MouseButton.LEFT:
            if component.data['toggle']:
                on = not component.data['on']
            else:
                on = True
            component.data['on'] = on
            color = (component_display.WHITE, component_display.GRAY)[int(on)]
            component.display.fill_color = color
            component.outputs[0].value = component.data['off_on'][int(on)]
        elif button == -utils.MouseButton.LEFT:
            if not component.data['toggle']:
                component.data['on'] = False
                component.schedule_update()

    def on_update(component):
        if not component.data['toggle'] and not component.data['on']:
            component.outputs[0].value = component.data['off_on'][0]
            component.display.fill_color = component_display.WHITE

    component = Component(
        circuit,
        num_inputs=0, num_outputs=1,
        on_click=on_click,
        on_update=on_update)
    component.data['on'] = False
    component.data['toggle'] = False
    component.data['off_on'] = [False, True]
    component.outputs[0].value = False
    return component


button.add_property(BoolProperty(
    getter=utils.data_getter('toggle'),
    setter=utils.data_setter('toggle'),
    label='Toggle'))


def button_on_off_setter(component, values):
    component.data['off_on'] = values
    on = component.data['on']
    component.outputs[0].value = component.data['off_on'][int(on)]


button.add_property(MultiValueProperty(
    getter=utils.data_getter('off_on'),
    setter=button_on_off_setter,
    labels=['Off', 'On'],
    title='Values'))


@registry.register('Clock', CATEGORY)
def clock(circuit):
    def on_update(component):
        value = not component.outputs[0].value
        component.outputs[0].value = value
        delay = (
            component.data['off_delay'],
            component.data['on_delay']
        )[int(value)]
        component.schedule_update(delay)

    component = Component(
        circuit, num_inputs=0, num_outputs=1,
        on_update=on_update)
    component.data['off_delay'] = 1
    component.data['on_delay'] = 1
    component.outputs[0].value = False
    component.schedule_update()
    return component


clock.add_property(NumberProperty(
    getter=utils.data_getter('off_delay'),
    setter=utils.data_setter('off_delay'),
    min_value=1, max_value=10,
    label='Off delay'))

clock.add_property(NumberProperty(
    getter=utils.data_getter('on_delay'),
    setter=utils.data_setter('on_delay'),
    min_value=1, max_value=10,
    label='On delay'))
