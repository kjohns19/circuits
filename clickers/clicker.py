class Clicker:
    def on_click(self, app, event, button, position, component):
        print('Click event={} button={} position={} component={}'.format(
            event, button, position, component))

    def draw(self, app, cr, mouse_pos):
        pass
