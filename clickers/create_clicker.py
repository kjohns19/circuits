from .clicker import Clicker


class CreateClicker(Clicker):
    def __init__(self, creator=None):
        self._creator = creator

    @property
    def creator(self):
        return self._creator

    @creator.setter
    def creator(self, value):
        self._creator = value

    def on_click(self, app, event, position, component):
        if self._creator is None:
            return
        # TODO check button
        new_component = self._creator(app.circuit)
        new_component.display.position = position
        app.repaint()
