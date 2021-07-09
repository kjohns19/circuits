import collections.abc as abc
import collections
import threading
import typing as t

from gi.repository import Gdk  # type: ignore

from . import component as component_mod
from . import shapes


class Circuit:
    def __init__(self) -> None:
        self._components: set[component_mod.Component] = set()
        self._updates: dict[int, set[component_mod.Component]] = \
            collections.defaultdict(set)
        self._time = 0
        self._current_id = 0
        self._update_lock = threading.Lock()
        self._key_callbacks: dict[int, abc.Callable[[Gdk.EventKey], None]] = {}

    @property
    def time(self) -> int:
        return self._time

    def add_component(self, component: component_mod.Component) -> None:
        self._components.add(component)
        component.id = self._current_id
        self._current_id += 1

    def get_save_data(self, components: t.Optional[
            abc.Collection[component_mod.Component]] = None) -> dict[str, t.Any]:
        save_components = components or self._components
        with self._update_lock:
            components_by_id = sorted(save_components, key=lambda c: c.id)
            component_data = [
                component.get_save_data()
                for component in components_by_id
            ]
            update_data = {
                time - self._time: list(sorted(
                    c.id for c in components if c in save_components))
                for time, components in self._updates.items()
            }
            return {
                'components': component_data,
                'updates': update_data
            }

    def register_key_callback(self,
                              callback: abc.Callable[[Gdk.EventKey], None]) -> int:
        callback_id = len(self._key_callbacks)
        self._key_callbacks[callback_id] = callback
        return callback_id

    def unregister_key_callback(self, callback_id: int) -> None:
        del self._key_callbacks[callback_id]

    def handle_key_press(self, event: Gdk.EventKey) -> None:
        for callback in self._key_callbacks.values():
            callback(event)

    def load(self, data: dict[str, t.Any]) -> set[component_mod.Component]:
        with self._update_lock:
            self.clear()
            return self._load_data_lk(data)

    def load_module(self, data: dict[str, t.Any]) -> set[component_mod.Component]:
        with self._update_lock:
            return self._load_data_lk(data)

    def _load_data_lk(self, data: dict[str, t.Any]) -> set[component_mod.Component]:
        component_data_by_id = {}
        components_by_id = {}

        save_updates = self._updates.copy()

        # Create components
        for component_data in data['components']:
            component = component_mod.Component.load(self, component_data)
            component_data_by_id[component.id] = component_data
            components_by_id[component_data['id']] = component

        # Load input connections
        # This must be done after component creation
        # so all components exist
        new_components = set(components_by_id.values())
        for component in new_components:
            component_data = component_data_by_id[component.id]
            component.load_inputs(component_data, components_by_id)

        self._components.update(new_components)

        self._updates = save_updates
        for delay, ids in data['updates'].items():
            time = self._time + int(delay)
            self._updates[time].update(components_by_id[id] for id in ids)

        return new_components

    def remove_component(self, component: component_mod.Component) -> None:
        component.on_destroy()
        self._components.remove(component)
        with self._update_lock:
            for updates in self._updates.values():
                if component in updates:
                    updates.remove(component)

    def clear(self) -> None:
        for component in self._components:
            component.on_destroy()
        self._components = set()
        self._updates = collections.defaultdict(set)
        self._time = 0
        self._current_id = 0

    @property
    def components(self) -> abc.Iterator[component_mod.Component]:
        return iter(self._components)

    def component_at_position(self, position: shapes.VecOrTup) \
            -> t.Optional[component_mod.Component]:
        for component in self._components:
            if component.display.bounds.contains_point(position):
                return component
        return None

    def components_in_rectangle(self, rectangle: shapes.Rectangle) \
            -> list[component_mod.Component]:
        return [
            component for component in self._components
            if rectangle.contains_rectangle(component.display.rect)
        ]

    def wire_node_at_position(self, position: shapes.VecOrTup) \
            -> t.Optional[component_mod.WireNode]:
        for component in self._components:
            for input in component.inputs:
                for node in input.wire_nodes:
                    if node.position == position:
                        return node
        return None

    def wire_nodes_in_rectangle(self, rectangle: shapes.Rectangle) \
            -> list[component_mod.WireNode]:
        nodes: list[component_mod.WireNode] = []
        for component in self._components:
            for input in component.inputs:
                for node in input.wire_nodes:
                    if rectangle.contains_point(node.position):
                        nodes.append(node)
        return nodes

    def schedule_update(self, component: component_mod.Component, delay: int) -> None:
        if delay < 1:
            delay = 1
        self._updates[self._time+delay].add(component)

    def components_to_update(self) -> tuple[set[component_mod.Component],
                                            set[component_mod.Component]]:
        with self._update_lock:
            next_updates = set()
            later_updates = set()
            for time, components in self._updates.items():
                if time == self._time+1:
                    next_updates.update(components)
                else:
                    later_updates.update(components)
        return next_updates, later_updates

    def update(self) -> None:
        with self._update_lock:
            self._time += 1
            components_to_update = self._updates[self._time]
            for component in components_to_update:
                component.update_inputs()
            for component in components_to_update:
                component.on_update()
            del self._updates[self._time]
