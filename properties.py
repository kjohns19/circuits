import property_widgets


class Property:
    def __init__(self, getter, setter):
        self._getter = getter
        self._setter = setter

    @property
    def getter(self):
        return self._getter

    @property
    def setter(self):
        return self._setter

    def apply(self, from_component, to_component):
        self.setter(to_component, self.getter(from_component))


class ListProperty(Property):
    def __init__(self, getter, setter, max_values=10, title='Values'):
        super().__init__(getter, setter)
        self._max_values = max_values
        self._title = title

    def create_widget(self, component, callback=None):
        def real_callback(values):
            self.setter(component, values)
            if callback:
                callback(self, component, values)

        return property_widgets.create_value_list_widget(
            title=self._title,
            callback=real_callback,
            max_values=self._max_values,
            initial_values=self.getter(component))
