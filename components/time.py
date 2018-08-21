from component import Component
from component_registry import registry
from properties import NumberProperty
import utils


CATEGORY = 'Time'


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
