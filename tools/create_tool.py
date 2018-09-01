from .tool import Tool
import utils


class CreateTool(Tool):
    def __init__(self, creator=None):
        self._creator = creator
        self._component = None

    @property
    def creator(self):
        return self._creator

    @creator.setter
    def creator(self, value):
        self._creator = value

    def on_click(self, app, event, button, position, component):
        if self._creator is None:
            return

        if button == utils.MouseButton.RELEASE_LEFT:
            self._component = None
        if button == utils.MouseButton.LEFT:
            self._component = self._creator(app.circuit)
            self._component.display.position = position
            app.repaint()
        elif button == utils.MouseButton.RIGHT and component:
            if component is self._component:
                component.delete()
                app.repaint()
                self._component = None
                return

            def callback(idx, selection):
                if selection == 'Yes':
                    component.delete()
                    app.repaint()

            utils.show_popup('Delete?', ['Yes', 'No'], event, callback)

    def on_move(self, app, event, position):
        if self._component:
            self._component.display.position = app.snap_position(position)
            app.repaint()
