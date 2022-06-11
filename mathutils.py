# Made by Reuben Unicruz

from math import *

# Class Declarations...
class Vector:pass
class Polar:pass


# A 2D vector
class Vector:

    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y

    # Create the Vector attribute 'magnitude'
    # and have it update whenever x, y, or
    # itself is modified.
    @property
    def magnitude(self)->float:
        return sqrt( pow(self.x, 2) + pow(self.y, 2) )

    @magnitude.setter
    def magnitude(self, val:float):
        nx = self.x / self.magnitude
        ny = self.y / self.magnitude

        self.x = nx * val
        self.y = ny * val

    # Make this Vector class summable
    # with other Vector classes.
    def __add__(self, other)->Vector:
        return Vector(self.x+other.x, self.y+other.y)

    def __radd__(self, other)->Vector:
        if (other == 0):
            return self
        else:
            return self.__add__(other)

    # Make this Vector class subtractable
    def __sub__(self, other)->Vector:
        return Vector(self.x - other.x, self.y - other.y)

    def __rsub__(self, other)->Vector:
        if (other == 0):
            return self
        else:
            return self.__sub__(other)

    # Make this Vector class be able
    # to be inverted (unary negative sign).
    def __neg__(self)->Vector:
        return Vector(-self.x, -self.y)

    # Make this class be able to be
    # multiplied with either a scalar
    # or another vector.
    def __mul__(self, other):
        if (type(other) == int or type(other) == float):
            return Vector(self.x * other, self.y * other)
        
        return self.Dot(self, other)

    def __rmul__(self, other):
        if (other == 0):
            return self

        return self.__mul__(other)

    # Return a normalized (magnitude = 1) vector
    # of itself.
    def Normalized(self)->Vector:
        return Vector(self.x/self.magnitude, self.y/self.magnitude)

    # Convert this vector into a polar vector.
    def toPolar(self)->Polar:
        return Polar(self.magnitude, atan2(self.y, self.x))

    # Multiply two vectors.
    # This returns a dot product of two vectors (scalar result).
    def Dot(self, vectorA:Vector, vectorB:Vector)->float:
        return (vectorA.x * vectorB.x) + (vectorA.y * vectorB.y)


# A 2D polar vector. Inherits from Vector class.
class Polar(Vector):
    def __init__(self, magnitude:float, angle:float):
        super().__init__(
            x = round(magnitude * cos(angle), 4),
            y = round(magnitude * sin(angle), 4)
        )

    # Make the Polar attribute 'angle'
    # and update it whenever the x, y, or itself
    # is modified.
    @property
    def angle(self)->float:
        return atan2(self.y, self.x)

    @angle.setter
    def angle(self, val):
        mag = self.magnitude

        self.x = round(mag * cos(val), 4)
        self.y = round(mag * sin(val), 4)

    # Make this Polar class summable
    # with other Polar classes.
    def __add__(self, other)->Polar:
        rv = Vector(self.x + other.x, self.y + other.y)

        return rv.toPolar()

    def __radd__(self, other)->Polar:
        if (other == 0):
            return self
        else:
            return self.__add__(other)

    # Make this Polar class subtractable
    def __sub__(self, other)->Polar:
        rv = Vector(self.x - other.x, self.y - other.y)

        return rv.toPolar()

    def __rsub__(self, other)->Polar:
        if (other == 0):
            return self
        else:
            return self.__sub__(other)

    # Make this Polar class be able
    # to be inverted (unary negative sign).
    def __neg__(self)->Polar:
        rv = Vector(-self.x, -self.y)

        return rv.toPolar()

    # Make this class be able to be
    # multiplied with either a scalar
    # or another polar vector.
    def __mul__(self, other):
        if (type(other) == int or type(other) == float):
            return Vector(self.x * other, self.y * other).toPolar()
        
        return self.Dot(self, other)

    def __rmul__(self, other):
        if (other == 0):
            return self

        return self.__mul__(other)


    # Return a normalized (magnitude = 1) polar vector
    # of itself.
    def Normalized(self)->Polar:
        return Vector(self.x/self.magnitude, self.y/self.magnitude).toPolar()


# Clamp value between a minimum and
# a maximum.
def clamp(value:float, minValue:float, maxValue:float)->float:
    return min(maxValue, max(minValue, value))

# Make an input value that ranges from "fromMin" to "fromMax"
# map directly to a new range that goes from "toMin" to "toMax".
def mapInputToRange(inputVal:float, fromMin:float, fromMax:float, toMin:float, toMax:float)->float:
    return (inputVal-fromMin)/(fromMax-fromMin)*(toMax-toMin)+toMin

# Linear Interpolation function where a is the start value,
# b is the goal, and t is the interpolation step.
def lerp(a:float, b:float, t:float):
    return a + (b-a)*t
