import component as component_module
from component_registry import registry
import properties
import utils


CATEGORY = 'Storage'


def _memory_should_update(component):
    if component.data['edge_triggered']:
        clk = component.inputs[0].value
        old_clk = component.inputs[0].old_value
        return clk and clk != old_clk
    else:
        return component.inputs[0].value


@registry.register('Memory', CATEGORY)
def memory(circuit):
    def on_update(component):
        if _memory_should_update(component):
            component.outputs[0].value = component.inputs[1].value

    component = component_module.Component(
        circuit, num_inputs=2, num_outputs=1,
        input_labels=['clk', 'value'],
        output_labels=['value'],
        on_update=on_update)
    component.data['edge_triggered'] = True
    return component


memory.add_property(properties.BoolProperty(
    getter=utils.data_getter('edge_triggered'),
    setter=utils.data_setter('edge_triggered'),
    label='Edge Triggered'))


def _ram_address(component):
    address = component.inputs[1].value
    if not isinstance(address, int):
        return None
    if address < 0 or address >= len(component.data['memory']):
        return None
    return address


@registry.register('RAM', CATEGORY)
def ram(circuit):
    def on_update(component):
        address = _ram_address(component)
        if address is None:
            component.outputs[0].value = None
            return

        memory = component.data['memory']
        component.outputs[0].value = memory[address]

        if _memory_should_update(component):
            memory[address] = component.inputs[2].value

    component = component_module.Component(
        circuit,
        num_inputs=3,
        num_outputs=1,
        input_labels=['clk', 'adr', 'val'],
        output_labels=['value'],
        on_update=on_update)
    component.data['memory'] = [None]*10
    component.data['edge_triggered'] = True
    return component


def ram_getter(component):
    return component.data['memory']


def ram_setter(component, values):
    memory = list(values)
    component.data['memory'] = memory
    address = _ram_address(component)
    component.outputs[0].value = None if address is None else memory[address]


ram.add_property(properties.BoolProperty(
    getter=utils.data_getter('edge_triggered'),
    setter=utils.data_setter('edge_triggered'),
    label='Edge Triggered'))

ram.add_property(properties.RangedMultiValueProperty(
    getter=ram_getter,
    setter=ram_setter,
    min_values=1, max_values=1000,
    title='Values'))
