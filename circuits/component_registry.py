import collections.abc as abc
import dataclasses
import functools
import typing as t

from . import creator as creator_mod
from . import properties
from . import utils

if t.TYPE_CHECKING:
    from . import circuit as circuit_mod
    from . import component as component_mod


@dataclasses.dataclass
class ComponentData:
    name: str
    category: str
    creator: creator_mod.Creator


class Registry:
    def __init__(self) -> None:
        self._component_data: list[ComponentData] = []

    def register(self, name: str, category: str = 'Uncategorized') \
            -> abc.Callable[[abc.Callable[['circuit_mod.Circuit'],
                                          'component_mod.Component']],
                            creator_mod.Creator]:
        ''' Register a component creator

        Example:
        @registry.register(name='My Component', category='My Category')
        def create_component(circuit):
            return Component(...)
        '''
        def decorator(f: abc.Callable[['circuit_mod.Circuit'],
                                      'component_mod.Component']) \
                -> creator_mod.Creator:
            @functools.wraps(f)
            def creator_func(circuit: 'circuit_mod.Circuit') \
                    -> 'component_mod.Component':
                component = f(circuit)
                component.name = name
                return component

            creator = creator_mod.Creator(creator_func, name, category)

            creator.add_property(properties.StringProperty(
                getter=utils.attr_getter('name'),
                setter=utils.attr_setter('name'),
                label='Name'))

            self._component_data.append(ComponentData(name, category, creator))

            return creator
        return decorator

    def get_creator(self, category: str, name: str) -> creator_mod.Creator:
        for data in self._component_data:
            creator = data.creator
            if creator.category == category and creator.name == name:
                return creator
        raise RuntimeError(f'No creator for category {category}, name {name}')

    def get_component_data(self) -> list[ComponentData]:
        return list(self._component_data)


# Global registry
registry: Registry = Registry()
