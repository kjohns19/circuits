import shapes
import utils

import math


WIDTH = 72

OUTLINE_WIDTH = 1

NODE_SEPARATION = 24
NODE_RADIUS = 8

BLACK = (0, 0, 0)
WHITE = (1, 1, 1)
RED   = (1, 0, 0)
GREEN = (0, 1, 0)


class ComponentDisplay:
    def __init__(self, component):
        self._component = component
        self.recalculate_size()

    @property
    def position(self):
        return self._rect.position

    @property
    def bounds(self):
        return self._rect

    @position.setter
    def position(self, value):
        self._rect.position = value

    def contains(self, point):
        return self._rect.contains(point)

    def recalculate_size(self):
        max_nodes = max(
            self._component.num_inputs,
            self._component.num_outputs)
        height = NODE_SEPARATION * max_nodes + NODE_SEPARATION//2
        self._rect = shapes.Rectangle(size=(WIDTH, height))

    def _node_pos(self, input, idx):
        offset = WIDTH/2 * (-1 if input else 1)
        center = self._rect.position + (offset, 0)
        count = len(
            self._component.inputs if input else self._component.outputs)
        start_y = center.y - (count-1)*NODE_SEPARATION//2
        return (center.x, start_y + NODE_SEPARATION*idx)

    def draw(self, window, cr):
        cr.rectangle(*self._rect.top_left, *self._rect.size)

        cr.set_source_rgb(*WHITE)
        cr.fill_preserve()

        cr.set_source_rgb(*BLACK)
        cr.set_line_width(2)
        cr.stroke()

        def draw_nodes(input, count):
            for i in range(count):
                position = self._node_pos(input, i)
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

        self._component.on_draw(window, cr)

    def draw_input_wires(self, window, cr):
        inputs = self._component.inputs

        for input_idx, input in enumerate(inputs):
            output = input.connected_output
            if output is None:
                continue

            component = output.component
            output_idx = output.index

            input_pos = self._node_pos(True, input_idx)
            output_pos = component.display._node_pos(False, output_idx)

            color = GREEN if input.new_value else RED

            cr.set_source_rgb(*color)
            cr.move_to(*input_pos)
            cr.line_to(*output_pos)
            cr.set_line_width(2)
            cr.stroke()
