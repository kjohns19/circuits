import shapes
import utils

import math


WIDTH = 72

OUTLINE_WIDTH = 1

NODE_SEPARATION = 24
NODE_RADIUS = 8

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

    def contains(self, point):
        return self._rect.contains(point)

    def recalculate_size(self):
        max_nodes = max(
            self._component.num_inputs,
            self._component.num_outputs)
        height = NODE_SEPARATION * max_nodes + NODE_SEPARATION//2
        pos = (0, 0) if self._rect is None else self._rect.position
        self._rect = shapes.Rectangle(size=(WIDTH, height), position=pos)

    def node_pos(self, input, idx):
        offset = WIDTH/2 * (-1 if input else 1)
        center = self._rect.position + (offset, 0)
        count = len(
            self._component.inputs if input else self._component.outputs)
        start_y = center.y - (count-1)*NODE_SEPARATION//2
        return (center.x, start_y + NODE_SEPARATION*idx)

    def draw(self, app, cr):
        cr.rectangle(*self._rect.top_left, *self._rect.size)

        cr.set_source_rgb(*self._fill_color)
        cr.fill_preserve()

        cr.set_source_rgb(*self._outline_color)
        cr.set_line_width(2)
        cr.stroke()

        def draw_nodes(input, count):
            for i in range(count):
                position = self.node_pos(input, i)
                cr.arc(*position, NODE_RADIUS, 0, math.pi*2)
                cr.set_source_rgb(*WHITE)
                cr.fill_preserve()

                cr.set_source_rgb(*BLACK)
                cr.set_line_width(2)
                cr.stroke()

        draw_nodes(True, len(self._component.inputs))
        draw_nodes(False, len(self._component.outputs))

        name = self._component.name
        if name:
            position = self.position - (0, self._rect.height/2-8)
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

            color = GREEN if input.new_value else RED
            utils.draw_line(cr, input_pos, output_pos, color)
