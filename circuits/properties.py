from gi.repository import Gtk  # type: ignore
import collections.abc as abc
import typing as t

from . import property_widgets
from . import utils

if t.TYPE_CHECKING:
    from . import component as component_mod

_T = t.TypeVar('_T')
Getter = abc.Callable[['component_mod.Component'], _T]
Setter = abc.Callable[['component_mod.Component', _T], None]


class Property(t.Generic[_T]):
    def __init__(self, getter: Getter[_T], setter: Setter[_T]) -> None:
        self._getter = getter
        self._setter = setter

    @property
    def getter(self) -> Getter[_T]:
        return self._getter

    @property
    def setter(self) -> Setter[_T]:
        return self._setter

    def apply(self, from_component: 'component_mod.Component',
              to_component: 'component_mod.Component') -> None:
        self.setter(to_component, self.getter(from_component))

    def create_widget(self, component: 'component_mod.Component',
                      callback: t.Optional[
                        abc.Callable[['Property[_T]', 'component_mod.Component', _T],
                                     None]] = None) -> Gtk.Widget:
        def real_callback(value: _T) -> None:
            self._setter(component, value)
            if callback:
                callback(self, component, value)
        return self.real_create_widget(component, real_callback)

    def real_create_widget(self, component: 'component_mod.Component',
                           callback: abc.Callable[[_T], None]) -> Gtk.Widget:
        raise NotImplementedError()


class BoolProperty(Property[bool]):
    def __init__(self, getter: Getter[bool], setter: Setter[bool],
                 label: str = 'Value') -> None:
        super().__init__(getter, setter)
        self._label = label

    def real_create_widget(self, component: 'component_mod.Component',
                           callback: abc.Callable[[bool], None]) -> Gtk.Widget:
        return property_widgets.create_value_bool_widget(
            label=self._label,
            callback=callback,
            initial_value=self.getter(component))


class NumberProperty(Property[int]):
    def __init__(self, getter: Getter[int], setter: Setter[int],
                 min_value: int = 0, max_value: int = 10,
                 label: str = 'Value') -> None:
        super().__init__(getter, setter)
        self._label = label
        self._min_value = min_value
        self._max_value = max_value

    def real_create_widget(self, component: 'component_mod.Component',
                           callback: abc.Callable[[int], None]) -> Gtk.Widget:
        return property_widgets.create_value_int_widget(
            label=self._label,
            callback=callback,
            min_value=self._min_value,
            max_value=self._max_value,
            initial_value=self.getter(component))


class NumInputsProperty(NumberProperty):
    def __init__(self,
                 callback: t.Optional[abc.Callable[['component_mod.Component', int],
                                                   None]] = None,
                 min_value: int = 0, max_value: int = 10,
                 label: str = 'Number of inputs'):
        def setter(component: 'component_mod.Component', value: int) -> None:
            setattr(component, 'num_inputs', value)
            if self._callback:
                self._callback(component, value)
        super().__init__(
            getter=utils.attr_getter('num_inputs'),
            setter=setter,
            min_value=min_value, max_value=max_value, label=label)
        self._callback = callback

    def real_create_widget(self, component: 'component_mod.Component',
                           callback: abc.Callable[[int], None]) -> Gtk.Widget:
        def real_callback(value: int) -> None:
            callback(value)
            if self._callback is not None:
                self._callback(component, value)

        return super().real_create_widget(component, real_callback)


class NumOutputsProperty(NumberProperty):
    def __init__(self,
                 callback: t.Optional[abc.Callable[['component_mod.Component', int],
                                                   None]] = None,
                 min_value: int = 0, max_value: int = 10,
                 label: str = 'Number of outputs'):
        def setter(component: 'component_mod.Component', value: int) -> None:
            setattr(component, 'num_outputs', value)
            if self._callback:
                self._callback(component, value)
        super().__init__(
            getter=utils.attr_getter('num_outputs'),
            setter=setter,
            min_value=min_value, max_value=max_value, label=label)
        self._callback = callback

    def real_create_widget(self, component: 'component_mod.Component',
                           callback: abc.Callable[[int], None]) -> Gtk.Widget:
        def real_callback(value: int) -> None:
            callback(value)
            if self._callback is not None:
                self._callback(component, value)

        return super().real_create_widget(component, real_callback)


class StringProperty(Property[str]):
    def __init__(self, getter: Getter[str], setter: Setter[str], label: str) -> None:
        super().__init__(getter, setter)
        self._label = label

    def real_create_widget(self, component: 'component_mod.Component',
                           callback: abc.Callable[[str], None]) -> Gtk.Widget:
        return property_widgets.create_value_string_widget(
            label=self._label,
            callback=callback,
            initial_value=self.getter(component))


class MultiValueProperty(Property[list[t.Any]]):
    def __init__(self, getter: Getter[list[t.Any]], setter: Setter[list[t.Any]],
                 labels: list[str], title: str = 'Values') -> None:
        super().__init__(getter, setter)
        self._labels = labels
        self._title = title

    def real_create_widget(self, component: 'component_mod.Component',
                           callback: abc.Callable[[list[t.Any]], None]) -> Gtk.Widget:
        return property_widgets.create_multi_value_widget(
            title=self._title,
            callback=callback,
            labels=self._labels,
            initial_values=self.getter(component))


class RangedMultiValueProperty(Property[list[t.Any]]):
    def __init__(self, getter: Getter[list[t.Any]], setter: Setter[list[t.Any]],
                 min_values: int = 1, max_values: int = 10,
                 title: str = 'Values', start_index: int = 1):
        super().__init__(getter, setter)
        self._min_values = min_values
        self._max_values = max_values
        self._title = title
        self._start_index = start_index

    def real_create_widget(self, component: 'component_mod.Component',
                           callback: abc.Callable[[list[t.Any]], None]) -> Gtk.Widget:
        return property_widgets.create_ranged_multi_value_widget(
            title=self._title,
            callback=callback,
            initial_values=self.getter(component),
            min_values=self._min_values,
            max_values=self._max_values,
            start_index=self._start_index)
