from .tool import Tool


class EditTool(Tool):
    def __init__(self):
        self._move_component = None
        self._offset = None

    def on_left_click(self, app, event, position, component):
        if component is not None:
            self._move_component = component
            self._offset = component.display.position - position

    def on_left_release(self, app, event, position, component):
        self._move_component = None

    def on_right_click(self, app, event, position, component):
        if component is not None:
            app.show_component_properties(component)

    def on_move(self, app, event, position):
        if self._move_component:
            self._move_component.display.position = app.snap_position(
                self._offset + position)
            app.repaint()
