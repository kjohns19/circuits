from .clicker import Clicker
import utils


class WireClicker(Clicker):
    def __init__(self):
        self._input = None

    def on_click(self, app, event, position, component):
        if component is None:
            self._input = None
            return

        def input_callback(selection):
            self._input = component.inputs[int(selection)]

        def output_callback(selection):
            output = component.outputs[int(selection)]
            self._input.connect(output)
            self._input = None
            app.repaint()

        if self._input is None:
            count = component.num_inputs
            title = 'Inputs'
            callback = input_callback
        else:
            count = component.num_outputs
            title = 'Outputs'
            callback = output_callback

        options = [str(i) for i in range(count)]
        utils.show_popup(title, options, event, callback)
