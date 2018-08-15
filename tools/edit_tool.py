from .tool import Tool
from utils import MouseButton


class EditTool(Tool):
    def __init__(self):
        self._component = None
        self._offset = None

    def on_click(self, app, event, button, position, component):
        if button == MouseButton.LEFT and component is not None:
            self._component = component
            self._offset = component.display.position - position
        elif button == MouseButton.RELEASE_LEFT:
            self._component = None

    def on_move(self, app, event, position):
        if self._component:
            self._component.display.position = self._offset + position
            app.repaint()
