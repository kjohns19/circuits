import collections.abc as abc
import typing as t

import cairo

from . import component_display
from . import component_registry
from . import shapes

if t.TYPE_CHECKING:
    from . import application
    from . import circuit as circuit_mod
    from . import creator as creator_mod
    from . import utils


_T = t.TypeVar('_T')


class ComponentException(Exception):
    pass


class Component:
    OnUpdateFunc = abc.Callable[['Component'], None]
    OnDrawFunc = abc.Callable[['Component', 'application.Application', cairo.Context],
                              None]
    OnClickFunc = abc.Callable[['Component', 'utils.MouseButton'], None]
    OnDestroyFunc = abc.Callable[['Component'], None]

    def __init__(self, circuit: 'circuit_mod.Circuit',
                 num_inputs: int, num_outputs: int,
                 input_labels: t.Optional[list[str]] = None,
                 output_labels: t.Optional[list[str]] = None,
                 on_update: t.Optional['Component.OnUpdateFunc'] = None,
                 on_draw: t.Optional['Component.OnDrawFunc'] = None,
                 on_click: t.Optional['Component.OnClickFunc'] = None,
                 on_destroy: t.Optional['Component.OnDestroyFunc'] = None) -> None:
        self._circuit = circuit
        self._id = -1

        self._data: dict[str, t.Any] = {}

        self._inputs: list['Input'] = []
        self._outputs: list['Output'] = []

        self._display = component_display.ComponentDisplay(self)

        self.num_inputs = num_inputs
        self.num_outputs = num_outputs

        self._on_update = on_update or _default_on_update
        self._on_draw = on_draw or _default_on_draw
        self._on_click = on_click or _default_on_click
        self._on_destroy = on_destroy or _default_on_destroy

        self._circuit.add_component(self)

        self._name = ''
        self._input_labels = input_labels or []
        self._output_labels = output_labels or []

        self._creator: t.Optional['creator_mod.Creator'] = None

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    @property
    def circuit(self) -> 'circuit_mod.Circuit':
        return self._circuit

    @property
    def num_inputs(self) -> int:
        return len(self._inputs)

    @num_inputs.setter
    def num_inputs(self, value: int) -> None:
        self._inputs = _resize_list(
            lst=self._inputs,
            size=value,
            old_elem_func=lambda input, i: input.disconnect(),
            new_elem_func=lambda i: Input(self, i))
        self._display.recalculate_size()

    @property
    def num_outputs(self) -> int:
        return len(self._outputs)

    @num_outputs.setter
    def num_outputs(self, value: int) -> None:
        self._outputs = _resize_list(
            lst=self._outputs,
            size=value,
            old_elem_func=lambda output, i: output.disconnect_all(),
            new_elem_func=lambda i: Output(self, i))
        self._display.recalculate_size()

    @property
    def inputs(self) -> list['Input']:
        return self._inputs

    @property
    def outputs(self) -> list['Output']:
        return self._outputs

    @property
    def display(self) -> component_display.ComponentDisplay:
        return self._display

    @property
    def data(self) -> dict[str, t.Any]:
        return self._data

    def on_update(self) -> None:
        self._on_update(self)

    def set_on_update(self, func: 'Component.OnUpdateFunc') -> None:
        self._on_update = func

    def on_draw(self, app: 'application.Application', cr: cairo.Context) -> None:
        self._on_draw(self, app, cr)

    def set_on_draw(self, func: 'Component.OnDrawFunc') -> None:
        self._on_draw = func

    def on_click(self, button: 'utils.MouseButton') -> None:
        self._on_click(self, button)

    def set_on_click(self, func: 'Component.OnClickFunc') -> None:
        self._on_click = func

    def on_destroy(self) -> None:
        self._on_destroy(self)

    def set_on_destroy(self, func: 'Component.OnDestroyFunc') -> None:
        self._on_destroy = func

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def creator(self) -> t.Optional['creator_mod.Creator']:
        return self._creator

    @creator.setter
    def creator(self, value: 'creator_mod.Creator') -> None:
        self._creator = value

    @property
    def input_labels(self) -> list[str]:
        return self._input_labels

    @input_labels.setter
    def input_labels(self, value: list[str]) -> None:
        self._input_labels = value or []

    @property
    def output_labels(self) -> list[str]:
        return self._output_labels

    @output_labels.setter
    def output_labels(self, value: list[str]) -> None:
        self._output_labels = value or []

    def input_label(self, idx: int) -> str:
        if idx < len(self._input_labels):
            return self._input_labels[idx]
        if self.num_inputs == 1:
            return 'in'
        return 'in{}'.format(idx+1)

    def output_label(self, idx: int) -> str:
        if idx < len(self._output_labels):
            return self._output_labels[idx]
        if self.num_outputs == 1:
            return 'out'
        return 'out{}'.format(idx+1)

    def schedule_update(self, delay: int = 1) -> None:
        self._circuit.schedule_update(self, delay)

    def update_inputs(self) -> None:
        for input in self._inputs:
            input.update()

    def delete(self) -> None:
        for input in self._inputs:
            input.disconnect()
        for output in self._outputs:
            output.disconnect_all()
        self._circuit.remove_component(self)

    def __str__(self) -> str:
        return (
            'Component[inputs={} outputs={}]'.format(
                self._inputs, self._outputs))

    def get_save_data(self) -> dict[str, t.Any]:
        return {
            'id': self.id,
            'creator': self.creator.get_save_data() if self.creator else None,
            'inputs': [input.get_save_data() for input in self.inputs],
            'outputs': [output.get_save_data() for output in self.outputs],
            'display': self.display.get_save_data(),
            'data': self._data,
            'property_data': (
                self.creator.get_property_data(self) if self.creator else None)
        }

    @staticmethod
    def load(circuit: 'circuit_mod.Circuit', data: dict[str, t.Any]) -> 'Component':
        creator_data = data['creator']
        creator = component_registry.registry.get_creator(
            creator_data['category'], creator_data['name'])
        component = creator(circuit)

        creator.apply_property_data(component, data['property_data'])

        component.num_inputs = len(data['inputs'])

        output_data = data['outputs']
        component.num_outputs = len(output_data)
        for out_data in output_data:
            component.outputs[out_data['index']].value = out_data['value']

        component._data = data['data']
        component.display.load(data['display'])

        return component

    def load_inputs(self, data: dict[str, t.Any],
                    components_by_id: dict[int, 'Component']) -> None:
        input_data = data['inputs']
        for in_data in input_data:
            self.inputs[in_data['index']].load(in_data, components_by_id)


def _default_on_update(component: Component) -> None:
    pass


def _default_on_draw(component: Component, app: 'application.Application',
                     cr: cairo.Context) -> None:
    pass


def _default_on_click(component: Component, button: 'utils.MouseButton') -> None:
    pass


def _default_on_destroy(component: Component) -> None:
    pass


def _resize_list(lst: list[_T], size: int,
                 old_elem_func: abc.Callable[[_T, int], None],
                 new_elem_func: abc.Callable[[int], _T]) -> list[_T]:
    current = len(lst)
    if size < current:
        for i, obj in enumerate(lst[size:]):
            old_elem_func(obj, i)
        return lst[:size]
    elif size > current:
        new_elems = [new_elem_func(current+i) for i in range(size-current)]
        return lst + new_elems
    return lst


class Input:
    def __init__(self, component: Component, index: int) -> None:
        self._component = component
        self._index = index
        self._value: t.Any = None
        self._new_value: t.Any = None
        self._old_value: t.Any = None
        self._connected_output: t.Optional['Output'] = None
        self._wire_nodes: list['WireNode'] = []

    @property
    def component(self) -> Component:
        return self._component

    @property
    def index(self) -> int:
        return self._index

    @property
    def value(self) -> t.Any:
        return self._value

    @value.setter
    def value(self, value: t.Any) -> None:
        if self._new_value != value:
            self._new_value = value
            self._component.schedule_update()

    @property
    def new_value(self) -> t.Any:
        return self._new_value

    @property
    def old_value(self) -> t.Any:
        return self._old_value

    @property
    def connected_output(self) -> t.Optional['Output']:
        return self._connected_output

    @property
    def label(self) -> str:
        return self._component.input_label(self._index)

    @property
    def wire_nodes(self) -> list['WireNode']:
        return self._wire_nodes

    @property
    def wire_positions(self) -> list[shapes.Vector2]:
        return [node.position for node in self._wire_nodes]

    def is_connected(self) -> bool:
        return self._connected_output is not None

    def get_save_data(self) -> dict[str, t.Any]:
        connected = self.connected_output
        if connected is None:
            connected_data = None
        else:
            connected_data = {
                'component_id': connected.component.id,
                'index': connected.index
            }
        return {
            'index': self.index,
            'value': self.value,
            'new_value': self.new_value,
            'old_value': self.old_value,
            'connection': connected_data,
            'wire_positions': [tuple(node.position) for node in self._wire_nodes]
        }

    def load(self, data: dict[str, t.Any],
             components_by_id: dict[int, Component]) -> None:
        connection = data['connection']
        if connection:
            component = components_by_id[connection['component_id']]
            output = component.outputs[connection['index']]
            self._connected_output = output
            output.connect(self)
        self._value = data['value']
        self._new_value = data['new_value']
        self._old_value = data['old_value']
        self._wire_nodes = [
            WireNode(shapes.Vector2(pos)) for pos in data['wire_positions']
        ]

    def update(self) -> None:
        self._old_value, self._value = self._value, self._new_value

    def connect(self, output: 'Output',
                wire_positions: t.Optional[list[shapes.Vector2]] = None) -> None:
        if self._connected_output is output:
            self._wire_nodes = [WireNode(pos) for pos in (wire_positions or [])]
            return
        self.disconnect()
        self._connected_output = output
        self._wire_nodes = [WireNode(pos) for pos in (wire_positions or [])]
        self.value = output.value
        output.connect(self, wire_positions)

    def disconnect(self) -> None:
        output = self._connected_output
        if output is None:
            return
        self.value = None
        self._connected_output = None
        self._wire_nodes = []
        output.disconnect(self)

    def __str__(self) -> str:
        return 'Input[comp={} idx={}]'.format(self.component, self.index)


class Output:
    def __init__(self, component: Component, index: int) -> None:
        self._component = component
        self._index = index
        self._value: t.Any = None
        self._connected_inputs: set[Input] = set()

    @property
    def component(self) -> Component:
        return self._component

    @property
    def index(self) -> int:
        return self._index

    @property
    def value(self) -> t.Any:
        return self._value

    @value.setter
    def value(self, value: t.Any) -> None:
        self._value = value
        for input in self._connected_inputs:
            input.value = value

    @property
    def label(self) -> str:
        return self._component.output_label(self._index)

    @property
    def connected_inputs(self) -> abc.Iterator[Input]:
        return iter(self._connected_inputs)

    def is_connected(self) -> bool:
        return bool(self._connected_inputs)

    def get_save_data(self) -> dict[str, t.Any]:
        return {
            'index': self.index,
            'value': self.value
        }

    def connect(self, input: Input,
                wire_positions: t.Optional[list[shapes.Vector2]] = None) -> None:
        if input in self._connected_inputs:
            return
        self._connected_inputs.add(input)
        input.connect(self, wire_positions)

    def disconnect(self, input: Input) -> None:
        if input not in self._connected_inputs:
            return
        self._connected_inputs.remove(input)
        input.disconnect()

    def disconnect_all(self) -> None:
        inputs = set(self._connected_inputs)
        self._connected_inputs.clear()
        for input in inputs:
            input.disconnect()

    def __str__(self) -> str:
        return 'Output[comp={} idx={}]'.format(self.component, self.index)


class WireNode:
    def __init__(self, position: shapes.Vector2) -> None:
        self._position = position

    @property
    def position(self) -> shapes.Vector2:
        return self._position

    @position.setter
    def position(self, value: shapes.Vector2) -> None:
        self._position = value
