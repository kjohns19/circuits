class Clicker:
    def on_click(self, app, button, position, component):
        print('Click button={} position={} component={}'.format(
            button, position, component))
