import component as component_module
from component_registry import registry
import shapes
import utils

import itertools
import textwrap


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
    max_width = 20
    max_height = 7

    def on_draw(component, app, cr):
        lines = list(itertools.chain.from_iterable(
            textwrap.wrap(line, width=max_width, tabsize=4)
            for line in component.data['text'].split('\n')
        ))
        if lines and not lines[-1]:
            lines.pop()
        lines = lines[-max_height:]
        grid_size = app.grid_size
        position = (
            component.display.rect.bottom_left +
            (grid_size//2, -grid_size//2)
        )
        rect = shapes.Rectangle(
            position=position-(4, 12*max_height),
            size=(max_width*7+8, max_height*12+4))
        utils.draw_rectangle(cr, rect, (0.9, 0.9, 0.9), (0, 0, 0))
        for i, line in enumerate(reversed(lines)):
            pos = position - (0, i*12)
            utils.draw_text(
                cr, line, pos,
                h_align=utils.TextHAlign.LEFT,
                v_align=utils.TextVAlign.BOTTOM)

    def on_update(component):
        if component.inputs[2].value:
            component.data['text'] = ''
        elif component.inputs[0].value and not component.inputs[0].old_value:
            component.data['text'] += str(component.inputs[1].value)

    component = component_module.Component(
        circuit, num_inputs=3, num_outputs=0,
        on_draw=on_draw, on_update=on_update,
        input_labels=['clk', 'value', 'clear'])
    component.display.width = 160
    component.display.height = 160
    component.data['text'] = ''
    return component
