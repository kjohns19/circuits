from component_display import ComponentDisplay

import functools


class ComponentException(Exception):
    pass


class Component:
    def __init__(self, circuit, num_inputs, num_outputs,
                 on_update=None, on_draw=None):
        self._circuit = circuit

        self._inputs = []
        self._outputs = []

        self._display = ComponentDisplay(self)

        self.num_inputs = num_inputs
        self.num_outputs = num_outputs

        self.on_update = on_update or _default_on_update
        self.on_draw   = on_draw or _default_on_draw

        self._circuit.add_component(self)

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

    def schedule_update(self, delay=1):
        self._circuit.schedule_update(self, delay)

    def update_inputs(self):
        for input in self._inputs:
            input.update()

    def __str__(self):
        return (
            'Component[inputs={} outputs={}]'.format(
                self._inputs, self._outputs))


def _default_on_update(component):
    pass


def _default_on_draw(component, window, cr):
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
        self._value = None
        self._new_value = None
        self._old_value = None
        self._connected_output = None

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

    def update(self):
        self._old_value, self._value = self._value, self._new_value

    def connect(self, output):
        if self._connected_output is output:
            return
        self.disconnect()
        self._connected_output = output
        self.value = output.value
        output.connect(self)

    def disconnect(self):
        output = self._connected_output
        if output is None:
            return
        self.value = None
        self._connected_output = None
        output.disconnect(self)

    def __str__(self):
        return 'Input[comp={} idx={}]'.format(id(self.component, self.index))


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

    @value.setter
    def value(self, value):
        self._value = value
        for input in self._connected_inputs:
            input.value = value

    def connect(self, input):
        if input in self._connected_inputs:
            return
        self._connected_inputs.add(input)
        input.connect(self)

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
        return 'Output[comp={} idx={}]'.format(id(self.component, self.index))


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
