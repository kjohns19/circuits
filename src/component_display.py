import shapes
import utils

import collections
import math


WIDTH = 80

OUTLINE_WIDTH = 1

NODE_SEPARATION = 20
NODE_RADIUS = 4

BLACK = (0, 0, 0)
GRAY  = (0.8, 0.8, 0.8)
WHITE = (1, 1, 1)
RED   = (1, 0, 0)
GREEN = (0, 1, 0)
BLUE  = (0, 0, 1)


class ComponentDisplay:
    def __init__(self, component):
        self._component = component
        self._rect = None
        self.recalculate_size()
        self._outline_color = BLACK
        self._fill_color = WHITE

    @property
    def position(self):
        return self._rect.position

    @position.setter
    def position(self, value):
        self._rect.position = value

    @property
    def center(self):
        return self._rect.center

    @center.setter
    def center(self, value):
        self._rect.center = value

    @property
    def bounds(self):
        return self._rect

    @property
    def outline_color(self):
        return self._outline_color

    @outline_color.setter
    def outline_color(self, color):
        self._outline_color = color

    @property
    def fill_color(self):
        return self._fill_color

    @fill_color.setter
    def fill_color(self, color):
        self._fill_color = color

    def get_save_data(self):
        return collections.OrderedDict((
            ('position', list(self.position)),
            ('outline_color', self.outline_color),
            ('fill_color', self.fill_color)
        ))

    def load(self, data):
        self.position = data['position']
        self.outline_color = data['outline_color']
        self.fill_color = data['fill_color']

    def contains(self, point):
        return self._rect.contains(point)

    def recalculate_size(self):
        max_nodes = max(
            self._component.num_inputs,
            self._component.num_outputs)
        height = NODE_SEPARATION * max_nodes  # + NODE_SEPARATION//2
        pos = (0, 0) if self._rect is None else self._rect.position
        self._rect = shapes.Rectangle(size=(WIDTH, height), position=pos)

    def node_pos(self, input, idx):
        offset = WIDTH/2 * (-1 if input else 1)
        center = self._rect.center + (offset, 0)
        max_nodes = max(
            self._component.num_inputs,
            self._component.num_outputs)
        start_y = center.y - (max_nodes-1)*NODE_SEPARATION//2
        return shapes.Vector2((center.x, start_y + NODE_SEPARATION*idx))

    def draw(self, app, cr):
        cr.rectangle(*self._rect.top_left, *self._rect.size)

        cr.set_source_rgb(*self._fill_color)
        cr.fill_preserve()

        cr.set_source_rgb(*self._outline_color)
        cr.set_line_width(2)
        cr.stroke()

        for i, node in enumerate(self._component.inputs):
            position = self.node_pos(True, i)
            connected = node.is_connected()
            fill_color = _node_color(node.new_value, connected)
            _draw_node(cr, position, fill_color)
            utils.draw_text(
                cr, node.label, position + (NODE_RADIUS+1, 0), size=10,
                h_align=utils.TextHAlign.LEFT)

        for i, node in enumerate(self._component.outputs):
            position = self.node_pos(False, i)
            connected = node.is_connected()
            fill_color = _node_color(node.value, connected)
            _draw_node(cr, position, fill_color)
            utils.draw_text(
                cr, node.label, position - (NODE_RADIUS+1, 0), size=10,
                h_align=utils.TextHAlign.RIGHT)

        name = self._component.name
        if name:
            position = self.center - (0, self._rect.height/2+8)
            utils.draw_text(cr, name, position, bold=True)

        self._component.on_draw(app, cr)

    def draw_input_wires(self, app, cr):
        inputs = self._component.inputs

        for input_idx, input in enumerate(inputs):
            output = input.connected_output
            if output is None:
                continue

            component = output.component
            output_idx = output.index

            input_pos = self.node_pos(True, input_idx)
            output_pos = component.display.node_pos(False, output_idx)
            positions = [input_pos] + input.wire_positions + [output_pos]

            color = _wire_color(input.new_value)
            utils.draw_lines(cr, positions, color)


def _wire_color(value):
    if isinstance(value, bool):
        return GREEN if value else RED
    else:
        return BLACK


def _node_color(value, connected):
    if isinstance(value, bool):
        return GREEN if value else RED
    else:
        return BLACK if connected else WHITE


def _draw_node(cr, position, fill_color):
    cr.new_path()
    cr.arc(*position, NODE_RADIUS, 0, math.pi*2)

    cr.set_source_rgb(*fill_color)
    cr.fill_preserve()

    cr.set_source_rgb(*BLACK)
    cr.set_line_width(2)
    cr.stroke()
