import collections.abc as abc
import typing as t

VecOrTup = t.Union['Vector2', tuple[float, float], list[float]]


class Vector2:
    def __init__(self, xy: VecOrTup) -> None:
        self._x, self._y = xy

    @property
    def x(self) -> float:
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        self._x = value

    @property
    def y(self) -> float:
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        self._y = value

    def set(self, xy: VecOrTup) -> None:
        self._x, self._y = xy

    def __iter__(self) -> abc.Generator[float, None, None]:
        yield self._x
        yield self._y

    def __neg__(self) -> 'Vector2':
        return Vector2((-self._x, -self._y))

    def __add__(self, vec: VecOrTup) -> 'Vector2':
        x, y = vec
        return Vector2((self._x+x, self._y+y))

    def __sub__(self, vec: VecOrTup) -> 'Vector2':
        x, y = vec
        return Vector2((self._x-x, self._y-y))

    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2((self._x*scalar, self._y*scalar))

    def __truediv__(self, scalar: float) -> 'Vector2':
        return Vector2((self._x/scalar, self._y/scalar))


class Rectangle:
    def __init__(self, size: t.Optional[VecOrTup] = None,
                 position: t.Optional[VecOrTup] = None):
        self._size = Vector2(size or (0, 0))
        self._position = Vector2(position or (0, 0))

    @property
    def size(self) -> Vector2:
        return self._size

    @size.setter
    def size(self, value: VecOrTup) -> None:
        self._size = Vector2(value)

    @property
    def width(self) -> float:
        return self._size.x

    @width.setter
    def width(self, value: float) -> None:
        self._size.x = value

    @property
    def height(self) -> float:
        return self._size.y

    @height.setter
    def height(self, value: float) -> None:
        self._size.y = value

    @property
    def left(self) -> float:
        return self._position.x

    @property
    def right(self) -> float:
        return self._position.x + self._size.x

    @property
    def top(self) -> float:
        return self._position.y

    @property
    def bottom(self) -> float:
        return self._position.y + self._size.y

    @property
    def position(self) -> Vector2:
        return self._position

    @position.setter
    def position(self, value: VecOrTup) -> None:
        self._position = Vector2(value)

    @property
    def center(self) -> Vector2:
        return self._position + self._size/2

    @center.setter
    def center(self, value: VecOrTup) -> None:
        self._position = Vector2(value) - self._size/2

    @property
    def top_left(self) -> Vector2:
        return self._position

    @property
    def top_right(self) -> Vector2:
        return self._position + (self._size.x, 0)

    @property
    def bottom_left(self) -> Vector2:
        return self._position + (0, self._size.y)

    @property
    def bottom_right(self) -> Vector2:
        return self._position + self._size

    def contains_point(self, point: VecOrTup) -> bool:
        point = Vector2(point)
        xmin = self._position.x
        xmax = self._position.x + self._size.x

        ymin = self._position.y
        ymax = self._position.y + self._size.y
        return xmin < point.x < xmax and ymin < point.y < ymax

    def contains_rectangle(self, rectangle: 'Rectangle') -> bool:
        return all((
            self.left < rectangle.left,
            self.right > rectangle.right,
            self.top < rectangle.top,
            self.bottom > rectangle.bottom
        ))
