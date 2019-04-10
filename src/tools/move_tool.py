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

    def on_move(self, app, event, position):
        super().on_move(app, event, position)
        if self._move_data:
            for component, offset in self._move_data:
                component.display.position = (
                    app.snap_position(offset + position) - (0, app.grid_size/2)
                )
            app.repaint()
