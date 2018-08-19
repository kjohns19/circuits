import collections
import threading


class Circuit:
    def __init__(self):
        self._components = set()
        self._updates = collections.defaultdict(set)
        self._time = 0
        self._current_id = 0
        self._update_lock = threading.Lock()

    def add_component(self, component):
        self._components.add(component)
        component.id = self._current_id
        self._current_id += 1

    def get_save_data(self):
        with self._update_lock:
            components_by_id = sorted(self._components, key=lambda c: c.id)
            component_data = [
                component.get_save_data()
                for component in components_by_id
            ]
            update_data = collections.OrderedDict((
                (time - self._time, list(sorted(c.id for c in components)))
                for time, components in self._updates.items()
            ))
            return collections.OrderedDict((
                ('components', component_data),
                ('updates', update_data)
            ))

    def load(self, data):
        # TODO
        pass

    def remove_component(self, component):
        self._components.remove(component)

    def clear(self):
        self._components = set()

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
        with self._update_lock:
            self._time += 1
            components_to_update = self._updates[self._time]
            for component in components_to_update:
                component.update_inputs()
            for component in components_to_update:
                component.on_update()
            del self._updates[self._time]
