import component as component_module
from component_registry import registry
import utils


CATEGORY = 'Output'


@registry.register('Display', CATEGORY)
def make_display(circuit):
    def on_draw(component, app, cr):
        text = str(component.inputs[0].value)
        position = component.display.center
        utils.draw_text(cr, text, position)

    return component_module.Component(
        circuit, num_inputs=1, num_outputs=0, on_draw=on_draw)
