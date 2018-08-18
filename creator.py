import circuit


_CIRCUIT = circuit.Circuit()


class Creator:
    def __init__(self, creator_func):
        self._creator_func = creator_func
        self._base_component = creator_func(_CIRCUIT)
        self._properties = []

    def add_property(self, property):
        self._properties.append(property)

    def get_property_widgets(self, component=None, callback=None):
        if component is None:
            component = self._base_component
        return [
            property.create_widget(component, callback)
            for property in self._properties
        ]

    def __call__(self, circuit):
        component = self._creator_func(circuit)
        for property in self._properties:
            property.apply(self._base_component, component)
        component.creator = self
        return component
