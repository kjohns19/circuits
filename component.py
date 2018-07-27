from component_display import ComponentDisplay


class ComponentException(Exception):
    pass


class Component:
    def __init__(self, circuit, num_inputs, num_outputs,
                 update_func, display_func=None):
        self._circuit = circuit
        self._new_inputs = [None]*num_inputs
        self._old_inputs = [None]*num_inputs
        self._inputs = [None]*num_inputs
        self._input_components = [None]*num_inputs

        self._outputs = [None]*num_outputs
        self._output_components = [set() for i in range(num_outputs)]

        self._update_func = update_func
        self._display = ComponentDisplay(self, display_func)
        self._circuit.add_component(self)

    @property
    def inputs(self):
        return _ReadOnlyList(self._inputs)

    @property
    def old_inputs(self):
        return _ReadOnlyList(self._old_inputs)

    @property
    def new_inputs(self):
        return _ReadOnlyList(self._new_inputs)

    @property
    def outputs(self):
        return _OutputProxy(self)

    @property
    def input_connections(self):
        return iter(self._input_components)

    @outputs.setter
    def outputs(self, lst):
        if len(lst) != len(self._outputs):
            raise ComponentException(
                'Mismatched size when assigning outputs: {} vs {}'.format(
                    len(lst), len(self._outputs)))
        outputs = self.outputs
        for idx, value in enumerate(lst):
            outputs[idx] = value

    @property
    def display(self):
        return self._display

    def schedule_update(self, delay=1):
        self._circuit.schedule_update(self, delay)

    def update_inputs(self):
        self._old_inputs = self._inputs
        self._inputs = list(self._new_inputs)

    def update(self):
        self._update_func(self)

    def connect_input(self, input_idx, component, output_idx):
        self._input_components[input_idx] = (component, output_idx)
        component._output_components[output_idx].add((self, input_idx))
        self._new_inputs[input_idx] = component.outputs[output_idx]
        self.schedule_update()

    def disconnect_input(self, input_idx):
        component, output_idx = self._input_components[input_idx]
        self._input_components[input_idx] = None
        component._output_components[output_idx].remove((self, input_idx))

    def __str__(self):
        return (
            'Component[old_inputs={} inputs={}'
            ' new_inputs={} outputs={}]'.format(
                self._old_inputs, self._inputs,
                self._new_inputs, self._outputs))


class _OutputProxy:
    def __init__(self, component):
        self._component = component

    def __getitem__(self, idx):
        return self._component._outputs[idx]

    def __setitem__(self, idx, value):
        self._component._outputs[idx] = value
        for component, input_idx in self._component._output_components[idx]:
            component._new_inputs[input_idx] = value
            component.schedule_update()

    def __str__(self):
        return str(self._component._outputs)

    def __repr__(self):
        return repr(self._component._outputs)

    def __iter__(self):
        return iter(self._component._outputs)

    def __len__(self):
        return len(self._component._outputs)


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
