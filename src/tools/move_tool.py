from .tool import Tool


class MoveTool(Tool):
    def __init__(self):
        super().__init__()
        self._move_data = []

    def _set(self, components, position):
        self._move_data = [
            (component, component.display.position - position)
            for component in components
        ]

    def on_left_click(self, app, event, position, component):
        if component is not None:
            self._set([component], position)

    def on_left_release(self, app, event, position, component):
        self._move_data = []

    def on_right_click(self, app, event, position, component):
        if component is not None:
            components = set()
            _build_connected_components(component, components)
            self._set(components, position)

    def on_right_release(self, app, event, position, component):
        self._move_data = []

    def on_move(self, app, event, position):
        super().on_move(app, event, position)
        if self._move_data:
            for component, offset in self._move_data:
                component.display.position = (
                    app.snap_position(offset + position) - (0, app.grid_size/2)
                )
            app.repaint()


def _build_connected_components(component, components):
    if component in components:
        return
    components.add(component)
    for input in component.inputs:
        if input.is_connected():
            output = input.connected_output.component
            _build_connected_components(output, components)
    for output in component.outputs:
        for connected_input in output.connected_inputs:
            _build_connected_components(connected_input.component, components)
