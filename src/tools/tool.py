import utils


class Tool:
    def on_click(self, app, event, button, position, component):
        {
            utils.MouseButton.LEFT: self.on_left_click,
            utils.MouseButton.RELEASE_LEFT: self.on_left_release,
            utils.MouseButton.MIDDLE: self.on_middle_click,
            utils.MouseButton.RELEASE_MIDDLE: self.on_middle_release,
            utils.MouseButton.RIGHT: self.on_right_click,
            utils.MouseButton.RELEASE_RIGHT: self.on_right_release,
        }[button](app, event, position, component)

    def on_left_click(self, app, event, position, component):
        pass

    def on_left_release(self, app, event, position, component):
        pass

    def on_right_click(self, app, event, position, component):
        pass

    def on_right_release(self, app, event, position, component):
        pass

    def on_middle_click(self, app, event, position, component):
        pass

    def on_middle_release(self, app, event, position, component):
        pass

    def on_move(self, app, event, position):
        pass

    def draw(self, app, cr, mouse_pos):
        pass

    def reset(self, app):
        pass
