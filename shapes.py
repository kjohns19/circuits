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
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = Vector2(value)

    @property
    def top_left(self):
        return self._position - self._size/2

    @property
    def top_right(self):
        return self._position + (self._size.x/2, -self._size.y/2)

    @property
    def bottom_left(self):
        return self._position + (-self._size.x/2, self._size.y/2)

    @property
    def bottom_right(self):
        return self._position + self._size/2

    def contains(self, point):
        point = Vector2(point)
        xmin = self._position.x - self._size.x/2
        xmax = self._position.x + self._size.x/2

        ymin = self._position.y - self._size.y/2
        ymax = self._position.y + self._size.y/2
        return xmin < point.x < xmax and ymin < point.y < ymax
