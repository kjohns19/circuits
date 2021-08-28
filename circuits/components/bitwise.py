import collections.abc as abc
import typing as t

from .. import circuit as circuit_mod
from .. import component as component_mod
from ..component_registry import registry
from .. import properties
from .. import utils


CATEGORY = 'Bitwise'

_operators: list[tuple[str, abc.Callable[..., t.Any]]] = [
    ('And', lambda a, b: a & b),
    ('Or', lambda a, b: a | b),
    ('Nand', lambda a, b: ~(a & b)),
    ('Nor', lambda a, b: ~(a | b)),
    ('Xor', lambda a, b: a ^ b),
    ('Xnor', lambda a, b: ~(a ^ b)),
    ('Not', lambda a: ~a),
    ('Lshift', lambda a, b: a << b),
    ('Rshift', lambda a, b: a >> b)
]

for name, op in _operators:
    utils.create_nary_component(name, CATEGORY, op)


@registry.register('Splitter', CATEGORY)
def splitter(circuit: circuit_mod.Circuit) -> component_mod.Component:
    def on_update(component: component_mod.Component) -> None:
        print('Update splitter. Value', component.inputs[0].value,
              'Splits', component.data['splits'])
        value = component.inputs[0].value
        if not isinstance(value, int):
            for output in component.outputs:
                output.value = 0
            return

        current_bit = 0
        i = -1
        for i, split in enumerate(component.data['splits']):
            print(i)
            mask = (1 << (split - current_bit)) - 1
            component.outputs[i].value = (value >> current_bit) & mask
            current_bit = split

        mask = (1 << (64 - current_bit)) - 1
        component.outputs[-1].value = (value >> current_bit) & mask

    component = component_mod.Component(
        circuit, num_inputs=1, num_outputs=1,
        on_update=on_update)
    component.data['splits'] = []
    return component


def splitter_set_splits(component: component_mod.Component,
                        values: list[t.Any]) -> None:
    splits = sorted({
        val for val in values
        if isinstance(val, int) and 0 < val < 63
    })
    component.data['splits'] = splits
    component.num_outputs = len(splits) + 1
    component.on_update()


splitter.add_property(properties.RangedMultiValueProperty(
    getter=utils.data_getter('splits'),
    setter=splitter_set_splits,
    min_values=0,
    max_values=63,
    title='Splits'))


@registry.register('Merger', CATEGORY)
def merger(circuit: circuit_mod.Circuit) -> component_mod.Component:
    def on_update(component: component_mod.Component) -> None:
        print('Update merger. Values', [input.value for input in component.inputs],
              'Splits', component.data['splits'])
        inputs = [
            input.value if isinstance(input.value, int) else 0
            for input in component.inputs
        ]
        print(inputs)

        value = 0
        current_bit = 0
        for val, split in zip(inputs, component.data['splits']):
            mask = (1 << split) - 1
            value = value | ((val & mask) << current_bit)
            current_bit += split
            print(value)

        component.outputs[0].value = value

    component = component_mod.Component(
        circuit, num_inputs=1, num_outputs=1,
        on_update=on_update)
    component.data['splits'] = []
    return component


def merger_set_splits(component: component_mod.Component, values: list[t.Any]) -> None:
    splits = sorted({
        val for val in values
        if isinstance(val, int) and 0 < val < 63
    })
    component.data['splits'] = splits
    component.num_inputs = len(splits) + 1
    component.on_update()


merger.add_property(properties.RangedMultiValueProperty(
    getter=utils.data_getter('splits'),
    setter=merger_set_splits,
    min_values=0,
    max_values=63,
    title='Splits'))
