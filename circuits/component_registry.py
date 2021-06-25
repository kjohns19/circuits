import collections
import functools

from . import creator as creator_module
from . import properties
from . import utils


ComponentData = collections.namedtuple(
    'ComponentData',
    ['name', 'category', 'creator'])


class Registry:
    def __init__(self):
        self._component_data = []

    def register(self, name, category='Uncategorized'):
        ''' Register a component creator

        Example:
        @registry.register(name='My Component', category='My Category')
        def create_component(circuit):
            return Component(...)
        '''
        def decorator(f):
            @functools.wraps(f)
            def creator_func(circuit):
                component = f(circuit)
                component.name = name
                return component

            creator = creator_module.Creator(creator_func, name, category)

            creator.add_property(properties.StringProperty(
                getter=utils.attr_getter('name'),
                setter=utils.attr_setter('name'),
                label='Name'))

            self._component_data.append(ComponentData(
                name=name, category=category, creator=creator))

            return creator
        return decorator

    def get_creator(self, category, name):
        for data in self._component_data:
            creator = data.creator
            if creator.category == category and creator.name == name:
                return creator
        return None

    def get_component_data(self):
        return list(self._component_data)


# Global registry
registry = Registry()
