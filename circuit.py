import collections


class Circuit:
    def __init__(self):
        self._components = set()
        self._updates = collections.defaultdict(set)

    def add_component(self, component):
        self._components.add(component)

    def remove_component(self, component):
        self._components.remove(component)

    @property
    def components(self):
        return iter(self._components)

    def schedule_update(self, component, delay):
        if delay < 1:
            delay = 1
        self._updates[delay].add(component)

    def update(self):
        new_updates = collections.defaultdict(set)
        for delay, components in self._updates.items():
            if delay <= 1:
                for component in components:
                    component.update_inputs()
                for component in components:
                    component.update()
            else:
                new_updates[delay-1] = components
        self._updates = new_updates
