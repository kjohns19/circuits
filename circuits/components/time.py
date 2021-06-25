import component as component_module
from component_registry import registry
import properties
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

    component = component_module.Component(
        circuit, num_inputs=0, num_outputs=1,
        output_labels=['clk'],
        on_update=on_update)
    component.data['off_delay'] = 1
    component.data['on_delay'] = 1
    component.outputs[0].value = False
    component.schedule_update()
    return component


clock.add_property(properties.NumberProperty(
    getter=utils.data_getter('off_delay'),
    setter=utils.data_setter('off_delay'),
    min_value=1, max_value=100,
    label='Off delay'))

clock.add_property(properties.NumberProperty(
    getter=utils.data_getter('on_delay'),
    setter=utils.data_setter('on_delay'),
    min_value=1, max_value=100,
    label='On delay'))


@registry.register('Delay', CATEGORY)
def delay(circuit):
    def on_update(component):
        now = component.circuit.time
        old_value = component.inputs[0].old_value
        new_value = component.inputs[0].value
        updates = component.data['updates']
        delay = component.data['delay']

        # Add any updates to a queue
        if old_value != new_value:
            updates.append([new_value, now + delay - 1])
            if delay > 1:
                component.schedule_update(delay-1)

        # Check if the next update should happen yet
        if updates:
            next_update = updates[0]
            if next_update[1] == now:
                component.outputs[0].value = next_update[0]
                # Not very efficient
                del updates[0]

    component = component_module.Component(
        circuit, num_inputs=1, num_outputs=1,
        on_update=on_update)
    component.data['delay'] = 1
    component.data['updates'] = []
    return component


delay.add_property(properties.NumberProperty(
    getter=utils.data_getter('delay'),
    setter=utils.data_setter('delay'),
    min_value=1, max_value=100,
    label='Delay'))
