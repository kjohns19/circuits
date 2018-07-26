import collections


class Circuit:
    def __init__(self):
        self._components = set()
        self._updates = collections.defaultdict(set)
        self._time = 0

    def add_component(self, component):
        self._components.add(component)

    def remove_component(self, component):
        self._components.remove(component)

    @property
    def components(self):
        return iter(self._components)

    def component_at_position(self, position):
        for component in self._components:
            if component.display.bounds.contains(position):
                return component
        return None

    def schedule_update(self, component, delay):
        if delay < 1:
            delay = 1
        self._updates[self._time+delay].add(component)

    def update(self):
        self._time += 1
        components_to_update = self._updates[self._time]
        for component in components_to_update:
            component.update_inputs()
        for component in components_to_update:
            component.on_update()
        del self._updates[self._time]
