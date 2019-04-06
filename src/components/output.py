import component as component_module
from component_registry import registry
import utils


CATEGORY = 'Output'


@registry.register('Display', CATEGORY)
def display(circuit):
    def on_draw(component, app, cr):
        text = str(component.inputs[0].value)
        position = component.display.center
        utils.draw_text(cr, text, position)

    return component_module.Component(
        circuit, num_inputs=1, num_outputs=0, on_draw=on_draw)


@registry.register('Console', CATEGORY)
def console(circuit):
    def on_draw(component, app, cr):
        text = component.data['text']
        position = component.display.center
        utils.draw_text(cr, text, position, v_align=utils.TextVAlign.BOTTOM)

    def on_update(component):
        if component.inputs[2].value:
            component.data['text'] = ''
        elif component.inputs[0].value and not component.inputs[0].old_value:
            component.data['text'] += str(component.inputs[1].value)

    component = component_module.Component(
        circuit, num_inputs=3, num_outputs=0,
        on_draw=on_draw, on_update=on_update,
        input_labels=['clk', 'value', 'clear'])
    component.data['text'] = ''
    return component
