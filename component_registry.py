import collections


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
            self._component_data.append(ComponentData(
                name=name, category=category, creator=f))
            return f
        return decorator

    def get_component_data(self):
        return list(self._component_data)


# Global registry
registry = Registry()
