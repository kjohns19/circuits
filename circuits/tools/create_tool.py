from .tool import Tool
import utils


class CreateTool(Tool):
    def __init__(self, creator=None):
        super().__init__()
        self._creator = creator
        self._component = None

    @property
    def creator(self):
        return self._creator

    @creator.setter
    def creator(self, value):
        self._creator = value

    def on_left_click(self, app, event, position, component):
        if self._creator is not None:
            self._component = self._creator(app.circuit)
            self._component.display.position = (
                app.snap_position(position) - (0, app.grid_size/2))
            app.repaint()

    def on_left_release(self, app, event, position, component):
        self._component = None

    def on_right_click(self, app, event, position, component):
        if not component:
            return

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
        super().on_move(app, event, position)
        if self._component:
            self._component.display.position = (
                app.snap_position(position) - (0, app.grid_size/2))
            app.repaint()
