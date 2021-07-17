import typing as t

from gi.repository import Gdk  # type: ignore

from .. import circuit as circuit_mod
from .. import component as component_mod
from .. import draw
from ..component_registry import registry
from .. import properties
from .. import utils


CATEGORY = 'Input'


@registry.register('Constant', CATEGORY)
def constant(circuit: circuit_mod.Circuit) -> component_mod.Component:
    component = component_mod.Component(
        circuit, num_inputs=0, num_outputs=2)
    component.outputs[0].value = 0
    component.outputs[1].value = 1
    return component


def constant_getter(component: component_mod.Component) -> list[t.Any]:
    return [output.value for output in component.outputs]


def constant_setter(component: component_mod.Component, values: list[t.Any]) -> None:
    component.num_outputs = len(values)
    for i, value in enumerate(values):
        component.outputs[i].value = value
    component.output_labels = [str(val) for val in values]


constant.add_property(properties.RangedMultiValueProperty(
    getter=constant_getter,
    setter=constant_setter,
    title='Outputs'))


@registry.register('Button', CATEGORY)
def button(circuit: circuit_mod.Circuit) -> component_mod.Component:
    def on_click(component: component_mod.Component, button: utils.MouseButton) -> None:
        if button == utils.MouseButton.LEFT:
            if component.data['click_state'] != 0:
                return
            if component.data['toggle']:
                on = not component.data['on']
                component.data['click_state'] = 1
            else:
                on = True
                component.data['click_state'] = 2
            component.data['on'] = on
            color = draw.COLOR_GRAY if on else draw.COLOR_WHITE
            component.display.fill_color = color
            component.outputs[0].value = component.data['off_on'][int(on)]
            component.schedule_update()

    def on_update(component: component_mod.Component) -> None:
        component.data['click_state'] = max(
            0, component.data['click_state'] - 1)
        if component.data['click_state'] > 0:
            component.schedule_update()
        if not component.data['toggle']:
            component.outputs[0].value = component.data['off_on'][0]
            component.display.fill_color = draw.COLOR_WHITE
            component.data['on'] = False

    component = component_mod.Component(
        circuit,
        num_inputs=0, num_outputs=1,
        on_click=on_click,
        on_update=on_update)
    component.data['click_state'] = 0
    component.data['on'] = False
    component.data['toggle'] = False
    component.data['off_on'] = [False, True]
    component.outputs[0].value = False
    return component


button.add_property(properties.BoolProperty(
    getter=utils.data_getter('toggle'),
    setter=utils.data_setter('toggle'),
    label='Toggle'))


def button_on_off_setter(component: component_mod.Component,
                         values: list[t.Any]) -> None:
    component.data['off_on'] = values
    on = component.data['on']
    component.outputs[0].value = component.data['off_on'][int(on)]


button.add_property(properties.MultiValueProperty(
    getter=utils.data_getter('off_on'),
    setter=button_on_off_setter,
    labels=['Off', 'On'],
    title='Values'))


@registry.register('Keyboard', CATEGORY)
def keyboard(circuit: circuit_mod.Circuit) -> component_mod.Component:
    def on_click(component: component_mod.Component, button: utils.MouseButton) -> None:
        if button != utils.MouseButton.LEFT:
            return
        enabled = not component.data['enabled']
        component.data['enabled'] = enabled
        component.display.fill_color = draw.COLOR_GRAY if enabled else draw.COLOR_WHITE

    def on_destroy(component: component_mod.Component) -> None:
        circuit.unregister_key_callback(component.data['callback_id'])

    def on_key_press(key: Gdk.EventKey) -> None:
        if component.data['enabled']:
            name = Gdk.keyval_name(key.keyval)
            if name == 'Return':
                component.outputs[0].value = component.data['text_buffer']
                component.data['text_buffer'] = ''
            else:
                unicode_value = Gdk.keyval_to_unicode(key.keyval)
                if unicode_value != 0:
                    current = component.data['text_buffer']
                    if name == 'BackSpace':
                        component.data['text_buffer'] = current[:-1]
                    else:
                        component.data['text_buffer'] = current + chr(unicode_value)

    component = component_mod.Component(circuit, num_inputs=0, num_outputs=1,
                                        on_click=on_click, on_destroy=on_destroy)
    component.outputs[0].value = ''

    component.data['callback_id'] = circuit.register_key_callback(on_key_press,
                                                                  release_callback=None)
    component.data['enabled'] = False
    component.data['text_buffer'] = ''
    return component
