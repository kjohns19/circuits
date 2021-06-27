import cairo
import collections
import collections.abc as abc
import functools
import typing as t

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
    OnUpdateBoundFunc = abc.Callable[[], None]
    OnDrawFunc = abc.Callable[['Component', 'application.Application', cairo.Context],
                              None]
    OnDrawBoundFunc = abc.Callable[['application.Application', cairo.Context], None]
    OnClickFunc = abc.Callable[['Component', 'utils.MouseButton'], None]
    OnClickBoundFunc = abc.Callable[['utils.MouseButton'], None]

    def __init__(self, circuit: 'circuit_mod.Circuit',
                 num_inputs: int, num_outputs: int,
                 input_labels: t.Optional[list[str]] = None,
                 output_labels: t.Optional[list[str]] = None,
                 on_update: t.Optional['Component.OnUpdateFunc'] = None,
                 on_draw: t.Optional['Component.OnDrawFunc'] = None,
                 on_click: t.Optional['Component.OnClickFunc'] = None) -> None:
        self._circuit = circuit
        self._id = -1

        self._data: dict[str, t.Any] = collections.OrderedDict()

        self._inputs: list['_Input'] = []
        self._outputs: list['_Output'] = []

        self._display = component_display.ComponentDisplay(self)

        self.num_inputs = num_inputs
        self.num_outputs = num_outputs

        self._on_update = functools.partial(on_update or _default_on_update, self)
        self._on_draw = functools.partial(on_draw or _default_on_draw, self)
        self._on_click = functools.partial(on_click or _default_on_click, self)

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
            new_elem_func=lambda i: _Input(self, i))
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
            new_elem_func=lambda i: _Output(self, i))
        self._display.recalculate_size()

    @property
    def inputs(self) -> '_ReadOnlyList[_Input]':
        return _ReadOnlyList(self._inputs)

    @property
    def outputs(self) -> '_ReadOnlyList[_Output]':
        return _ReadOnlyList(self._outputs)

    @property
    def display(self) -> component_display.ComponentDisplay:
        return self._display

    @property
    def data(self) -> dict[str, t.Any]:
        return self._data

    @property
    def on_update(self) -> 'Component.OnUpdateBoundFunc':
        return self._on_update

    @on_update.setter
    def on_update(self, value: 'Component.OnUpdateFunc') -> None:
        self._on_update = functools.partial(value, self)

    @property
    def on_draw(self) -> 'Component.OnDrawBoundFunc':
        return self._on_draw

    @on_draw.setter
    def on_draw(self, value: 'Component.OnDrawFunc') -> None:
        self._on_draw = functools.partial(value, self)

    @property
    def on_click(self) -> 'Component.OnClickBoundFunc':
        return self._on_click

    @on_click.setter
    def on_click(self, value: 'Component.OnClickFunc') -> None:
        self._on_click = functools.partial(value, self)

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
        return collections.OrderedDict((
            ('id', self.id),
            ('name', self.name),
            ('creator', self.creator.get_save_data() if self.creator else None),
            ('inputs', [input.get_save_data() for input in self.inputs]),
            ('outputs', [output.get_save_data() for output in self.outputs]),
            ('display', self.display.get_save_data()),
            ('data', self._data)
        ))

    @staticmethod
    def load(circuit: 'circuit_mod.Circuit', data: dict[str, t.Any]) -> 'Component':
        creator_data = data['creator']
        creator = component_registry.registry.get_creator(
            creator_data['category'], creator_data['name'])
        component = creator(circuit)
        component.name = data['name']

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


class _Input:
    def __init__(self, component: Component, index: int) -> None:
        self._component = component
        self._index = index
        self._value: t.Any = None
        self._new_value: t.Any = None
        self._old_value: t.Any = None
        self._connected_output: t.Optional['_Output'] = None
        self._wire_positions: list[shapes.Vector2] = []

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
    def connected_output(self) -> t.Optional['_Output']:
        return self._connected_output

    @property
    def label(self) -> str:
        return self._component.input_label(self._index)

    @property
    def wire_positions(self) -> list[shapes.Vector2]:
        return self._wire_positions

    def move(self, amount: shapes.VecOrTup) -> None:
        self._wire_positions = [
            pos + amount
            for pos in self._wire_positions
        ]

    def is_connected(self) -> bool:
        return self._connected_output is not None

    def get_save_data(self) -> dict[str, t.Any]:
        connected = self.connected_output
        if connected is None:
            connected_data = None
        else:
            connected_data = collections.OrderedDict((
                ('component_id', connected.component.id),
                ('index', connected.index)
            ))
        return collections.OrderedDict((
            ('index', self.index),
            ('value', self.value),
            ('new_value', self.new_value),
            ('old_value', self.old_value),
            ('connection', connected_data),
            ('wire_positions', [tuple(pos) for pos in self.wire_positions])
        ))

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
        self._wire_positions = [
            shapes.Vector2(pos) for pos in data['wire_positions']
        ]

    def update(self) -> None:
        self._old_value, self._value = self._value, self._new_value

    def connect(self, output: '_Output',
                wire_positions: t.Optional[list[shapes.Vector2]] = None) -> None:
        if self._connected_output is output:
            self._wire_positions = wire_positions or []
            return
        self.disconnect()
        self._connected_output = output
        self._wire_positions = wire_positions or []
        self.value = output.value
        output.connect(self, wire_positions)

    def disconnect(self) -> None:
        output = self._connected_output
        if output is None:
            return
        self.value = None
        self._connected_output = None
        self._wire_positions = []
        output.disconnect(self)

    def __str__(self) -> str:
        return 'Input[comp={} idx={}]'.format(self.component, self.index)


class _Output:
    def __init__(self, component: Component, index: int) -> None:
        self._component = component
        self._index = index
        self._value: t.Any = None
        self._connected_inputs: set[_Input] = set()

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
    def connected_inputs(self) -> abc.Iterator[_Input]:
        return iter(self._connected_inputs)

    def is_connected(self) -> bool:
        return bool(self._connected_inputs)

    def get_save_data(self) -> dict[str, t.Any]:
        return collections.OrderedDict((
            ('index', self.index),
            ('value', self.value)
        ))

    def connect(self, input: _Input,
                wire_positions: t.Optional[list[shapes.Vector2]] = None) -> None:
        if input in self._connected_inputs:
            return
        self._connected_inputs.add(input)
        input.connect(self, wire_positions)

    def disconnect(self, input: _Input) -> None:
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


class _ReadOnlyList(t.Generic[_T]):
    def __init__(self, lst: list[_T]) -> None:
        self._lst = lst

    def __getitem__(self, idx: int) -> _T:
        return self._lst[idx]

    def __str__(self) -> str:
        return str(self._lst)

    def __repr__(self) -> str:
        return repr(self._lst)

    def __iter__(self) -> abc.Iterator[_T]:
        return iter(self._lst)

    def __len__(self) -> int:
        return len(self._lst)
