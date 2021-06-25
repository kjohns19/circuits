from .. import component as component_module
from .. import component_display
from ..component_registry import registry
from .. import properties
from .. import utils


CATEGORY = 'Input'


@registry.register('Constant', CATEGORY)
def constant(circuit):
    component = component_module.Component(
        circuit, num_inputs=0, num_outputs=2)

    def output_label(idx):
        return str(component.outputs[idx].value)
    component.output_label = output_label

    component.outputs[0].value = 0
    component.outputs[1].value = 1
    return component


def constant_getter(component):
    return [output.value for output in component.outputs]


def constant_setter(component, values):
    component.num_outputs = len(values)
    for i, value in enumerate(values):
        component.outputs[i].value = value


constant.add_property(properties.RangedMultiValueProperty(
    getter=constant_getter,
    setter=constant_setter,
    title='Outputs'))


@registry.register('Button', CATEGORY)
def button(circuit):
    def on_click(component, button):
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
            color = (component_display.WHITE, component_display.GRAY)[int(on)]
            component.display.fill_color = color
            component.outputs[0].value = component.data['off_on'][int(on)]
            component.schedule_update()

    def on_update(component):
        component.data['click_state'] = max(
            0, component.data['click_state'] - 1)
        if component.data['click_state'] > 0:
            component.schedule_update()
        if not component.data['toggle']:
            component.outputs[0].value = component.data['off_on'][0]
            component.display.fill_color = component_display.WHITE

    component = component_module.Component(
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


def button_on_off_setter(component, values):
    component.data['off_on'] = values
    on = component.data['on']
    component.outputs[0].value = component.data['off_on'][int(on)]


button.add_property(properties.MultiValueProperty(
    getter=utils.data_getter('off_on'),
    setter=button_on_off_setter,
    labels=['Off', 'On'],
    title='Values'))
