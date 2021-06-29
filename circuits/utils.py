import collections.abc as abc
import enum
import inspect
import pathlib
import typing as t

from gi.repository import Gtk, Gdk  # type: ignore

from . import circuit as circuit_mod
from . import component as component_mod
from . import component_registry
from . import properties


class MouseButton(enum.IntEnum):
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    RELEASE_LEFT = -1
    RELEASE_MIDDLE = -2
    RELEASE_RIGHT = -3

    @classmethod
    def is_press(cls, button: 'MouseButton') -> bool:
        return button > 0

    @classmethod
    def is_release(cls, button: 'MouseButton') -> bool:
        return button < 0


def data_file(name: str) -> str:
    data_dir = pathlib.Path(__file__).resolve().parent.parent / 'data'
    return str(data_dir / name)


def get_connected_components(components: abc.Iterable['component_mod.Component']) \
        -> set['component_mod.Component']:
    def build(component: 'component_mod.Component',
              components: set['component_mod.Component']) -> None:
        if component in components:
            return
        components.add(component)
        for input in component.inputs:
            output = input.connected_output
            if output is not None:
                build(output.component, components)
        for output in component.outputs:
            for connected_input in output.connected_inputs:
                build(connected_input.component, components)
    all_components: set['component_mod.Component'] = set()
    for component in components:
        build(component, all_components)
    return all_components


def show_popup(title: str, options: abc.Iterable[str], event: Gdk.EventButton,
               callback: abc.Callable[[int, str], None]) -> None:
    menu = Gtk.Menu()

    title_menu = Gtk.MenuItem(title)
    title_menu.set_sensitive(False)
    menu.append(title_menu)

    for i, option in enumerate(options):
        def activate(widget: Gtk.Widget, option: str = option, i: int = i) -> None:
            callback(i, option)

        item = Gtk.MenuItem(option)
        item.connect('activate', activate)
        menu.append(item)

    menu.show_all()
    menu.popup(None, None, None, None, event.button, event.time)


def create_nary_component(name: str, category: str, function: abc.Callable[..., t.Any],
                          min_inputs: t.Optional[int] = None,
                          max_inputs: t.Optional[int] = None,
                          input_labels: t.Optional[list[str]] = None,
                          output_labels: t.Optional[list[str]] = None,
                          default_value: t.Optional[t.Any] = None) -> None:
    real_min_inputs = min_inputs or len(inspect.signature(function).parameters)
    max_inputs = max_inputs or real_min_inputs

    @component_registry.registry.register(name, category)
    def creator(circuit: circuit_mod.Circuit) -> 'component_mod.Component':
        def on_update(component: 'component_mod.Component') -> None:
            operands = (input.value for input in component.inputs)
            try:
                result = function(*operands)
            except Exception:
                result = default_value
            component.outputs[0].value = result
        component = component_mod.Component(
            circuit, num_inputs=real_min_inputs, num_outputs=1, on_update=on_update,
            input_labels=input_labels, output_labels=output_labels)
        on_update(component)
        return component

    if real_min_inputs != max_inputs:
        creator.add_property(properties.NumInputsProperty(
            min_value=real_min_inputs, max_value=max_inputs))


def data_getter(name: str) -> abc.Callable[['component_mod.Component'], t.Any]:
    return lambda component: component.data[name]


def data_setter(name: str) -> abc.Callable[['component_mod.Component', t.Any], None]:
    def setter(component: 'component_mod.Component', value: t.Any) -> None:
        component.data[name] = value
    return setter


def attr_getter(name: str) -> abc.Callable[['component_mod.Component'], t.Any]:
    return lambda component: getattr(component, name)


def attr_setter(name: str) -> abc.Callable[['component_mod.Component', t.Any], None]:
    return lambda component, value: setattr(component, name, value)


_T = t.TypeVar('_T')


def get_builder_obj(builder: Gtk.Builder, name: str, object_type: t.Type[_T]) -> _T:
    obj = builder.get_object(name)
    if obj is None:
        raise RuntimeError(f'Failed to find object {name}')
    if not isinstance(obj, object_type):
        raise RuntimeError(
            f'Mismatched object type. '
            f'Expected {object_type.__name__}, got {type(obj).__name__}')
    return obj
