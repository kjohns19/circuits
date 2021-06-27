import typing as t

from .. import component as component_mod
from .. import circuit as circuit_mod
from ..component_registry import registry
from .. import properties
from .. import utils


CATEGORY = 'Storage'


def _memory_should_update(component: component_mod.Component) -> bool:
    if component.data['edge_triggered']:
        clk = bool(component.inputs[0].value)
        old_clk = bool(component.inputs[0].old_value)
        return clk and clk != old_clk
    else:
        return bool(component.inputs[0].value)


@registry.register('Memory', CATEGORY)
def memory(circuit: circuit_mod.Circuit) -> component_mod.Component:
    def on_update(component: component_mod.Component) -> None:
        if _memory_should_update(component):
            component.outputs[0].value = component.inputs[1].value

    component = component_mod.Component(
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


def _memory_value_setter(component: component_mod.Component,
                         values: list[t.Any]) -> None:
    component.outputs[0].value = values[0]


memory.add_property(properties.MultiValueProperty(
    getter=lambda component: [component.outputs[0].value],
    setter=_memory_value_setter,
    labels=['Value'],
    title='Value'))


def _ram_address(component: component_mod.Component) -> int:
    address = component.inputs[1].value
    if not isinstance(address, int):
        return 0
    if address < 0 or address >= len(component.data['memory']):
        return 0
    return address


@registry.register('RAM', CATEGORY)
def ram(circuit: circuit_mod.Circuit) -> component_mod.Component:
    def on_update(component: component_mod.Component) -> None:
        address = _ram_address(component)
        memory = component.data['memory']
        component.outputs[0].value = memory[address]

        if _memory_should_update(component):
            memory[address] = component.inputs[2].value

    component = component_mod.Component(
        circuit,
        num_inputs=3,
        num_outputs=1,
        input_labels=['clk', 'adr', 'val'],
        output_labels=['value'],
        on_update=on_update)
    component.data['memory'] = [None]*10
    component.data['edge_triggered'] = True
    return component


def ram_getter(component: component_mod.Component) -> t.Any:
    return component.data['memory']


def ram_setter(component: component_mod.Component, values: list[t.Any]) -> None:
    memory = list(values)
    component.data['memory'] = memory
    address = _ram_address(component)
    component.outputs[0].value = memory[address]


ram.add_property(properties.BoolProperty(
    getter=utils.data_getter('edge_triggered'),
    setter=utils.data_setter('edge_triggered'),
    label='Edge Triggered'))

ram.add_property(properties.RangedMultiValueProperty(
    getter=ram_getter,
    setter=ram_setter,
    min_values=1, max_values=1000,
    title='Values', start_index=0))
