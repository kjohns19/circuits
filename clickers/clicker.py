class Clicker:
    def on_click(self, app, event, button, position, component):
        print('Click event={} button={} position={} component={}'.format(
            event, button, position, component))

    def on_move(self, app, event, position):
        pass

    def draw(self, app, cr, mouse_pos):
        pass
