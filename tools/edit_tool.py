from .tool import Tool
from utils import MouseButton


class EditTool(Tool):
    def __init__(self):
        self._move_component = None
        self._offset = None

    def on_click(self, app, event, button, position, component):
        if button == MouseButton.LEFT and component is not None:
            self._move_component = component
            self._offset = component.display.position - position
        elif button == MouseButton.RELEASE_LEFT:
            self._move_component = None
        elif button == MouseButton.RIGHT and component is not None:
            app.show_component_properties(component)

    def on_move(self, app, event, position):
        if self._move_component:
            self._move_component.display.position = app.snap_position(
                self._offset + position)
            app.repaint()
