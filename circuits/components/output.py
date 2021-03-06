import itertools
import textwrap
import typing as t

import cairo

from .. import circuit as circuit_mod
from .. import component as component_mod
from .. import draw
from ..component_registry import registry
from .. import shapes

if t.TYPE_CHECKING:
    from .. import application


CATEGORY = 'Output'


@registry.register('Display', CATEGORY)
def display(circuit: circuit_mod.Circuit) -> component_mod.Component:
    def on_draw(component: component_mod.Component, app: 'application.Application',
                cr: cairo.Context) -> None:
        text = str(component.inputs[0].value)
        position = component.display.center
        draw.text(cr, text, position)

    return component_mod.Component(
        circuit, num_inputs=1, num_outputs=0, on_draw=on_draw)


@registry.register('Console', CATEGORY)
def console(circuit: circuit_mod.Circuit) -> component_mod.Component:
    max_width = 20
    max_height = 7

    def on_draw(component: component_mod.Component, app: 'application.Application',
                cr: cairo.Context) -> None:
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
        draw.rectangle(cr, rect, draw.Color((0.9, 0.9, 0.9)), draw.COLOR_BLACK)
        for i, line in enumerate(reversed(lines)):
            pos = position - (0, i*12)
            draw.text(
                cr, line, pos,
                h_align=draw.TextHAlign.LEFT,
                v_align=draw.TextVAlign.BOTTOM)

    def on_update(component: component_mod.Component) -> None:
        if component.inputs[2].value:
            component.data['text'] = ''
        elif component.inputs[0].value and not component.inputs[0].old_value:
            component.data['text'] += str(component.inputs[1].value)

    component = component_mod.Component(
        circuit, num_inputs=3, num_outputs=0,
        on_draw=on_draw, on_update=on_update,
        input_labels=['clk', 'value', 'clear'])
    component.display.width = 160
    component.display.height = 160
    component.data['text'] = ''
    return component
