class Clicker:
    def on_click(self, app, event, position, component):
        print('Click event={} position={} component={}'.format(
            event, position, component))
