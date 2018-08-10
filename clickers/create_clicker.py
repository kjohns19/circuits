from .clicker import Clicker
import utils


class CreateClicker(Clicker):
    def __init__(self, creator=None):
        self._creator = creator

    @property
    def creator(self):
        return self._creator

    @creator.setter
    def creator(self, value):
        self._creator = value

    def on_click(self, app, event, button, position, component):
        if self._creator is None:
            return

        if button == utils.MouseButton.LEFT:
            new_component = self._creator(app.circuit)
            new_component.display.position = position
            app.repaint()
        elif button == utils.MouseButton.RIGHT and component:
            def callback(selection):
                if selection == 'Yes':
                    component.delete()
                    app.repaint()

            utils.show_popup('Delete?', ['Yes', 'No'], event, callback)
