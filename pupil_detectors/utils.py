class Roi(object):
    """this is a simple 2D Region of Interest class
    it is applied on numpy arrays for convenient slicing
    like this:

    roi_array_slice = full_array[r.view]
    # do something with roi_array_slice

    this creates a view, no data copying done
    """

    def __init__(self, array_shape):
        self.array_shape = array_shape
        self.lX = 0
        self.lY = 0
        self.uX = array_shape[1]
        self.uY = array_shape[0]
        self.nX = 0
        self.nY = 0

    @property
    def view(self):
        return slice(self.lY, self.uY), slice(self.lX, self.uX)

    @view.setter
    def view(self, value):
        raise Exception("The view field is read-only. Use the set methods instead")

    def add_vector(self, vector):
        """
        adds the roi offset to a len2 vector
        """
        x, y = vector
        return (self.lX + x, self.lY + y)

    def sub_vector(self, vector):
        """
        subs the roi offset to a len2 vector
        """
        x, y = vector
        return (x - self.lX, y - self.lY)

    def set(self, vals):
        if vals is not None and len(vals) is 5:
            self.lX, self.lY, self.uX, self.uY, self.array_shape = vals
        elif vals is not None and len(vals) is 4:
            self.lX, self.lY, self.uX, self.uY = vals

    def get(self):
        return self.lX, self.lY, self.uX, self.uY, self.array_shape


def normalize(pos, size, flip_y=False):
    """
    normalize return as float
    """
    width, height = size
    x = pos[0]
    y = pos[1]
    x /= float(width)
    y /= float(height)
    if flip_y:
        return x, 1 - y
    return x, y

