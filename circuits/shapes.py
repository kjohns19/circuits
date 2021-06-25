class Vector2:
    def __init__(self, xy):
        self._x, self._y = xy

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    def set(self, xy):
        self._x, self._y = xy

    def __iter__(self):
        yield self._x
        yield self._y

    def __add__(self, vec):
        x, y = vec
        return Vector2((self._x+x, self._y+y))

    def __sub__(self, vec):
        x, y = vec
        return Vector2((self._x-x, self._y-y))

    def __mul__(self, scalar):
        return Vector2((self._x*scalar, self._y*scalar))

    def __truediv__(self, scalar):
        return Vector2((self._x/scalar, self._y/scalar))


class Rectangle:
    def __init__(self, size=None, position=None):
        self._size = Vector2(size or (0, 0))
        self._position = Vector2(position or (0, 0))

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = Vector2(value)

    @property
    def width(self):
        return self._size.x

    @width.setter
    def width(self, value):
        self._size.x = value

    @property
    def height(self):
        return self._size.y

    @height.setter
    def height(self, value):
        self._size.y = value

    @property
    def left(self):
        return self._position.x

    @property
    def right(self):
        return self._position.x + self._size.x

    @property
    def top(self):
        return self._position.y

    @property
    def bottom(self):
        return self._position.y + self._size.y

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = Vector2(value)

    @property
    def center(self):
        return self._position + self._size/2

    @center.setter
    def center(self, value):
        self._position = value - self._size/2

    @property
    def top_left(self):
        return self._position

    @property
    def top_right(self):
        return self._position + (self._size.x, 0)

    @property
    def bottom_left(self):
        return self._position + (0, self._size.y)

    @property
    def bottom_right(self):
        return self._position + self._size

    def contains_point(self, point):
        point = Vector2(point)
        xmin = self._position.x
        xmax = self._position.x + self._size.x

        ymin = self._position.y
        ymax = self._position.y + self._size.y
        return xmin < point.x < xmax and ymin < point.y < ymax

    def contains_rectangle(self, rectangle):
        return all((
            self.left < rectangle.left,
            self.right > rectangle.right,
            self.top < rectangle.top,
            self.bottom > rectangle.bottom
        ))
