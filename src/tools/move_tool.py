from .tool import Tool


class MoveTool(Tool):
    def __init__(self):
        super().__init__()
        self._move_component = None
        self._offset = None

    def on_left_click(self, app, event, position, component):
        if component is not None:
            self._move_component = component
            self._offset = component.display.position - position

    def on_left_release(self, app, event, position, component):
        self._move_component = None

    def on_move(self, app, event, position):
        super().on_move(app, event, position)
        if self._move_component:
            self._move_component.display.position = app.snap_position(
                self._offset + position) - (0, app.grid_size/2)
            app.repaint()
