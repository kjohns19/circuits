from .clicker import Clicker
from utils import MouseButton


class RunClicker(Clicker):
    def __init__(self):
        self._component = None

    def on_click(self, app, event, button, position, component):
        if MouseButton.is_press(button):
            self._component = component
        else:
            component = self._component
            self._component = None

        if component is None:
            return

        component.on_click(button)
        app.repaint()
