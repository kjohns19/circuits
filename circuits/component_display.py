import typing as t

import cairo

from . import shapes
from . import draw

if t.TYPE_CHECKING:
    from . import application
    from . import component as component_mod


WIDTH = 80

OUTLINE_WIDTH = 1

NODE_SEPARATION = 20
NODE_RADIUS = 4


class ComponentDisplay:
    def __init__(self, component: 'component_mod.Component') -> None:
        self._component = component
        self._rect = shapes.Rectangle((0, 0), (0, 0))
        self._custom_width: t.Optional[float] = None
        self._custom_height: t.Optional[float] = None
        self.recalculate_size()
        self._outline_color = draw.COLOR_BLACK
        self._fill_color = draw.COLOR_WHITE
        self._debug = False

    @property
    def position(self) -> shapes.Vector2:
        return self._rect.position

    @position.setter
    def position(self, value: shapes.Vector2) -> None:
        amount = value - self._rect.position
        self._rect.position = value
        for input in self._component.inputs:
            input.move(amount)

    @property
    def center(self) -> shapes.Vector2:
        return self._rect.center

    @center.setter
    def center(self, value: shapes.Vector2) -> None:
        self._rect.center = value

    @property
    def rect(self) -> shapes.Rectangle:
        return self._rect

    @property
    def width(self) -> float:
        return self._rect.width

    @width.setter
    def width(self, value: float) -> None:
        self._rect.width = value
        self._custom_width = value

    @property
    def height(self) -> float:
        return self._rect.height

    @height.setter
    def height(self, value: float) -> None:
        self._rect.height = value
        self._custom_height = value

    @property
    def bounds(self) -> shapes.Rectangle:
        return self._rect

    @property
    def outline_color(self) -> draw.Color:
        return self._outline_color

    @outline_color.setter
    def outline_color(self, color: draw.Color) -> None:
        self._outline_color = color

    @property
    def fill_color(self) -> draw.Color:
        return self._fill_color

    @fill_color.setter
    def fill_color(self, color: draw.Color) -> None:
        self._fill_color = color

    @property
    def debug(self) -> bool:
        return self._debug

    @debug.setter
    def debug(self, value: bool) -> None:
        self._debug = value

    def get_save_data(self) -> dict[str, t.Any]:
        return {
            'position': list(self.position),
            'outline_color': self.outline_color,
            'fill_color': self.fill_color
        }

    def load(self, data: dict[str, t.Any]) -> None:
        def get_color(field: list[float]) -> draw.Color:
            return (field[0], field[1], field[2])
        self.position = shapes.Vector2(data['position'])
        self.outline_color = get_color(data['outline_color'])
        self.fill_color = get_color(data['fill_color'])

    def contains_point(self, point: shapes.VecOrTup) -> bool:
        return self._rect.contains_point(point)

    def recalculate_size(self) -> None:
        max_nodes = max(
            self._component.num_inputs,
            self._component.num_outputs)
        width = self._custom_width or WIDTH
        height = self._custom_height or (NODE_SEPARATION * max_nodes)
        pos = (0, 0) if self._rect is None else self._rect.position
        self._rect = shapes.Rectangle(size=(width, height), position=pos)

    def node_pos(self, input: bool, idx: int) -> shapes.Vector2:
        start = self._rect.top_left if input else self._rect.top_right
        return start + (0, NODE_SEPARATION//2) + (0, NODE_SEPARATION*idx)

    def draw(self, app: 'application.Application', cr: cairo.Context) -> None:
        draw.rectangle(
            cr, self._rect, self._fill_color, self._outline_color)

        node_data: list[
            tuple[t.Union[list['component_mod.Input'], list['component_mod.Output']],
                  bool, tuple[float, float], draw.TextHAlign]] = [
            # Nodes, input, offset, text align
            (self._component.inputs, True,
             (NODE_RADIUS+2.0, 0.0), draw.TextHAlign.LEFT),
            (self._component.outputs, False,
             (-NODE_RADIUS-2.0, 0.0), draw.TextHAlign.RIGHT),
        ]

        for nodes, is_input, offset, text_align in node_data:
            for i, node in enumerate(nodes):
                node = t.cast(t.Union['component_mod.Input', 'component_mod.Output'],
                              node)
                position = self.node_pos(is_input, i)
                connected = node.is_connected()
                fill_color = _node_color(node.value, connected)
                draw.circle(cr, position, NODE_RADIUS, fill_color, draw.COLOR_BLACK)
                draw.text(
                    cr, node.label, position + offset, size=10,
                    bold=True, h_align=text_align)

        name = self._component.name
        if name:
            position = self.center - (0, self._rect.height/2+8)
            draw.text(cr, name, position, bold=True)

        self._component.on_draw(app, cr)

    def draw_input_wires(self, app: 'application.Application',
                         cr: cairo.Context, debugging: bool = False) -> None:
        inputs = self._component.inputs

        for input_idx, input in enumerate(inputs):
            output = input.connected_output
            if output is None:
                continue

            component = output.component
            output_idx = output.index

            if debugging and not self._debug and not component.display.debug:
                continue

            input_pos = self.node_pos(True, input_idx)
            output_pos = component.display.node_pos(False, output_idx)
            positions = [input_pos] + input.wire_positions + [output_pos]

            color = _wire_color(input.new_value, debugging)
            draw.lines(cr, positions, color, thickness=4 if debugging else 2)
            for pos in input.wire_positions:
                draw.circle(cr, pos, 2, color, color)

    def draw_debug_values(self, app: 'application.Application',
                          cr: cairo.Context) -> None:
        if not self._debug:
            return

        color = draw.COLOR_GRAY

        for i, in_node in enumerate(self._component.inputs):
            position = self.node_pos(True, i)
            draw.text(
                cr, str(in_node.value), position - (NODE_RADIUS+1, 0), size=10,
                h_align=draw.TextHAlign.RIGHT,
                bold=True, background_color=color)

        for i, out_node in enumerate(self._component.outputs):
            position = self.node_pos(False, i)
            draw.text(
                cr, str(out_node.value), position + (NODE_RADIUS+1, 0), size=10,
                h_align=draw.TextHAlign.LEFT,
                bold=True, background_color=color)


def _wire_color(value: t.Any, debug: bool = False) -> draw.Color:
    if debug:
        if isinstance(value, bool):
            return draw.COLOR_MAGENTA if value else draw.COLOR_CYAN
        else:
            return draw.COLOR_BLUE
    else:
        if isinstance(value, bool):
            return draw.COLOR_GREEN if value else draw.COLOR_RED
        else:
            return draw.COLOR_BLACK


def _node_color(value: t.Any, connected: bool) -> draw.Color:
    if isinstance(value, bool):
        return draw.COLOR_GREEN if value else draw.COLOR_RED
    else:
        return draw.COLOR_BLACK if connected else draw.COLOR_WHITE
