from .clicker import Clicker
from utils import MouseButton


class EditClicker(Clicker):
    def __init__(self):
        self._component = None

    def on_click(self, app, event, button, position, component):
        if button == MouseButton.LEFT:
            self._component = component
        elif button == MouseButton.RELEASE_LEFT:
            self._component = None

    def on_move(self, app, event, position):
        if self._component:
            self._component.display.position = position
            app.repaint()
