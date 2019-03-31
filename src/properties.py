import property_widgets
import utils


class Property:
    def __init__(self, getter, setter):
        self._getter = getter
        self._setter = setter

    @property
    def getter(self):
        return self._getter

    @property
    def setter(self):
        return self._setter

    def apply(self, from_component, to_component):
        self.setter(to_component, self.getter(from_component))

    def create_widget(self, component, callback=None):
        def real_callback(value):
            self._setter(component, value)
            if callback:
                callback(self, component, value)
        return self.real_create_widget(component, real_callback)


class BoolProperty(Property):
    def __init__(self, getter, setter, label='Value'):
        super().__init__(getter, setter)
        self._label = label

    def real_create_widget(self, component, callback):
        return property_widgets.create_value_bool_widget(
            label=self._label,
            callback=callback,
            initial_value=self.getter(component))


class NumberProperty(Property):
    def __init__(self, getter, setter,
                 min_value=0, max_value=10,
                 label='Value'):
        super().__init__(getter, setter)
        self._label = label
        self._min_value = min_value
        self._max_value = max_value

    def real_create_widget(self, component, callback):
        return property_widgets.create_value_int_widget(
            label=self._label,
            callback=callback,
            min_value=self._min_value,
            max_value=self._max_value,
            initial_value=self.getter(component))


def _create_num_inout_property(name, attr_name, label):
    class NumInOutProperty(NumberProperty):
        def __init__(self, callback=None,
                     min_value=0, max_value=10,
                     label=label):
            def setter(component, value):
                utils.attr_setter(attr_name)(component, value)
                if callback:
                    callback(component, value)
            super().__init__(
                getter=utils.attr_getter(attr_name),
                setter=setter,
                min_value=min_value, max_value=max_value, label=label)
            self._callback = callback

        def real_create_widget(self, component, callback):
            def real_callback(value):
                callback(value)
                if self._callback is not None:
                    self._callback(component, value)

            return super().real_create_widget(component, real_callback)

    NumInOutProperty.__name__ = name
    return NumInOutProperty


NumInputsProperty = _create_num_inout_property(
    'NumInputsProperty', 'num_inputs', 'Number of inputs')

NumOutputsProperty = _create_num_inout_property(
    'NumOutputsProperty', 'num_outputs', 'Number of outputs')


class StringProperty(Property):
    def __init__(self, getter, setter, label):
        super().__init__(getter, setter)
        self._label = label

    def real_create_widget(self, component, callback):
        return property_widgets.create_value_string_widget(
            label=self._label,
            callback=callback,
            initial_value=self.getter(component))


class MultiValueProperty(Property):
    def __init__(self, getter, setter, labels, title='Values'):
        super().__init__(getter, setter)
        self._labels = labels
        self._title = title

    def real_create_widget(self, component, callback):
        return property_widgets.create_multi_value_widget(
            title=self._title,
            callback=callback,
            labels=self._labels,
            initial_values=self.getter(component))


class RangedMultiValueProperty(Property):
    def __init__(self, getter, setter,
                 min_values=1, max_values=10,
                 title='Values'):
        super().__init__(getter, setter)
        self._min_values = min_values
        self._max_values = max_values
        self._title = title

    def real_create_widget(self, component, callback):
        return property_widgets.create_ranged_multi_value_widget(
            title=self._title,
            callback=callback,
            min_values=self._min_values,
            max_values=self._max_values,
            initial_values=self.getter(component))