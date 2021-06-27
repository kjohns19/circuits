import collections
import collections.abc as abc
import typing as t

from gi.repository import Gtk  # type: ignore

from . import circuit as circuit_mod

if t.TYPE_CHECKING:
    from . import component as component_mod
    from . import properties


_CIRCUIT = circuit_mod.Circuit()


class Creator:
    def __init__(self, creator_func: abc.Callable[[circuit_mod.Circuit],
                                                  'component_mod.Component'],
                 name: str, category: str) -> None:
        self._creator_func = creator_func
        self._name = name
        self._category = category
        self._base_component = creator_func(_CIRCUIT)
        self._properties: list['properties.Property[t.Any]'] = []

    @property
    def category(self) -> str:
        return self._category

    @property
    def name(self) -> str:
        return self._name

    def get_save_data(self) -> dict[str, str]:
        return collections.OrderedDict((
            ('category', self._category),
            ('name', self._name)
        ))

    def add_property(self, property: 'properties.Property[t.Any]') -> None:
        self._properties.append(property)

    def get_property_widgets(self,
                             component: t.Optional['component_mod.Component'] = None,
                             callback: t.Optional[
                                abc.Callable[['properties.Property[t.Any]',
                                              'component_mod.Component', t.Any],
                                             None]] = None) -> list[Gtk.Widget]:
        if component is None:
            component = self._base_component
        return [
            property.create_widget(component, callback)
            for property in self._properties
        ]

    def __call__(self, circuit: circuit_mod.Circuit) -> 'component_mod.Component':
        component = self._creator_func(circuit)
        for property in self._properties:
            property.apply(self._base_component, component)
        component.creator = self
        return component
