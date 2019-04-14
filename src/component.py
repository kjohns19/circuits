import component_display
import component_registry
import shapes

import collections
import functools


class ComponentException(Exception):
    pass


class Component:
    def __init__(self, circuit, num_inputs, num_outputs,
                 input_labels=None, output_labels=None,
                 on_update=None, on_draw=None, on_click=None):
        self._circuit = circuit
        self._id = None

        self._data = collections.OrderedDict()

        self._inputs = []
        self._outputs = []

        self._display = component_display.ComponentDisplay(self)

        self.num_inputs = num_inputs
        self.num_outputs = num_outputs

        self.on_update = on_update or _default_on_update
        self.on_draw   = on_draw or _default_on_draw
        self.on_click = on_click or _default_on_click

        self._circuit.add_component(self)

        self._name = None
        self._input_labels = input_labels or []
        self._output_labels = output_labels or []

        self._creator = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def circuit(self):
        return self._circuit

    @property
    def num_inputs(self):
        return len(self._inputs)

    @num_inputs.setter
    def num_inputs(self, value):
        self._inputs = _resize_list(
            lst=self._inputs,
            size=value,
            old_elem_func=lambda input, i: input.disconnect(),
            new_elem_func=lambda i: _Input(self, i))
        self._display.recalculate_size()

    @property
    def num_outputs(self):
        return len(self._outputs)

    @num_outputs.setter
    def num_outputs(self, value):
        self._outputs = _resize_list(
            lst=self._outputs,
            size=value,
            old_elem_func=lambda output, i: output.disconnect_all(),
            new_elem_func=lambda i: _Output(self, i))
        self._display.recalculate_size()

    @property
    def inputs(self):
        return _ReadOnlyList(self._inputs)

    @property
    def outputs(self):
        return _ReadOnlyList(self._outputs)

    @property
    def display(self):
        return self._display

    @property
    def data(self):
        return self._data

    @property
    def on_update(self):
        return self._on_update

    @on_update.setter
    def on_update(self, value):
        self._on_update = functools.partial(value, self)

    @property
    def on_draw(self):
        return self._on_draw

    @on_draw.setter
    def on_draw(self, value):
        self._on_draw = functools.partial(value, self)

    @property
    def on_click(self):
        return self._on_click

    @on_click.setter
    def on_click(self, value):
        self._on_click = functools.partial(value, self)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def creator(self):
        return self._creator

    @creator.setter
    def creator(self, value):
        self._creator = value

    @property
    def input_labels(self):
        return self._input_labels

    @input_labels.setter
    def input_labels(self, value):
        self._input_labels = value or []

    @property
    def output_labels(self):
        return self._output_labels

    @output_labels.setter
    def output_labels(self, value):
        self._output_labels = value or []

    def input_label(self, idx):
        if idx < len(self._input_labels):
            return self._input_labels[idx]
        if self.num_inputs == 1:
            return 'in'
        return 'in{}'.format(idx+1)

    def output_label(self, idx):
        if idx < len(self._output_labels):
            return self._output_labels[idx]
        if self.num_outputs == 1:
            return 'out'
        return 'out{}'.format(idx+1)

    def schedule_update(self, delay=1):
        self._circuit.schedule_update(self, delay)

    def update_inputs(self):
        for input in self._inputs:
            input.update()

    def delete(self):
        for input in self._inputs:
            input.disconnect()
        for output in self._outputs:
            output.disconnect_all()
        self._circuit.remove_component(self)

    def __str__(self):
        return (
            'Component[inputs={} outputs={}]'.format(
                self._inputs, self._outputs))

    def get_save_data(self):
        return collections.OrderedDict((
            ('id', self.id),
            ('name', self.name),
            ('creator', self.creator.get_save_data()),
            ('inputs', [input.get_save_data() for input in self.inputs]),
            ('outputs', [output.get_save_data() for output in self.outputs]),
            ('display', self.display.get_save_data()),
            ('data', self._data)
        ))

    @staticmethod
    def load(circuit, data):
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

    def load_inputs(self, data, components_by_id):
        input_data = data['inputs']
        for in_data in input_data:
            self.inputs[in_data['index']].load(in_data, components_by_id)


def _default_on_update(component):
    pass


def _default_on_draw(component, app, cr):
    pass


def _default_on_click(component, button):
    pass


def _resize_list(lst, size, old_elem_func, new_elem_func):
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
    def __init__(self, component, index):
        self._component = component
        self._index = index
        self._value = None
        self._new_value = None
        self._old_value = None
        self._connected_output = None
        self._wire_positions = None

    @property
    def component(self):
        return self._component

    @property
    def index(self):
        return self._index

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._new_value != value:
            self._new_value = value
            self._component.schedule_update()

    @property
    def new_value(self):
        return self._new_value

    @property
    def old_value(self):
        return self._old_value

    @property
    def connected_output(self):
        return self._connected_output

    @property
    def label(self):
        return self._component.input_label(self._index)

    @property
    def wire_positions(self):
        return self._wire_positions or []

    def move(self, amount):
        if self._wire_positions:
            self._wire_positions = [
                pos + amount
                for pos in self._wire_positions
            ]

    def is_connected(self):
        return self._connected_output is not None

    def get_save_data(self):
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

    def load(self, data, components_by_id):
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

    def update(self):
        self._old_value, self._value = self._value, self._new_value

    def connect(self, output, wire_positions=None):
        if self._connected_output is output:
            self._wire_positions = wire_positions
            return
        self.disconnect()
        self._connected_output = output
        self._wire_positions = wire_positions
        self.value = output.value
        output.connect(self, wire_positions)

    def disconnect(self):
        output = self._connected_output
        if output is None:
            return
        self.value = None
        self._connected_output = None
        self._wire_positions = None
        output.disconnect(self)

    def __str__(self):
        return 'Input[comp={} idx={}]'.format(self.component, self.index)


class _Output:
    def __init__(self, component, index):
        self._component = component
        self._index = index
        self._value = None
        self._connected_inputs = set()

    @property
    def component(self):
        return self._component

    @property
    def index(self):
        return self._index

    @property
    def value(self):
        return self._value

    @property
    def label(self):
        return self._component.output_label(self._index)

    @value.setter
    def value(self, value):
        self._value = value
        for input in self._connected_inputs:
            input.value = value

    @property
    def connected_inputs(self):
        return iter(self._connected_inputs)

    def is_connected(self):
        return bool(self._connected_inputs)

    def get_save_data(self):
        return collections.OrderedDict((
            ('index', self.index),
            ('value', self.value)
        ))

    def connect(self, input, wire_positions=None):
        if input in self._connected_inputs:
            return
        self._connected_inputs.add(input)
        input.connect(self, wire_positions)

    def disconnect(self, input):
        if input not in self._connected_inputs:
            return
        self._connected_inputs.remove(input)
        input.disconnect()

    def disconnect_all(self):
        inputs = set(self._connected_inputs)
        self._connected_inputs.clear()
        for input in inputs:
            input.disconnect()

    def __str__(self):
        return 'Output[comp={} idx={}]'.format(self.component, self.index)


class _ReadOnlyList:
    def __init__(self, lst):
        self._lst = lst

    def __getitem__(self, idx):
        return self._lst[idx]

    def __str__(self):
        return str(self._lst)

    def __repr__(self):
        return repr(self._lst)

    def __iter__(self):
        return iter(self._lst)

    def __len__(self):
        return len(self._lst)
