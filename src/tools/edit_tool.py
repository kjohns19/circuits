from .tool import Tool


class EditTool(Tool):
    def __init__(self):
        super().__init__()
        self._components = set()
        self._move_data = []

    def _set(self, components, position):
        self._move_data = [
            (component, component.display.position - position)
            for component in components
        ]

    def on_left_click(self, app, event, position, component):
        keys = ['Control_R', 'Control_L']
        if not any(app.is_key_pressed(key) for key in keys):
            self._components.clear()
        if component is not None:
            if component in self._components:
                self._components.remove(component)
                return
            else:
                self._components.add(component)

        self._move_data = [
            (component, component.display.position - position)
            for component in self._components
        ]

    def on_left_release(self, app, event, position, component):
        self._move_data = []

    def on_right_click(self, app, event, position, component):
        if component is not None:
            app.show_component_properties(component)

    def on_move(self, app, event, position):
        super().on_move(app, event, position)
        if self._move_data:
            for component, offset in self._move_data:
                component.display.position = (
                    app.snap_position(offset + position) - (0, app.grid_size/2)
                )
            app.repaint()
