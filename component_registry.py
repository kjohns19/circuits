from creator import Creator

import collections
import functools


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

            creator = Creator(creator_func)

            self._component_data.append(ComponentData(
                name=name, category=category, creator=creator))

            return creator
        return decorator

    def get_component_data(self):
        return list(self._component_data)


# Global registry
registry = Registry()
