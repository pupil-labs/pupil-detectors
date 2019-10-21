import typing as T


class Roi:
    def __init__(self, x_min: int, y_min: int, x_max: int, y_max: int):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    @property
    def width(self) -> int:
        return self.x_max - self.x_min

    @property
    def height(self) -> int:
        return self.y_max - self.y_min

    @property
    def slices(self) -> T.Tuple[slice, slice]:
        return slice(self.y_min, self.y_max + 1), slice(self.x_min, self.x_max + 1)

    @property
    def rect(self) -> T.Tuple[int, int, int, int]:
        return self.x_min, self.x_max, self.width, self.height

    @staticmethod
    def from_slices(x_slice: slice, y_slice: slice) -> "Roi":
        return Roi(
            x_min=x_slice.start,
            y_min=y_slice.start,
            x_max=x_slice.stop - 1,
            y_max=y_slice.stop - 1,
        )

    @staticmethod
    def from_rect(x: int, y: int, width: int, height: int) -> "Roi":
        return Roi(x_min=x, y_min=y, x_max=x + width - 1, y_max=y + height - 1)

    @staticmethod
    def from_shape(shape: T.Tuple[int, int]) -> "Roi":
        return Roi.from_rect(x=0, y=0, width=shape[1], height=shape[0])

